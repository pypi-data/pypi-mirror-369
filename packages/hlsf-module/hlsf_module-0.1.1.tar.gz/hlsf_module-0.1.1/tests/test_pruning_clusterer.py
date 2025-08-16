import pytest

from hlsf_module import pruning, clusterer, weights_bp
from hlsf_module.symbols.schema import SymbolToken

def test_prune_and_collapse():
    graph = {0: 0.5, 1: 0.0001, 2: 0.2}
    store = {1: {"w": 1, "f": 1, "s": 0.5}, 2: {"w": 1, "f": 1, "s": 1.0}}
    pruned = pruning.apply(graph, threshold=0.001)
    assert pruned == [1]
    assert 1 not in graph
    removed = clusterer.collapse(graph, density=1)
    assert removed == [2]
    weights_bp.update(graph, list(set(pruned) | set(removed)), store)
    # collapse should merge two remaining bands into one
    assert len(graph) == 1
    assert store[0]["w"] == 1 and store[0]["f"] == 1
    assert store[0]["s"] == pytest.approx(0.7)
    # pruned and collapsed bands get negative reinforcement
    assert store[1] == {"w": 0, "f": 0, "s": 0.0}
    assert store[2] == {"w": 0, "f": 0, "s": 0.0}


def test_collapse_reduces_to_density():
    graph = {0: 0.5, 1: 0.4, 2: 0.3, 3: 0.2, 4: 0.1}
    removed = clusterer.collapse(graph, density=2)
    assert len(removed) == 3
    assert len(graph) == 2
    assert sum(graph.values()) == pytest.approx(1.5)


def test_prune_text_tokens_dedup_and_filter():
    tokens = [
        SymbolToken(t=0, id=1, mod="text", feat={}, w=0.5),
        SymbolToken(t=1, id=1, mod="text", feat={}, w=0.6),
        SymbolToken(t=2, id=2, mod="text", feat={}, w=0.2),
    ]
    pruned_tokens = pruning.prune_text_tokens(tokens, min_weight=0.3)
    assert len(pruned_tokens) == 1
    assert pruned_tokens[0].id == 1
    assert pruned_tokens[0].w == pytest.approx(1.1)


def test_collapse_after_rotation_updates_weights():
    graph = {0: 0.5, 1: 0.4, 2: 0.3}
    angles = {0: 0.0, 1: 5.0, 2: 90.0}
    removed = clusterer.collapse_after_rotation(graph, angles, delta=10.0)
    # Bands 0 and 1 have similar angles, so band 1 should be merged into 0
    assert removed == [1]
    assert len(graph) == 2
    store: dict = {}
    weights_bp.update(graph, removed, store)

    assert store[0] == {"w": 1, "f": 1, "s": pytest.approx(0.9)}
    assert store[2] == {"w": 1, "f": 1, "s": pytest.approx(0.3)}
    # collapsed band gets its metrics decremented and clamped to zero
    assert store[1] == {"w": 0, "f": 0, "s": 0.0}
