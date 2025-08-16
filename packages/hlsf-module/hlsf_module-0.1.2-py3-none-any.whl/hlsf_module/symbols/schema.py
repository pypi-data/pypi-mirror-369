from __future__ import annotations

"""Shared symbol schema and serialization helpers."""

from dataclasses import asdict, dataclass
from typing import Dict, Iterable, List
import json


@dataclass(frozen=True)
class SymbolToken:
    t: int
    id: int
    mod: str
    feat: Dict[str, float]
    w: int = 0
    f: int = 0


class SymbolBatch(List[SymbolToken]):
    """List of :class:`SymbolToken` with JSON helpers."""

    def to_json(self) -> str:
        return json.dumps([asdict(t) for t in self])

    @classmethod
    def from_json(cls, data: str) -> "SymbolBatch":
        items = json.loads(data)
        batch = cls()
        for item in items:
            batch.append(SymbolToken(**item))
        return batch
