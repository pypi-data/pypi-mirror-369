from __future__ import annotations

"""Asynchronous streaming pipeline for audio frames.

The pipeline links ``SignalStream`` reading, ``AudioEncoder`` processing,
``TensorMapper`` accumulation and optional gating modules using
``asyncio.Queue`` objects.  Frames can be fed externally (e.g. from a
microphone) or pulled from a :class:`~hlsf_module.signal_io.SignalStream`.
"""

import asyncio
import logging
from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, List, Optional, Tuple

from .agency_gates import decide as gate
from .enc_audio import AudioEncoder
from .signal_io import SignalStream
from .tensor_mapper import TensorMapper, HLSFState
from .symbols.schema import SymbolToken

logger = logging.getLogger(__name__)

Scores = Dict[int, float]
Triangles = Iterable[Iterable[Iterable[float]]]


@dataclass
class StreamPipeline:
    """Asynchronous audio processing pipeline.

    Parameters
    ----------
    stream:
        Optional :class:`SignalStream` providing frames.  When ``None`` frames
        must be supplied via :meth:`feed_frame`.
    queue_size:
        Maximum number of pending items per internal queue.
    encoder_args:
        Keyword arguments forwarded to :class:`AudioEncoder`.
    """

    stream: Optional[SignalStream] = None
    queue_size: int = 1
    encoder_args: dict = field(default_factory=dict)
    gate_args: dict = field(default_factory=dict)
    mapping_strategy: Optional[str] = None
    use_gpu: bool = False
    device: Optional[str] = None
    latency_window: int = 10
    latency_threshold: float = 0.05
    high_wm_perc: float = 0.8
    low_wm_perc: float = 0.2
    max_queue_size: Optional[int] = None
    metrics_callback: Optional[Callable[[float, float, float], None]] = None
    error_callback: Optional[Callable[[Exception], None]] = None
    num_workers: int = 1

    def __post_init__(self) -> None:
        """Create queues and helper objects after dataclass initialisation."""

        self.frame_q: "asyncio.Queue[Optional[Tuple[float, List[float]]]]" = asyncio.Queue(self.queue_size)
        # ``token_q`` retained for API compatibility; the worker loop bypasses it.
        self.token_q: "asyncio.Queue[Optional[List[SymbolToken]]]" = asyncio.Queue(self.queue_size)
        self.result_q: "asyncio.Queue[Optional[Tuple[Scores, Triangles]]]" = asyncio.Queue(self.queue_size)
        self._encoder = AudioEncoder(**self.encoder_args, use_gpu=self.use_gpu, device=self.device)
        self._mapper = TensorMapper(
            use_gpu=self.use_gpu,
            device=self.device,
            mapping_strategy=self.mapping_strategy,
        )
        self._tasks: List[asyncio.Task[None]] = []
        self._closed = False
        self._can_feed = asyncio.Event()
        self._can_feed.set()
        self.high_wm = max(1, int(self.queue_size * self.high_wm_perc))
        self.low_wm = int(self.queue_size * self.low_wm_perc)
        self.max_queue_size = self.max_queue_size or self.queue_size * 4
        self._latency_samples: List[float] = []
        self._latency_window = self.latency_window
        self._latency_threshold = self.latency_threshold
        self._pending_workers = self.num_workers
        self._end_lock = asyncio.Lock()
        self._error: Optional[Exception] = None

    # ------------------------------------------------------------------
    # feeding
    def feed_nowait(self, frame: List[float]) -> bool:
        """Try to enqueue ``frame`` without blocking.

        Returns ``True`` on success, ``False`` when the queue is full or
        feeding is currently paused due to back‑pressure.
        """

        if not self._can_feed.is_set():
            return False
        loop = asyncio.get_running_loop()
        try:
            self.frame_q.put_nowait((loop.time(), frame))
        except asyncio.QueueFull:  # pragma: no cover - depends on timing
            return False
        self._check_watermarks()
        return True

    async def feed_frame(self, frame: List[float]) -> None:
        """Enqueue ``frame`` awaiting when necessary."""

        await self._can_feed.wait()
        await self.frame_q.put((asyncio.get_running_loop().time(), frame))
        self._check_watermarks()

    # ------------------------------------------------------------------
    async def _reader(self) -> None:
        """Read frames from :attr:`stream` and enqueue them."""

        if self.stream is None:
            return
        loop = asyncio.get_running_loop()
        while True:
            await self._can_feed.wait()
            frame = self.stream.read()
            if frame is None:
                break
            await self.frame_q.put((loop.time(), frame))
            self._check_watermarks()
        for _ in range(self.num_workers):
            await self.frame_q.put(None)

    async def _worker_loop(self, encoder: AudioEncoder, mapper: TensorMapper) -> None:
        """Process frames into scores/state pairs."""

        loop = asyncio.get_running_loop()
        while True:
            item = await self.frame_q.get()
            self._check_watermarks()
            if item is None:
                await self.token_q.put(None)
                break
            ts, frame = item
            tokens = self._encoder.step(frame)
            for t in tokens:
                # mark tokens as originating from the audio modality
                t.feat["modality"] = "audio"
            await self.token_q.put(tokens)
            self._adjust_queue_size(loop.time() - ts)

    async def _mapper_loop(self) -> None:
        """Aggregate tokens into geometry and emit scores/state pairs."""

        try:
            while True:
                item = await self.frame_q.get()
                self._check_watermarks()
                if item is None:
                    async with self._end_lock:
                        self._pending_workers -= 1
                        if self._pending_workers == 0:
                            await self.result_q.put(None)
                    break
                ts, frame = item
                tokens = encoder.step(frame)
                mapper.update(tokens)
                gated = [
                    t
                    for t in tokens
                    if gate(
                        {
                            "scores": [t.feat.get("mag", 0.0), 0.0],
                            "duration": self.gate_args.get("sustain", 1),
                            "detectors": self.gate_args.get("detectors", 1),
                            "cross_scores": t.feat.get("cross_scores", []),
                        },
                        **{
                            k: v
                            for k, v in self.gate_args.items()
                            if k not in {"sustain", "detectors"}
                        },
                    )
                ]
                scores = {
                    t.feat.get("band", t.id): t.feat.get("mag", 0.0)
                    for t in gated
                }
                state = mapper.to_hlsf()
                await self.result_q.put((scores, state))
                latency = loop.time() - ts
                self._adjust_queue_size(latency)
                self._record_metrics(len(tokens), latency)
        except asyncio.CancelledError:  # pragma: no cover - cancellation path
            raise
        except Exception as exc:  # pragma: no cover - unexpected errors
            self._report_error(exc)

    # ------------------------------------------------------------------
    async def start(self) -> None:
        """Launch background tasks."""

        if self._tasks:
            return
        if self.stream is not None:
            t = asyncio.create_task(self._reader())
            t.add_done_callback(self._task_err)
            self._tasks.append(t)
        for enc, mapper in zip(self._encoders, self._mappers):
            t = asyncio.create_task(self._worker_loop(enc, mapper))
            t.add_done_callback(self._task_err)
            self._tasks.append(t)

    async def stop(self) -> None:
        """Signal the pipeline to stop and wait for tasks."""

        if self._closed:
            return
        self._closed = True
        for _ in range(self.num_workers):
            await self.frame_q.put(None)
        for t in self._tasks:
            t.cancel()
        await asyncio.gather(*self._tasks, return_exceptions=True)

    async def join(self) -> None:
        """Wait for all tasks to finish."""

        if self._tasks:
            await asyncio.gather(*self._tasks, return_exceptions=True)

    # ------------------------------------------------------------------
    async def __aenter__(self) -> "StreamPipeline":
        """Start the pipeline when entering an ``async with`` block."""

        await self.start()
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        """Stop the pipeline and drain queues when leaving ``async with``."""

        await self.stop()
        for q in (self.frame_q, self.token_q, self.result_q):
            while not q.empty():
                try:
                    q.get_nowait()
                except asyncio.QueueEmpty:  # pragma: no cover - race condition
                    break
        self._tasks.clear()
        if self._error is not None:
            err = self._error
            self._error = None
            if not self.error_callback:
                raise err

    # ------------------------------------------------------------------
    def _check_watermarks(self) -> None:
        """Toggle feeding based on queue watermarks."""

        qsize = self.frame_q.qsize()
        if qsize >= self.high_wm:
            self._can_feed.clear()
        elif qsize <= self.low_wm:
            self._can_feed.set()

    def _adjust_queue_size(self, latency: float) -> None:
        """Expand or shrink queues according to recent processing latency."""

        self._latency_samples.append(latency)
        if len(self._latency_samples) < self._latency_window:
            return
        avg = sum(self._latency_samples) / len(self._latency_samples)
        self._latency_samples.clear()
        if avg > self._latency_threshold and self.frame_q._maxsize < self.max_queue_size:
            self.frame_q._maxsize += 1
        elif avg < self._latency_threshold / 2 and self.frame_q._maxsize > 1:
            self.frame_q._maxsize -= 1
        self.high_wm = max(1, int(self.frame_q._maxsize * 0.8))
        self.low_wm = int(self.frame_q._maxsize * 0.2)


