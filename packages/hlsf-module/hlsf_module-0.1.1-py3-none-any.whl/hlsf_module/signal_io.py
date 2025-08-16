"""Signal stream and asynchronous capture helpers."""

from __future__ import annotations

import asyncio
import logging
import math
from dataclasses import dataclass, field
from typing import IO, Iterable, List, Optional
logger = logging.getLogger(__name__)


def _window(name: str, n: int) -> List[float]:
    """Return ``n`` window coefficients for ``name``."""

    if name == "hann":
        return [0.5 - 0.5 * math.cos(2 * math.pi * i / (n - 1)) for i in range(n)]
    if name == "hamming":
        return [0.54 - 0.46 * math.cos(2 * math.pi * i / (n - 1)) for i in range(n)]
    if name == "blackman":
        return [
            0.42
            - 0.5 * math.cos(2 * math.pi * i / (n - 1))
            + 0.08 * math.cos(4 * math.pi * i / (n - 1))
            for i in range(n)
        ]
    if name == "rect":
        return [1.0] * n
    raise ValueError(f"unknown window type: {name}")


def _normalise(data: List[float], mode: str) -> List[float]:
    if mode == "none":
        return data
    if mode == "peak":
        peak = max(abs(x) for x in data) or 1.0
        return [x / peak for x in data]
    if mode == "rms":
        rms = math.sqrt(sum(x * x for x in data) / len(data)) or 1.0
        return [x / rms for x in data]
    raise ValueError(f"unknown normalisation mode: {mode}")


def _apply_pre_emphasis(frame: List[float], alpha: float, mode: str) -> None:
    if mode == "first_order":
        for i in range(len(frame) - 1, 0, -1):
            frame[i] -= alpha * frame[i - 1]
        return
    if mode == "dc_block":
        prev_x = frame[0]
        prev_y = 0.0
        for i, x in enumerate(frame):
            y = x - prev_x + alpha * prev_y
            frame[i] = y
            prev_x = x
            prev_y = y
        return
    raise ValueError(f"unknown pre-emphasis mode: {mode}")


@dataclass
class SignalStream:
    """Simple 1‑D normalised stream with optional pre‑emphasis."""

    data: List[float]
    sr: int
    frame: int
    hop: int
    pre_emphasis: float = 0.0
    pre_mode: str = "first_order"
    window: str = "hann"

    norm_mode: str = "peak"
    _pos: int = 0
    _win: List[float] = field(init=False)

    def __post_init__(self) -> None:  # pragma: no cover - trivial
        self.data = _normalise(self.data, self.norm_mode)
        self._win = _window(self.window, self.frame)

    # ------------------------------------------------------------------
    # factory helpers

    @classmethod
    def from_array(
        cls,
        data: Iterable[float] | IO[str],
        sr: int,
        frame: int,
        hop: int,
        pre_emphasis: float = 0.0,
        *,
        pre_mode: str = "first_order",
        norm_mode: str = "peak",
        window: str = "hann",
    ) -> tuple["SignalStream", float]:
        """Create a signal stream from ``data``.

        Returns a tuple containing the stream and the peak absolute sample
        value observed in the input before any normalisation is applied.
        """

        data_list = list(data)
        if not data_list:
            raise ValueError("data iterable is empty")
        peak = max(abs(x) for x in data_list) or 1.0
        stream = cls(
            list(data_list),
            sr,
            frame,
            hop,
            pre_emphasis,
            pre_mode,
            window,
            norm_mode,
        )
        return stream, peak

    @classmethod
    def from_iterable(
        cls,
        it: Iterable[float],
        sr: int,
        frame: int,
        hop: int,
        pre_emphasis: float = 0.0,
        *,
        pre_mode: str = "first_order",
        norm_mode: str = "peak",
        window: str = "hann",
    ) -> tuple["SignalStream", float]:
        stream, peak = cls.from_array(
            list(it),
            sr,
            frame,
            hop,
            pre_emphasis,
            pre_mode=pre_mode,
            norm_mode=norm_mode,
            window=window,
        )
        return stream, peak

    @classmethod
    def from_microphone(
        cls,
        duration: float,
        sr: int,
        frame: int,
        hop: int,
        pre_emphasis: float = 0.0,
        *,
        pre_mode: str = "first_order",
        norm_mode: str = "peak",
        window: str = "hann",
    ) -> "SignalStream":
        """Record ``duration`` seconds from the default microphone."""

        logger.info("recording microphone", extra={"duration": duration, "sr": sr})
        try:  # pragma: no cover - hardware path
            import sounddevice as sd  # type: ignore
        except ImportError as exc:  # pragma: no cover - optional
            raise RuntimeError(
                "sounddevice is required for microphone capture. Install with 'pip install hlsf_module[audio]'",
            ) from exc

        samples = sd.rec(int(duration * sr), samplerate=sr, channels=1, dtype="float32")
        sd.wait()
        data = samples.reshape(-1).tolist()
        logger.info("microphone capture complete", extra={"frames": len(data), "sr": sr})
        stream, _ = cls.from_array(
            data,
            sr,
            frame,
            hop,
            pre_emphasis,
            pre_mode=pre_mode,
            norm_mode=norm_mode,
            window=window,
        )
        return stream


    # ------------------------------------------------------------------
    # reading
    def read(self) -> Optional[List[float]]:
        if self._pos + self.frame > len(self.data):
            return None
        frame = self.data[self._pos : self._pos + self.frame]
        if self.pre_emphasis:
            frame = list(frame)
            _apply_pre_emphasis(frame, self.pre_emphasis, self.pre_mode)
        frame = [f * w for f, w in zip(frame, self._win)]
        self._pos += self.hop
        return frame


