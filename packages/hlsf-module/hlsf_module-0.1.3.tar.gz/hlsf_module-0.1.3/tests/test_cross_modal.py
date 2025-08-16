from hlsf_module.cross_modal import CrossModalEmbedder
from hlsf_module.symbols.schema import SymbolToken
from hlsf_module.tensor_mapper import TensorMapper
from hlsf_module import agency_gates


def test_embeddings_align_and_gate():
    pairs = [([1.0, 0.0], [1.0, 0.0]), ([0.0, 1.0], [0.0, 1.0])]
    emb = CrossModalEmbedder(audio_dim=2, text_dim=2, embed_dim=2, lr=0.1)
    emb.train(pairs, epochs=50)

    # Matched tokens
    a_emb = emb.encode_audio([1.0, 0.0])
    t_emb = emb.encode_text([1.0, 0.0])
    tokens = [
        SymbolToken(t=0, id=1, mod="audio", feat={"embedding": a_emb}),
        SymbolToken(t=0, id=1, mod="text", feat={"embedding": t_emb}),
    ]
    mapper = TensorMapper()
    mapper.update(tokens)
    sim = mapper.symbolic_resonance_index()
    assert sim > 0.9
    assert agency_gates.decide({"scores": [sim, 0.1], "duration": 2, "detectors": 1}, threshold=0.5, margin=0.1, sustain=2) is True

    # Mismatched tokens produce lower similarity and fail the gate
    t_emb_mis = emb.encode_text([0.0, 1.0])
    tokens_mis = [
        SymbolToken(t=0, id=1, mod="audio", feat={"embedding": a_emb}),
        SymbolToken(t=0, id=1, mod="text", feat={"embedding": t_emb_mis}),
    ]
    mapper_mis = TensorMapper()
    mapper_mis.update(tokens_mis)
    sim_mis = mapper_mis.symbolic_resonance_index()
    assert sim_mis < sim
    assert agency_gates.decide({"scores": [sim_mis, 0.1], "duration": 2, "detectors": 1}, threshold=0.5, margin=0.1, sustain=2) is False
