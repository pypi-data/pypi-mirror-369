"""Very small motif clusterer."""
from __future__ import annotations

from typing import Dict, List, Optional, Tuple

def collapse(graph: Dict[int, float], density: float = 8.0) -> List[int]:
    """Collapse low‑energy bands into a single meta motif.

    While the number of bands exceeds ``density`` the weakest band is removed
    and its weight folded into the strongest one.  The ids of removed bands
    are returned so callers can treat them as pruned for weight
    back‑propagation.
    """

    removed: List[int] = []
    while len(graph) > density:
        weakest = min(graph, key=graph.get)
        strongest = max(graph, key=graph.get)
        graph[strongest] += graph[weakest]
        del graph[weakest]
        removed.append(weakest)
    return removed


def collapse_after_rotation(
    graph: Dict[int, float], angles: Dict[int, float], delta: float = 15.0
) -> List[int]:
    """Collapse bands that rotate toward similar angles.

    ``angles`` maps band ids to rotation angles in degrees.  Bands whose
    angles differ by less than ``delta`` are merged, folding the weaker band
    into the stronger one.  The ids of removed bands are returned so callers
    can treat them as pruned for weight back‑propagation.
    """

    bands = sorted((b for b in angles if b in graph), key=lambda b: angles[b])
    removed: List[int] = []
    i = 0
    while i < len(bands) - 1:
        b1, b2 = bands[i], bands[i + 1]
        if abs(angles[b1] - angles[b2]) <= delta:
            if graph.get(b1, 0.0) >= graph.get(b2, 0.0):
                graph[b1] = graph.get(b1, 0.0) + graph.get(b2, 0.0)
                del graph[b2]
                removed.append(b2)
                bands.pop(i + 1)
            else:
                graph[b2] = graph.get(b2, 0.0) + graph.get(b1, 0.0)
                del graph[b1]
                removed.append(b1)
                bands.pop(i)
        else:
            i += 1
    return removed

