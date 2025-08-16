"""Very small motif clusterer."""
from __future__ import annotations

from typing import Dict, List, Mapping, Union

Value = Union[float, Mapping[str, float]]


def _weight(value: Value) -> float:
    """Extract numeric weight from ``value``."""

    if isinstance(value, Mapping):
        return value.get("weight", 0.0)
    return float(value)


def _add(value: Value, weight: float) -> Value:
    """Add ``weight`` to ``value`` and return the updated value."""

    if isinstance(value, Mapping):
        value = dict(value)
        value["weight"] = value.get("weight", 0.0) + weight
        return value
    return value + weight


def collapse(graph: Dict[int, Value], density: float = 8.0) -> List[int]:
    """Collapse low‑energy bands into a single meta motif.

    ``graph`` maps band ids to either float weights or dictionaries containing
    a ``"weight"`` entry.  While the number of bands exceeds ``density`` the
    weakest band is removed and its weight folded into the strongest one.  The
    ids of removed bands are returned so callers can treat them as pruned for
    weight back‑propagation.
    """

    removed: List[int] = []
    while len(graph) > density:
        weakest = min(graph, key=lambda b: _weight(graph[b]))
        strongest = max(graph, key=lambda b: _weight(graph[b]))
        graph[strongest] = _add(graph[strongest], _weight(graph[weakest]))
        del graph[weakest]
        removed.append(weakest)
    return removed


def collapse_after_rotation(
    graph: Dict[int, Value], angles: Dict[int, float], delta: float = 15.0
) -> List[int]:
    """Collapse bands that rotate toward similar angles.

    ``graph`` accepts the same value types as :func:`collapse`. ``angles`` maps
    band ids to rotation angles in degrees. Bands whose angles differ by less
    than ``delta`` are merged, folding the weaker band into the stronger one.
    The ids of removed bands are returned so callers can treat them as pruned
    for weight back‑propagation.
    """

    bands = sorted((b for b in angles if b in graph), key=lambda b: angles[b])
    removed: List[int] = []
    i = 0
    while i < len(bands) - 1:
        b1, b2 = bands[i], bands[i + 1]
        if abs(angles[b1] - angles[b2]) <= delta:
            if _weight(graph.get(b1, 0.0)) >= _weight(graph.get(b2, 0.0)):
                graph[b1] = _add(graph.get(b1, 0.0), _weight(graph.get(b2, 0.0)))
                del graph[b2]
                removed.append(b2)
                bands.pop(i + 1)
            else:
                graph[b2] = _add(graph.get(b2, 0.0), _weight(graph.get(b1, 0.0)))
                del graph[b1]
                removed.append(b1)
                bands.pop(i)
        else:
            i += 1
    return removed

