from math import pi, sin

from hlsf_module.fft_tokenizer import FFTTokenizer
from hlsf_module.verification import FFTResynthesizer, SynthVerifier, residual


def test_resynth_residual_small():
    sr, n_fft, hop, bands = 48000, 64, 64, 8
    frame = [sin(2 * pi * 440 * n / sr) for n in range(n_fft)]
    tok = FFTTokenizer(sr=sr, n_fft=n_fft, hop=hop, n_bands=bands)
    tokens = tok.step(frame)
    synth = FFTResynthesizer(sr=sr, n_fft=n_fft, n_bands=bands)
    recon = synth.step(tokens)
    err = residual(frame, recon)
    assert err < 0.5


def test_synth_verifier_api():
    sr, n_fft, hop, bands = 48000, 64, 64, 8
    frame = [sin(2 * pi * 440 * n / sr) for n in range(n_fft)]
    tok = FFTTokenizer(sr=sr, n_fft=n_fft, hop=hop, n_bands=bands)
    tokens = tok.step(frame)
    api = SynthVerifier(sr=sr, n_fft=n_fft, n_bands=bands)
    err = api.compare(frame, tokens)
    assert err < 0.5
