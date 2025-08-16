"""Minimal FastAPI application exposing weight and list helpers.

The API intentionally mirrors the tiny surface of :mod:`weight_cache` to keep
tests lightweight while still demonstrating a web facing interface.

Endpoints
---------
``GET /weights/{key}``
    Return the cached weight for ``key`` (``{"weight": <float>}``).

``POST /weights/{key}``
    Store a weight using payload ``{"weight": <float>}``.

``POST /rotate``
    Rotate a list of numbers.  Payload:
    ``{"values": [...], "steps": <int>}`` → ``{"values": [...]}``.

``POST /collapse``
    Collapse a list of numbers.  Payload ``{"values": [...]}`` →
    ``{"value": <float>}``.
"""

from __future__ import annotations

from fastapi import FastAPI
from pydantic import BaseModel
from typing import List

from .weight_cache import WeightCache, collapse, rotate


class WeightPayload(BaseModel):
    weight: float


class RotatePayload(BaseModel):
    values: List[float]
    steps: int


class CollapsePayload(BaseModel):
    values: List[float]


def create_app(cache: WeightCache) -> FastAPI:
    """Return a FastAPI app wired to ``cache``."""

    app = FastAPI()

    @app.get("/weights/{key}")
    def get_weight(key: str) -> dict:
        return {"weight": cache.get(key)}

    @app.post("/weights/{key}")
    def set_weight(key: str, payload: WeightPayload) -> dict:
        cache.set(key, payload.weight)
        return {"status": "ok"}

    @app.post("/rotate")
    def rotate_view(payload: RotatePayload) -> dict:
        return {"values": rotate(payload.values, payload.steps)}

    @app.post("/collapse")
    def collapse_view(payload: CollapsePayload) -> dict:
        return {"value": collapse(payload.values)}

    return app

