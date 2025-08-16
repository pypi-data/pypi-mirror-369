import math

import pytest

from hlsf_module.fft_tokenizer import FFTTokenizer


def test_mel_banding_edges():
    sr = 8000
    n_fft = 256
    nb = 4
    tok = FFTTokenizer(sr=sr, n_fft=n_fft, hop=64, banding="mel", n_bands=nb)
    edges = tok._edges[0]
    f_min = sr / n_fft
    f_max = sr / 2
    mel_min = 2595 * math.log10(1 + f_min / 700)
    mel_max = 2595 * math.log10(1 + f_max / 700)
    step = (mel_max - mel_min) / nb
    expected = [700 * (10 ** ((mel_min + i * step) / 2595) - 1) for i in range(nb + 1)]
    assert edges == pytest.approx(expected)
