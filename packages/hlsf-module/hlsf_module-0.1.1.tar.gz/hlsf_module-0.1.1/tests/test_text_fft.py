import asyncio
import pytest
from hlsf_module.symbols.schema import SymbolToken
from hlsf_module.text_fft import (
    expand_adjacency_sync,
    expand_adjacency,
    prune_tokens,
    tokenize_text_fft,
)
from hlsf_module.llm_client import StubLLMClient
from hlsf_module.adjacency_expander import clear_cache


def test_deterministic_fft_tokens():
    t1 = tokenize_text_fft("hello")
    t2 = tokenize_text_fft("hello")
    sig1 = [
        (
            tok.id,
            round(tok.feat["mag"], 6),
            round(tok.feat["dphi"], 6),
            round(tok.feat.get("peak_mag", 0.0), 6),
            round(tok.feat.get("centroid", 0.0), 6),
            round(tok.feat.get("bandwidth", 0.0), 6),
            round(tok.feat.get("coherence", 0.0), 6),
        )
        for tok in t1
    ]
    sig2 = [
        (
            tok.id,
            round(tok.feat["mag"], 6),
            round(tok.feat["dphi"], 6),
            round(tok.feat.get("peak_mag", 0.0), 6),
            round(tok.feat.get("centroid", 0.0), 6),
            round(tok.feat.get("bandwidth", 0.0), 6),
            round(tok.feat.get("coherence", 0.0), 6),
        )
        for tok in t2
    ]
    assert sig1 == sig2


def test_adjacency_expansion_two_per_token():
    tokens = [
        SymbolToken(t=0, id=1, mod="m", feat={"mag": 0.1}),
        SymbolToken(t=1, id=2, mod="m", feat={"mag": 0.2}),
        SymbolToken(t=2, id=3, mod="m", feat={"mag": 0.3}),
        SymbolToken(t=3, id=4, mod="m", feat={"mag": 0.4}),
    ]
    stub = StubLLMClient(["a", "b"])
    adj = expand_adjacency_sync(tokens, q=0.5, llm=stub)

    assert len(adj) == 2
    assert stub.calls == 2
    assert all(len(v) == 2 for v in adj.values())


def test_expand_adjacency_with_stub_llm():
    """``expand_adjacency`` works with an object-based stub LLM."""
    tokens = [
        SymbolToken(t=0, id=1, mod="m", feat={"mag": 1.0}),
        SymbolToken(t=1, id=2, mod="m", feat={"mag": 2.0}),
    ]

    stub = StubLLMClient(["foo"])
    adj = expand_adjacency_sync(tokens, q=0.0, llm=stub)
    assert stub.calls == 2
    assert set(adj.keys()) == {1, 2}


def test_expand_adjacency_respects_max_concurrency_async():
    clear_cache()
    tokens = [SymbolToken(t=i, id=i + 1, mod="m", feat={"mag": 1.0}) for i in range(4)]

    class RecordingLLM(StubLLMClient):
        def __init__(self, responses):
            super().__init__(responses, delay=0.01)
            self.active = 0
            self.max_active = 0

        async def neighbors(self, text: str, *, count: int, prompt_template: str):
            self.active += 1
            self.max_active = max(self.max_active, self.active)
            try:
                return await super().neighbors(
                    text, count=count, prompt_template=prompt_template
                )
            finally:
                self.active -= 1

    llm = RecordingLLM(["foo"])
    asyncio.run(
        expand_adjacency(
            tokens, adjacency_percentile=0.0, llm=llm, max_concurrency=2
        )
    )
    assert llm.max_active == 2


def test_expand_adjacency_sync_respects_max_concurrency():
    clear_cache()
    tokens = [SymbolToken(t=i, id=i + 1, mod="m", feat={"mag": 1.0}) for i in range(4)]

    class RecordingLLM(StubLLMClient):
        def __init__(self, responses):
            super().__init__(responses, delay=0.01)
            self.active = 0
            self.max_active = 0

        async def neighbors(self, text: str, *, count: int, prompt_template: str):
            self.active += 1
            self.max_active = max(self.max_active, self.active)
            try:
                return await super().neighbors(
                    text, count=count, prompt_template=prompt_template
                )
            finally:
                self.active -= 1

    llm = RecordingLLM(["foo"])
    expand_adjacency_sync(
        tokens, q=0.0, llm=llm, max_concurrency=2
    )
    assert llm.max_active == 2


def test_pruning_leaves_expected_tokens():
    tokens = [
        SymbolToken(t=0, id=1, mod="m", feat={"mag": 0.05}),
        SymbolToken(t=1, id=2, mod="m", feat={"mag": 1.0}, w=1),
    ]
    pruned, mapper = prune_tokens(tokens, threshold=0.1)
    assert pruned == [1]
    assert list(mapper.graph.keys()) == [2]