# ---------------------------------------------------------------------------
# unified multi-modal pipeline


@dataclass
class MultiStreamPipeline:
    """Pipeline handling multiple encoders concurrently.

    The ``encoders`` argument maps modality names to encoder instances.  Each
    encoder receives data via :meth:`feed` and produces :class:`SymbolToken`
    objects tagged with the modality name.  Bands are offset per modality to
    avoid collisions.
    """

    encoders: Dict[str, Any]
    queue_size: int = 1
    gate_args: dict = field(default_factory=dict)

    def __post_init__(self) -> None:
        self.token_q: "asyncio.Queue[Optional[List[SymbolToken]]]" = asyncio.Queue(
            self.queue_size
        )
        self.result_q: "asyncio.Queue[Optional[Tuple[Dict[str, Scores], HLSFState]]]" = (
            asyncio.Queue(self.queue_size)
        )
        self._mapper = TensorMapper()
        self._tasks: List[asyncio.Task[None]] = []
        self._closed = False
        self._queues: Dict[str, asyncio.Queue] = {}
        self._offsets: Dict[str, int] = {}
        offset = 0
        for name in self.encoders:
            self._queues[name] = asyncio.Queue(self.queue_size)
            self._offsets[name] = offset
            offset += 10000

    async def feed(self, modality: str, data: Any) -> None:
        """Enqueue ``data`` for the given ``modality``."""

        await self._queues[modality].put(data)

    async def _encoder_loop(self, name: str, enc: Any) -> None:
        offset = self._offsets[name]
        q = self._queues[name]
        while True:
            item = await q.get()
            if item is None:
                await self.token_q.put(None)
                break
            tokens = enc.step(item)
            for t in tokens:
                band = t.feat.get("band", t.id) + offset
                t.feat["band"] = band
                t.feat["modality"] = name
            await self.token_q.put(tokens)

    async def _mapper_loop(self) -> None:
        finished = 0
        while True:
            tokens = await self.token_q.get()
            if tokens is None:
                finished += 1
                if finished == len(self.encoders):
                    await self.result_q.put(None)
                    break
                continue
            self._mapper.update(tokens)
            gated = [
                t
                for t in tokens
                if gate(
                    {
                        "scores": [t.feat.get("mag", 0.0), 0.0],
                        "duration": self.gate_args.get("sustain", 1),
                        "detectors": self.gate_args.get("detectors", 1),
                        "cross_scores": t.feat.get("cross_scores", []),
                    },
                    **{
                        k: v
                        for k, v in self.gate_args.items()
                        if k not in {"sustain", "detectors"}
                    },
                )
            ]
            scores: Dict[str, Scores] = {}
            for t in gated:
                mod = t.feat.get("modality", "unknown")
                scores.setdefault(mod, {})[t.feat.get("band", t.id)] = t.feat.get(
                    "mag", 0.0
                )
            state = self._mapper.to_hlsf()
            await self.result_q.put((scores, state))

    async def start(self) -> None:
        if self._tasks:
            return
        for name, enc in self.encoders.items():
            self._tasks.append(asyncio.create_task(self._encoder_loop(name, enc)))
        self._tasks.append(asyncio.create_task(self._mapper_loop()))

    async def stop(self) -> None:
        if self._closed:
            return
        self._closed = True
        for q in self._queues.values():
            await q.put(None)
        for t in self._tasks:
            t.cancel()
        await asyncio.gather(*self._tasks, return_exceptions=True)

    async def join(self) -> None:
        if self._tasks:
            await asyncio.gather(*self._tasks, return_exceptions=True)

    async def __aenter__(self) -> "MultiStreamPipeline":
        await self.start()
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        await self.stop()
        for q in [*self._queues.values(), self.token_q, self.result_q]:
            while not q.empty():
                try:
                    q.get_nowait()
                except asyncio.QueueEmpty:  # pragma: no cover - race condition
                    break
        self._tasks.clear()
