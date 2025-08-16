"""Simple integer weight back‑propagation."""
from __future__ import annotations

from typing import Dict, Iterable, List


def update(
    graph: Dict[int, float],
    pruned: Iterable[int],
    store: Dict[int, Dict[str, float]],
) -> None:
    """Update integer counters and prototype strength.

    ``store`` keeps ``{"w": int, "f": int, "s": float}`` per band.  For
    each surviving band ``w`` and ``f`` are incremented and ``s`` gains the
    band's current weight.  Pruned bands have all three metrics decremented by
    one and clamped to zero, modelling negative reinforcement.

    """

    for band, weight in graph.items():
        entry = store.setdefault(band, {"w": 0, "f": 0, "s": 0.0})
        entry["w"] += 1
        entry["f"] += 1
        entry["s"] += weight
    for band in pruned:
        entry = store.setdefault(band, {"w": 0, "f": 0, "s": 0.0})
        entry["w"] = max(0, entry["w"] - 1)
        entry["f"] = max(0, entry["f"] - 1)
        entry["s"] = max(0.0, entry["s"] - 1.0)

