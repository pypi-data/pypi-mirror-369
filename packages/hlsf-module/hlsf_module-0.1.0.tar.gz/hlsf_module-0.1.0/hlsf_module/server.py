"""FastAPI server exposing text and audio prompt endpoints."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List
import asyncio
import json

from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from . import agency_gates, clusterer, rotation_rules
from .llm_weights import TrainingDB
from .text_fft import expand_adjacency, run_audio_pipeline, text_fft_pipeline
from .gating_strategies import compute_K

from .tensor_mapper import HLSFState
from .web_viewer import router as viewer_router

from . import plugins as _plugins  # ensure plugin entry points are loaded

app = FastAPI()
_db = TrainingDB()
_streams: list[asyncio.Queue[str]] = []
_latest: Dict[str, Any] | None = None


class TextRequest(BaseModel):
    prompt: str
    gate_threshold: float | None = None
    gate_strategy: str | None = None
    cross_weight: float | None = None
    rh_mode: bool = False
    rh_config: Dict[str, Any] | None = None
    mapping_strategy: str | None = None


class AudioRequest(BaseModel):
    duration: float = 1.0
    gate_threshold: float | None = None
    gate_strategy: str | None = None
    cross_weight: float | None = None
    rh_mode: bool = False
    rh_config: Dict[str, Any] | None = None
    mapping_strategy: str | None = None


class ImageRequest(BaseModel):
    path: str
    gate_threshold: float | None = None


def _prepare_response(
    tokens: List[Any],
    adj: Dict[int, List[int]],
    state: HLSFState,
    threshold: float | None,
    strategy: str | None = None,
    cross_weight: float | None = None,
) -> Dict[str, Any]:
    """Apply rotation/collapse, update TrainingDB and format JSON."""

    _db.update(tokens)
    stats = {t.feat.get("band", t.id): t.feat.get("dphi", 0.0) for t in tokens}
    angles = rotation_rules.for_motifs(stats)
    graph = {t.feat.get("band", t.id): t.feat.get("mag", 0.0) for t in tokens}
    collapsed = dict(graph)
    removed = clusterer.collapse_after_rotation(collapsed, angles)
    scores = [t.feat.get("mag", 0.0) for t in tokens]
    K_val = compute_K(scores)
    motif = {"scores": scores, "K_dev": abs(K_val - 0.0)}
    decision = agency_gates.decide(
        motif,
        threshold=threshold if threshold is not None else 0.2,
        strategy=strategy if strategy is not None else "rh",
        cross_weight=cross_weight if cross_weight is not None else 0.5,
        k_target=0.0,
    )
    snapshot = {
        "state": state.to_hlsf(),
        "gating": {"decision": decision, "threshold": threshold, "scores": scores},
    }
    global _latest
    _latest = snapshot
    for q in list(_streams):
        q.put_nowait(json.dumps(snapshot))
    return {
        "tokens": [t.__dict__ for t in tokens],
        "adjacency": adj,
        "adjacency_weights": _db.connections,
        "gating": snapshot["gating"],
        "geometry": snapshot["state"],
        "rotation": {"angles": angles, "collapsed": collapsed, "removed": removed},
    }


@app.post("/text")
async def process_text(req: TextRequest) -> Dict[str, Any]:
    tokens, adj, graph, state = text_fft_pipeline(
        req.prompt,
        rh_mode=req.rh_mode,
        rh_config=req.rh_config,
        gate_strategy=req.gate_strategy,
        mapping_strategy=req.mapping_strategy,
    )
    return _prepare_response(
        tokens, adj, state, req.gate_threshold, req.gate_strategy, req.cross_weight
    )


@app.post("/audio")
async def process_audio(req: AudioRequest) -> Dict[str, Any]:
    tokens, _, state = run_audio_pipeline(
        duration=req.duration,
        rh_mode=req.rh_mode,
        rh_config=req.rh_config,
        gate_strategy=req.gate_strategy,
        mapping_strategy=req.mapping_strategy,
    )
    adj = await expand_adjacency(tokens)
    return _prepare_response(
        tokens, adj, state, req.gate_threshold, req.gate_strategy, req.cross_weight
    )


@app.post("/image")
async def process_image(req: ImageRequest) -> Dict[str, Any]:
    enc = ImageEncoder()
    tokens = enc.step(req.path)
    adj = await expand_adjacency(tokens)
    mapper = TensorMapper()
    mapper.update(tokens)
    state = mapper.to_hlsf()
    return _prepare_response(tokens, adj, state, req.gate_threshold)


@app.get("/state")
async def get_state() -> Dict[str, Any]:
    """Return the most recent HLSF snapshot."""
    return _latest or {}


@app.get("/state/stream")
async def stream_state() -> StreamingResponse:
    """Stream state updates to connected clients using SSE."""

    async def event_generator() -> Any:
        q: asyncio.Queue[str] = asyncio.Queue()
        _streams.append(q)
        try:
            while True:
                data = await q.get()
                yield f"data: {data}\n\n"
        finally:  # pragma: no cover - network cleanup
            _streams.remove(q)

    return StreamingResponse(event_generator(), media_type="text/event-stream")


# Expose the viewer HTML and documentation
app.include_router(viewer_router)
static_dir = Path(__file__).resolve().parent.parent / "docs"
app.mount("/", StaticFiles(directory=static_dir, html=True), name="docs")
