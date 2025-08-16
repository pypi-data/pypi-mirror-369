"""Prototype trainer enforcing minimum spectral distance between examples."""

from __future__ import annotations

from typing import List
from pathlib import Path
import json
import math
import csv


def spectral_distance(a: List[float], b: List[float]) -> float:
    return math.sqrt(sum((x - y) ** 2 for x, y in zip(a, b)))


class PrototypeTrainer:
    """Store spectral prototypes enforcing a minimum distance."""

    def __init__(self, min_distance: float = 1.0) -> None:
        self.min_distance = min_distance
        self.prototypes: List[List[float]] = []

    def add(self, proto: List[float]) -> bool:
        """Add ``proto`` if it's far enough from existing ones.

        Returns ``True`` if the prototype was stored, ``False`` otherwise.
        """

        for p in self.prototypes:
            if spectral_distance(p, proto) < self.min_distance:
                return False
        self.prototypes.append(list(proto))
        return True

    def save(self, path: str | Path) -> None:
        """Serialise ``self.prototypes`` to *path* as JSON or CSV."""

        path = Path(path)
        if path.suffix.lower() == ".csv":
            with open(path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerows(self.prototypes)
        else:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(self.prototypes, f)

    def load(self, path: str | Path) -> None:
        """Load prototypes from *path* overwriting the current list."""

        path = Path(path)
        if path.suffix.lower() == ".csv":
            with open(path, "r", newline="", encoding="utf-8") as f:
                reader = csv.reader(f)
                self.prototypes = [[float(v) for v in row] for row in reader if row]
        else:
            with open(path, "r", encoding="utf-8") as f:
                self.prototypes = json.load(f)

    def merge(self, *others: "PrototypeTrainer") -> None:
        """Combine prototypes from ``others`` into this trainer.

        Each prototype from ``others`` is added via :meth:`add`, ensuring the
        minimum distance constraint remains in effect and avoiding duplicates.
        """

        for other in others:
            for proto in other.prototypes:
                self.add(proto)
