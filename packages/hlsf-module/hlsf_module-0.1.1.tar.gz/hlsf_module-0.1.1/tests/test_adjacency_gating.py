from hlsf_module.text_fft import expand_adjacency_sync
from hlsf_module.llm_client import StubLLMClient
from hlsf_module.symbols.schema import SymbolToken
from hlsf_module.agency_gates import decide


def test_adjacency_expansion_and_gating_with_mock_llm():
    token = SymbolToken(t=0, id=1, mod="text", feat={"mag": 1.0, "text": "hi"}, w=1.0)
    stub = StubLLMClient(["foo", "bar"])
    adj = expand_adjacency_sync([token], llm=stub, q=0.0)
    assert adj[token.id]
    assert stub.calls == 1
    motif = {
        "scores": [1.0, 0.2],
        "cross_scores": [1.0] * len(adj[token.id]),
        "duration": 1,
        "detectors": 1,
    }
    assert decide(motif, threshold=0.5, cross_weight=0.5, margin=0.0)
