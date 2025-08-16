from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, List, Tuple

from .tensor_mapper import _triangle_mapper


@dataclass
class RHMapping:
    """Minimal mapping that extracts band ids from tokens."""

    name: str = "rh"

    def map(self, tokens: Iterable) -> List[int]:  # pragma: no cover - simple
        out: List[int] = []
        for t in tokens:
            if hasattr(t, "band"):
                out.append(getattr(t, "band"))
            else:
                feat = getattr(t, "feat", {})
                out.append(int(feat.get("band", 0)))
        return out


register_mapper("rh", RHMapping)


def rh_mapper(idx: int, total: int, metrics: Dict[str, float]) -> Tuple[List[List[float]], List[float]]:
    """Basic RH mapping used by tests.

    The geometry is not meaningful; the first colour channel reflects
    ``K_dev`` when present otherwise ``prime_channel``.
    """

    color0 = metrics.get("K_dev", metrics.get("prime_channel", 0.0))
    tri = [[0.0, 0.0], [0.0, 0.0], [0.0, 0.0]]
    colour = [float(color0), 0.0, 0.0, 1.0]
    return tri, colour
