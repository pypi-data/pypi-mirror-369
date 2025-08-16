import asyncio

from hlsf_module.text_fft import text_fft_pipeline
from hlsf_module.llm_client import StubLLMClient


def test_text_fft_pipeline_integration():
    stub = StubLLMClient(["foo"])
    tokens, adj, graph, state = asyncio.run(
        text_fft_pipeline("hi", llm=stub, prune_threshold=0.01, adjacency_percentile=0.5)
    )
    assert tokens
    assert adj
    assert graph
    assert state.triangles
    assert stub.calls == len(adj)
    assert state.metrics["token_count"] == len(tokens)
    assert "symbolic_resonance" in state.resonance_metrics
