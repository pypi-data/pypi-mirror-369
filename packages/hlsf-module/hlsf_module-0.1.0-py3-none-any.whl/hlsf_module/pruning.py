"""Simple pruning utilities for tokens and token graphs."""
from __future__ import annotations

from typing import Dict, List, Mapping, Union

from .symbols.schema import SymbolToken


def apply(
    graph: Dict[int, Union[float, Mapping[str, float]]], threshold: float = 1e-3
) -> List[int]:
    """Prune weak bands from ``graph``.

    ``graph`` may contain raw float magnitudes or richer metric dictionaries as
    produced by :class:`TensorMapper`.  Only the ``weight`` entry is considered
    when pruning metric dictionaries.
    """

    pruned: List[int] = []
    for band in list(graph):
        val = graph[band]
        weight = val if isinstance(val, (int, float)) else float(val.get("weight", 0.0))
        if weight < threshold:
            pruned.append(band)
            del graph[band]
    return pruned


def prune_text_tokens(tokens: List[SymbolToken], min_weight: float) -> List[SymbolToken]:
    """Deduplicate and filter ``tokens``.

    Tokens with identical ``id`` values are merged by summing their weights.
    Any resulting token with aggregate weight below ``min_weight`` is discarded.
    The returned list preserves the order of first occurrence of each token id.
    """

    merged: Dict[int, SymbolToken] = {}
    for tok in tokens:
        weight = float(tok.w or tok.feat.get("mag", 0.0))
        if tok.id in merged:
            prev = merged[tok.id]
            total = (prev.w or prev.feat.get("mag", 0.0)) + weight
            merged[tok.id] = SymbolToken(
                t=prev.t,
                id=prev.id,
                mod=prev.mod,
                feat=prev.feat,
                w=total,
                f=prev.f,
            )
        else:
            merged[tok.id] = SymbolToken(
                t=tok.t,
                id=tok.id,
                mod=tok.mod,
                feat=tok.feat,
                w=weight,
                f=tok.f,
            )

    pruned = [
        tok
        for tok in merged.values()
        if (tok.w or tok.feat.get("mag", 0.0)) >= min_weight
    ]
    pruned.sort(key=lambda t: t.t)
    return pruned

