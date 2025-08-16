from __future__ import annotations

from typing import Callable, Dict, List, Sequence, Tuple

from .symbols.schema import SymbolToken
from . import agency_gates
from .gating_strategies import compute_K

# ---------------------------------------------------------------------------
# Relationship symbols
# ---------------------------------------------------------------------------

RELATIONSHIP_SYMBOLS: List[str] = [f"REL_{i:02d}" for i in range(50)]

# Cache structure: (token_id, relationship_symbol, list_index) -> list
_CACHE: Dict[Tuple[int, str, int], List[Tuple[int, float]]] = {}
_DONE: Dict[int, set[str]] = {}
_COMPLETED: set[int] = set()


def clear_cache() -> None:
    """Reset caches used for relationship lookups."""

    _CACHE.clear()
    _DONE.clear()
    _COMPLETED.clear()


def _prune(items: List[Tuple[int, float]]) -> List[Tuple[int, float]]:
    """Prune ``items`` below their median weight."""

    if not items:
        return items
    weights = sorted(w for _, w in items)
    thresh = weights[len(weights) // 2]
    return [(i, w) for i, w in items if w >= thresh]


def fetch_relationships(
    token: SymbolToken,
    relationship: str,
    llm: (
        Callable[
            [SymbolToken, str],
            Tuple[Sequence[Tuple[int, float]], Sequence[Tuple[int, float]]],
        ]
        | None
    ) = None,
) -> Tuple[List[Tuple[int, float]], List[Tuple[int, float]]]:
    """Return two weighted adjacency lists for ``token`` and ``relationship``."""

    key_f = (token.id, relationship, 0)
    key_b = (token.id, relationship, 1)
    if key_f in _CACHE and key_b in _CACHE:
        return _CACHE[key_f], _CACHE[key_b]

    llm_fn: Callable[
        [SymbolToken, str],
        Tuple[Sequence[Tuple[int, float]], Sequence[Tuple[int, float]]],
    ]
    if llm is None:

        def llm_fn(
            tok: SymbolToken, rel: str
        ) -> Tuple[Sequence[Tuple[int, float]], Sequence[Tuple[int, float]]]:
            forward = [
                (tok.id + 1, 1.0),
                (tok.id + 2, 0.5),
                (tok.id + 3, 0.1),
            ]
            backward = [
                (tok.id - 1, 0.9),
                (tok.id - 2, 0.4),
                (tok.id - 3, 0.1),
            ]
            return forward, backward

    else:
        llm_fn = getattr(llm, "relationships", llm)

    forward_raw, backward_raw = llm_fn(token, relationship)

    forward = _prune(list(forward_raw))
    backward = _prune(list(backward_raw))

    _CACHE[key_f] = forward
    _CACHE[key_b] = backward

    done = _DONE.setdefault(token.id, set())
    done.add(relationship)
    if len(done) == len(RELATIONSHIP_SYMBOLS):
        _COMPLETED.add(token.id)

    return forward, backward


def _default_gate(
    lst: List[Tuple[int, float]], *, strategy: str = "rh"
) -> List[Tuple[int, float]]:
    scores = [w for _, w in lst]
    K_val = compute_K(scores)
    motif = {
        "scores": scores,
        "duration": 1,
        "detectors": 1,
        "K_dev": abs(K_val - 0.0),
    }
    if agency_gates.decide(motif, strategy=strategy, k_target=0.0):
        return sorted(lst, key=lambda x: x[1], reverse=True)
    return lst


def expand_adjacency(
    token: SymbolToken,
    *,
    llm: (
        Callable[
            [SymbolToken, str],
            Tuple[Sequence[Tuple[int, float]], Sequence[Tuple[int, float]]],
        ]
        | None
    ) = None,
    gate: Callable[[List[Tuple[int, float]]], List[Tuple[int, float]]] | None = None,
    gate_strategy: str = "rh",
) -> Dict[str, List[List[Tuple[int, float]]]]:
    """Expand ``token`` across all relationship symbols."""

    gate_fn = gate or (lambda lst: _default_gate(lst, strategy=gate_strategy))
    out: Dict[str, List[List[Tuple[int, float]]]] = {}
    for rel in RELATIONSHIP_SYMBOLS:
        forward, backward = fetch_relationships(token, rel, llm=llm)
        forward = gate_fn(forward)
        backward = gate_fn(backward)
        out[rel] = [forward, backward]
    return out
