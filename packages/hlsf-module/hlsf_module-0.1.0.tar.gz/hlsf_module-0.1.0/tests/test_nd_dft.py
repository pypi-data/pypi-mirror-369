import pytest

from hlsf_module.fft_tokenizer import _nd_dft, _nd_dft_python


def test_nd_dft_matches_python():
    frame = [[0.0, 1.0], [2.0, 3.0]]
    n_fft = (4, 4)
    spec_vec = _nd_dft(frame, n_fft)
    spec_py = _nd_dft_python(frame, n_fft)
    assert spec_vec.keys() == spec_py.keys()
    for k in spec_vec:
        assert spec_vec[k] == pytest.approx(spec_py[k])
