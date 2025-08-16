from __future__ import annotations

from hlsf_module.adjacency_mapping import (
    RELATIONSHIP_SYMBOLS,
    clear_cache,
    expand_adjacency,
    fetch_relationships,
)
from hlsf_module.symbols.schema import SymbolToken


class DummyLLM:
    def __init__(self) -> None:
        self.calls = 0

    def relationships(self, token: SymbolToken, relationship: str):
        self.calls += 1
        forward = [
            (token.id + 1, 1.0),
            (token.id + 2, 0.5),
            (token.id + 3, 0.1),
        ]
        backward = [
            (token.id - 1, 0.9),
            (token.id - 2, 0.4),
            (token.id - 3, 0.1),
        ]
        return forward, backward


def test_two_lists_per_relationship() -> None:
    clear_cache()
    token = SymbolToken(t=0, id=1, mod="x", feat={})
    llm = DummyLLM()
    adj = expand_adjacency(token, llm=llm)
    assert len(adj) == len(RELATIONSHIP_SYMBOLS)
    for lists in adj.values():
        assert len(lists) == 2


def test_caching() -> None:
    clear_cache()
    token = SymbolToken(t=0, id=1, mod="x", feat={})
    llm = DummyLLM()
    expand_adjacency(token, llm=llm)
    first_calls = llm.calls
    expand_adjacency(token, llm=llm)
    assert llm.calls == first_calls


def test_pruning() -> None:
    clear_cache()
    token = SymbolToken(t=0, id=1, mod="x", feat={})

    class PruneLLM:
        def relationships(self, token: SymbolToken, relationship: str):
            forward = [(1, 0.1), (2, 0.5), (3, 0.9)]
            backward = [(4, 0.2), (5, 0.4), (6, 0.6)]
            return forward, backward

    llm = PruneLLM()
    fwd, bwd = fetch_relationships(token, RELATIONSHIP_SYMBOLS[0], llm=llm)
    assert fwd == [(2, 0.5), (3, 0.9)]
    assert bwd == [(5, 0.4), (6, 0.6)]
