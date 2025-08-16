import math

from hlsf_module.fft_tokenizer import FFTTokenizer


def test_token_features_are_present():
    sr = 8
    n_fft = 8
    tok = FFTTokenizer(sr=sr, n_fft=n_fft, hop=n_fft, n_bands=1)
    frame = [math.sin(2 * math.pi * i / sr) for i in range(n_fft)]
    tokens = tok.step(frame)
    assert tokens, "expected at least one token"
    t = tokens[0]
    assert t.peak_mag is not None
    assert t.centroid is not None
    assert t.bandwidth is not None
    assert t.coherence is not None
    assert t.mods and "mel0" in t.mods
