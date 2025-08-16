from hlsf_module.powerlaw import powerlaw_bands


def test_powerlaw_bands_monotonic_and_shape():
    edges = powerlaw_bands(sr=8000, n_fft=64, n_bands=4, exponent=2.0)
    assert len(edges) == 5
    assert edges[0] < edges[-1]
    assert edges[-1] == 8000 / 2
    assert all(a < b for a, b in zip(edges, edges[1:]))
    # exponent > 1 concentrates bands at low frequencies
    first_span = edges[1] - edges[0]
    last_span = edges[-1] - edges[-2]
    assert first_span < last_span