# ---------------------------------------------------------------------------
# asynchronous capture helpers


async def _iterate_stream(stream: SignalStream):
    while True:
        frame = stream.read()
        if frame is None:
            break
        yield frame
        await asyncio.sleep(0)


async def capture_file(
    fh: IO[str],
    *,
    sr: int,
    frame: int,
    hop: int,
    pre_emphasis: float = 0.0,
    pre_mode: str = "first_order",
    norm_mode: str = "peak",
    window: str = "hann",
):
    """Asynchronously read whitespace‑separated samples from ``fh``.

    The previous implementation read the entire file into memory before
    normalising and yielding frames.  This proved wasteful for large input
    files.  The new version scans the file twice: a first pass computes the
    normalisation factor and a second pass parses samples incrementally,
    yielding frames as soon as enough data is available.  Only a small
    sliding buffer of samples is kept in memory.
    """

    # ------------------------------------------------------------------
    # normalisation pass
    norm = 1.0
    if norm_mode != "none":
        peak = 0.0
        acc = 0.0
        count = 0
        for line in fh:
            for token in line.split():
                try:
                    val = float(token)
                except ValueError:  # pragma: no cover - defensive
                    continue
                if norm_mode == "peak":
                    peak = max(peak, abs(val))
                else:  # rms
                    acc += val * val
                    count += 1
        if norm_mode == "peak":
            norm = peak or 1.0
        else:
            norm = math.sqrt(acc / (count or 1)) or 1.0
        fh.seek(0)

    # ------------------------------------------------------------------
    # streaming pass
    buf: List[float] = []
    win = _window(window, frame)
    for line in fh:
        for token in line.split():
            if not token:
                continue
            buf.append(float(token) / norm)
            if len(buf) >= frame:
                fr = list(buf[:frame])
                if pre_emphasis:
                    _apply_pre_emphasis(fr, pre_emphasis, pre_mode)
                fr = [f * w for f, w in zip(fr, win)]
                yield fr
                del buf[:hop]
        await asyncio.sleep(0)


async def capture_socket(
    reader,
    *,
    sr: int,
    frame: int,
    hop: int,
    pre_emphasis: float = 0.0,
    pre_mode: str = "first_order",
    norm_mode: str = "peak",
    window: str = "hann",
):
    """Capture samples from an :class:`asyncio.StreamReader`.

    Instead of buffering the entire socket payload before processing, the
    function now parses each chunk as it arrives and yields frames
    immediately once enough samples are available.
    """

    buf: List[float] = []
    win = _window(window, frame)
    peak = 1.0
    acc = 0.0
    count = 0

    while True:
        chunk = await reader.read(4096)
        if not chunk:
            break
        text = chunk.decode()
        for token in text.split():
            if not token:
                continue
            val = float(token)
            if norm_mode == "peak":
                new_peak = max(peak, abs(val))
                if new_peak != peak:
                    if buf:
                        scale = peak / new_peak
                        buf = [x * scale for x in buf]
                    peak = new_peak
                buf.append(val / peak)
            elif norm_mode == "rms":
                count += 1
                acc += val * val
                rms = math.sqrt(acc / count) or 1.0
                if buf:
                    # rescale existing buffer when RMS changes
                    scale = peak / rms if peak != rms else 1.0
                    buf = [x * scale for x in buf]
                peak = rms
                buf.append(val / peak)
            else:  # none
                buf.append(val)

            if len(buf) >= frame:
                fr = list(buf[:frame])
                if pre_emphasis:
                    _apply_pre_emphasis(fr, pre_emphasis, pre_mode)
                fr = [f * w for f, w in zip(fr, win)]
                yield fr
                del buf[:hop]
        await asyncio.sleep(0)


async def capture_microphone(
    duration: float,
    *,
    sr: int,
    frame: int,
    hop: int,
    pre_emphasis: float = 0.0,
    pre_mode: str = "first_order",
    norm_mode: str = "peak",
    window: str = "hann",
):
    """Asynchronously capture audio from the default microphone."""
    logger.info(
        "starting async microphone capture",
        extra={"duration": duration, "sr": sr},
    )
    stream = SignalStream.from_microphone(
        duration,
        sr=sr,
        frame=frame,
        hop=hop,
        pre_emphasis=pre_emphasis,
        pre_mode=pre_mode,
        norm_mode=norm_mode,
        window=window,
    )
    async for frame_arr in _iterate_stream(stream):
        yield frame_arr
    logger.info("async microphone capture complete", extra={"sr": sr})
