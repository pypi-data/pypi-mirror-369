import pytest

from hlsf_module import pruning
from hlsf_module.symbols.schema import SymbolToken


def test_apply_prunes_metric_dicts():
    graph = {
        0: 0.5,
        1: {"weight": 0.0005, "phase": 0.1},
        2: {"weight": 0.2},
    }
    removed = pruning.apply(graph, threshold=0.001)
    assert removed == [1]
    assert 1 not in graph and 0 in graph and 2 in graph


def test_prune_text_tokens_merges_and_filters_preserving_order():
    tokens = [
        SymbolToken(t=0, id=1, mod="text", feat={}, w=0.4),
        SymbolToken(t=1, id=2, mod="text", feat={}, w=0.2),
        SymbolToken(t=2, id=1, mod="text", feat={}, w=0.3),
    ]
    pruned = pruning.prune_text_tokens(tokens, min_weight=0.5)
    assert [t.id for t in pruned] == [1]
    assert pruned[0].w == pytest.approx(0.7)
    assert pruned[0].t == 0
