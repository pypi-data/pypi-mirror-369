from __future__ import annotations

"""Simple WebSocket server broadcasting :class:`HLSFState` updates."""

import asyncio
import json
from typing import Set

from .stream_pipeline import MultiStreamPipeline, StreamPipeline
from .tensor_mapper import HLSFState


async def stream_pipeline(
    pipeline: StreamPipeline | MultiStreamPipeline,
    host: str = "127.0.0.1",
    port: int = 8765,
) -> None:
    """Expose pipeline results to WebSocket clients.

    Each message contains the JSON representation returned by
    :meth:`HLSFState.to_hlsf` augmented with ``scores`` from the gating stage.
    When multiple modalities are present ``scores`` is a mapping from modality
    names to band/score pairs.  The function runs until ``pipeline.result_q``
    yields ``None``.
    """

    try:  # pragma: no cover - optional dependency
        import websockets
    except Exception as exc:  # pragma: no cover - import error path
        raise RuntimeError(
            "websockets is required for web streaming. Install with 'pip install websockets'"
        ) from exc

    clients: Set["websockets.WebSocketServerProtocol"] = set()

    async def handler(ws: "websockets.WebSocketServerProtocol") -> None:
        clients.add(ws)
        try:
            await ws.wait_closed()
        finally:  # pragma: no cover - network cleanup
            clients.discard(ws)

    async def broadcaster() -> None:
        while True:
            item = await pipeline.result_q.get()
            if item is None:
                break
            scores, state = item
            payload = state.to_hlsf()
            payload["scores"] = scores
            message = json.dumps(payload)
            if clients:
                await asyncio.gather(
                    *[c.send(message) for c in list(clients)], return_exceptions=True
                )
        await asyncio.gather(*(c.close() for c in list(clients)), return_exceptions=True)

    async with websockets.serve(handler, host, port):
        await broadcaster()
