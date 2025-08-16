from __future__ import annotations

"""Simple sliding-window graph tracking token weights and frequency."""

from collections import deque
from typing import Deque, Dict, Iterable, List

from .schema import SymbolToken


class SymbolGraph:
    """Track token energy and basic statistics."""

    def __init__(self, window: int = 32, decay: float = 0.9) -> None:
        self.window = window
        self.decay = decay
        self.weights: Dict[int, int] = {}
        self.freq: Dict[int, int] = {}
        self._queue: Deque[int] = deque()
        self._stats: Dict[str, float] = {"energy": 0.0, "novelty": 0.0, "stability": 0.0}

    def update(self, tokens: Iterable[SymbolToken]) -> None:
        for k in list(self.weights):
            self.weights[k] = int(self.weights[k] * self.decay)
            if self.weights[k] == 0:
                del self.weights[k]
        new_ids: List[int] = []
        for tok in tokens:
            self.weights[tok.id] = self.weights.get(tok.id, 0) + (tok.w or 1)
            self.freq[tok.id] = self.freq.get(tok.id, 0) + 1
            self._queue.append(tok.id)
            new_ids.append(tok.id)
        while len(self._queue) > self.window:
            old = self._queue.popleft()
            self.weights[old] -= 1
            if self.weights[old] <= 0:
                del self.weights[old]
        self._stats = {
            "energy": float(sum(self.weights.values())),
            "novelty": float(len(set(new_ids))),
            "stability": float(len(self.weights)),
        }

    def stats(self) -> Dict[str, float]:
        return dict(self._stats)
