from __future__ import annotations

"""Asynchronous pipeline processing text tokens to :class:`HLSFState`."""

import asyncio
import json
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

from .adjacency_expander import expand as expand_neighbors
from .llm_client import LLMClient
from .llm_weights import TrainingDB
from .tensor_mapper import TensorMapper, HLSFState
from .symbols.schema import SymbolToken
from .text_encoder import TextEncoder
from . import pruning

Scores = Dict[int, float]


@dataclass
class TextStreamPipeline:
    """Asynchronous text token pipeline producing ``HLSFState`` updates."""

    llm: LLMClient | None = None
    vocab_path: str | None = None
    queue_size: int = 1
    prune_threshold: float = 1e-3
    training_db: TrainingDB | None = None
    update_db: bool = False
    band_offset: int = 10000

    def __post_init__(self) -> None:
        self.token_q: "asyncio.Queue[Optional[List[SymbolToken]]]" = asyncio.Queue(self.queue_size)
        self.result_q: "asyncio.Queue[Optional[Tuple[Scores, HLSFState]]]" = asyncio.Queue(self.queue_size)
        self._encoder = TextEncoder(vocab_path=self.vocab_path)
        self._mapper = TensorMapper()
        self._tasks: List[asyncio.Task[None]] = []
        self._closed = False

    async def feed_text(self, text: str) -> None:
        """Encode ``text`` into tokens and enqueue them."""

        await self.feed_tokens(self._encoder.step(text))

    async def feed_tokens(self, tokens: List[SymbolToken]) -> None:
        """Enqueue ``tokens`` for processing."""

        await self.token_q.put(tokens)

    async def _worker(self) -> None:
        try:
            while True:
                tokens = await self.token_q.get()
                if tokens is None:
                    await self.result_q.put(None)
                    break
                tokens = pruning.prune_text_tokens(tokens, self.prune_threshold)
                extra: List[SymbolToken] = []
                if self.llm is not None and tokens:
                    tasks = [
                        expand_neighbors(
                            t,
                            self.llm,
                            training_db=self.training_db,
                            update=self.update_db,
                        )
                        for t in tokens
                    ]
                    expanded = await asyncio.gather(*tasks)
                    for items in expanded:
                        for js in items:
                            extra.append(SymbolToken(**json.loads(js)))
                all_tokens = pruning.prune_text_tokens(
                    list(tokens) + extra, self.prune_threshold
                )
                if all_tokens:
                    for t in all_tokens:
                        band = t.feat.get("band", t.id) + self.band_offset
                        t.feat["band"] = band
                        t.feat["modality"] = "text"
                    self._mapper.update(all_tokens)
                    pruning.apply(self._mapper.graph, self.prune_threshold)
                    state = self._mapper.to_hlsf()
                    scores = {
                        t.feat["band"]: float(t.feat.get("mag", t.w))
                        for t in all_tokens
                    }
                    await self.result_q.put((scores, state))
        except asyncio.CancelledError:  # pragma: no cover - cancellation path
            raise
        except Exception:  # pragma: no cover - unexpected errors
            await self.result_q.put(None)
            raise

    async def start(self) -> None:
        if self._tasks:
            return
        self._tasks.append(asyncio.create_task(self._worker()))

    async def stop(self) -> None:
        if self._closed:
            return
        self._closed = True
        await self.token_q.put(None)
        for t in self._tasks:
            t.cancel()
        await asyncio.gather(*self._tasks, return_exceptions=True)

    async def join(self) -> None:
        if self._tasks:
            await asyncio.gather(*self._tasks, return_exceptions=True)

    async def __aenter__(self) -> "TextStreamPipeline":
        await self.start()
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        await self.stop()
        for q in (self.token_q, self.result_q):
            while not q.empty():
                try:
                    q.get_nowait()
                except asyncio.QueueEmpty:  # pragma: no cover - race condition
                    break
