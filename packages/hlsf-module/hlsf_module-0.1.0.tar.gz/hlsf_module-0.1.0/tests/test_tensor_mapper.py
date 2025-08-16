import math

from hlsf_module.tensor_mapper import TensorMapper, _triangle_mapper
from hlsf_module.symbols.vocab import Vocab
from hlsf_module.symbols.schema import SymbolToken
from hlsf_module.text_encoder import TextEncoder


def make_mapper() -> TensorMapper:
    return TensorMapper(mapper=_triangle_mapper)


def test_tokens_to_triangles_count():
    mapper = make_mapper()
    vocab = Vocab()
    tokens = [
        SymbolToken(t=0, id=vocab.id("audio", b), mod="audio", feat={"mag": 1.0}, w=1)
        for b in [0, 1, 2, 1]
    ]
    mapper.update(tokens)
    state = mapper.to_hlsf()
    assert len(state.triangles) == 3  # unique bands
    # repeated calls should keep same count and leave internal state untouched
    graph_snapshot = {k: v.copy() for k, v in mapper.graph.items()}
    state2 = mapper.to_hlsf()
    state3 = mapper.to_hlsf()
    assert len(state2.triangles) == len(state.triangles)
    assert len(state3.triangles) == len(state.triangles)
    assert mapper.graph == graph_snapshot


def test_text_tokens_render_polygons():
    mapper = make_mapper()
    encoder = TextEncoder()
    tokens = encoder.step("abcab")
    mapper.update(tokens)
    state = mapper.to_hlsf()
    # Expect one triangle per unique character
    assert len(state.triangles) == len(set("abcab"))
    hlsf = state.to_hlsf()
    assert len(hlsf["triangles"]) == len(state.triangles)


def test_triangles_scaled_by_weight():
    mapper = make_mapper()
    vocab = Vocab()
    tokens = [
        SymbolToken(t=0, id=vocab.id("audio", i), mod="audio", feat={"mag": 0.0}, w=w)
        for i, w in enumerate([1.0, 3.0])
    ]
    mapper.update(tokens)
    state = mapper.to_hlsf()
    assert len(state.triangles) == 2
    mag0 = math.hypot(*state.triangles[0][0])
    mag1 = math.hypot(*state.triangles[1][0])
    assert mag1 > mag0
    assert state.colors[1][2] > state.colors[0][2]


def test_cross_modal_prototypes_merge_text_and_audio():
    vocab = Vocab()
    audio_id = vocab.id("audio", 0)
    mapper = make_mapper()
    enc = TextEncoder(vocab=vocab)
    audio_tok = SymbolToken(t=0, id=audio_id, mod="audio", feat={"mag": 1.0}, w=1)
    text_tok = enc.step("a")[0]
    mapper.update([audio_tok, text_tok])
    assert set(mapper.graph.keys()) == {1, 2}
    state = mapper.to_hlsf()
    assert len(state.triangles) == 2


def test_tokens_with_same_id_segregate_modalities():
    mapper = make_mapper()
    # Tokens deliberately share the same ``id`` but belong to different
    # modalities.  They should be assigned distinct bands.
    audio_tok = SymbolToken(t=0, id=1, mod="audio", feat={"mag": 1.0}, w=1)
    text_tok = SymbolToken(t=0, id=1, mod="text", feat={"mag": 1.0}, w=1)
    mapper.update([audio_tok, text_tok])
    state = mapper.to_hlsf()
    assert len(state.triangles) == 2


def test_rh_mapping_strategy_and_mode():
    vocab = Vocab()
    tok = SymbolToken(
        t=0,
        id=vocab.id("audio", 0),
        mod="audio",
        feat={"mag": 1.0, "harmonic": 0.0, "prime_channel": 0.7},
        w=1,
    )
    mapper = TensorMapper(mapping_strategy="rh")
    mapper.update([tok])
    state = mapper.to_hlsf()
    assert math.isclose(state.colors[0][0], 0.7)

    tok2 = SymbolToken(
        t=0,
        id=vocab.id("audio", 1),
        mod="audio",
        feat={"mag": 1.0, "harmonic": 1.0, "prime_channel": 0.4, "K_dev": 0.25},
        w=1,
    )
    mapper2 = TensorMapper(rh_mode=True)
    mapper2.update([tok2])
    state2 = mapper2.to_hlsf()
    assert math.isclose(state2.colors[0][0], 0.25)
