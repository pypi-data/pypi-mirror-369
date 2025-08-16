from hlsf_module.text_fft import TextFFTPipeline


def test_pipeline_records_token_history():
    pipe = TextFFTPipeline()
    tokens, adj, graph, state = pipe.run("hi")
    # Should have at least raw, fft, adjacency and pruned snapshots
    names = [snap["name"] for snap in pipe.token_history]
    assert names[0] == "raw"
    assert "pruned" in names
    # Final snapshot should carry an HLSF state
    assert pipe.token_history[-1]["state"] is not None
