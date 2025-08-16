import math
import pytest

from hlsf_module.modal_stream import ModalStream


def test_2d_windowing():
    data = [[1.0, 2.0], [3.0, 4.0]]
    shape = (2, 2)
    hop = (2, 2)
    stream = ModalStream.from_array(data, shape, hop)
    out = stream.read()
    assert out is not None
    wy = [0.5 - 0.5 * math.cos(2 * math.pi * i / (shape[0] - 1)) for i in range(shape[0])]
    wx = [0.5 - 0.5 * math.cos(2 * math.pi * j / (shape[1] - 1)) for j in range(shape[1])]
    norm = [[x / 4.0 for x in row] for row in data]
    expected = [[norm[i][j] * wy[i] * wx[j] for j in range(shape[1])] for i in range(shape[0])]
    for i in range(shape[0]):
        for j in range(shape[1]):
            assert out[i][j] == pytest.approx(expected[i][j])
    assert stream.read() is None


def test_3d_windowing():
    data = [
        [[1.0, 2.0], [3.0, 4.0]],
        [[5.0, 6.0], [7.0, 8.0]],
    ]
    shape = (2, 2, 2)
    hop = (2, 2, 2)
    stream = ModalStream.from_array(data, shape, hop)
    out = stream.read()
    assert out is not None
    wz = [0.5 - 0.5 * math.cos(2 * math.pi * i / (shape[0] - 1)) for i in range(shape[0])]
    wy = [0.5 - 0.5 * math.cos(2 * math.pi * j / (shape[1] - 1)) for j in range(shape[1])]
    wx = [0.5 - 0.5 * math.cos(2 * math.pi * k / (shape[2] - 1)) for k in range(shape[2])]
    norm = [
        [[val / 8.0 for val in row] for row in plane]
        for plane in data
    ]
    expected = [
        [
            [norm[i][j][k] * wz[i] * wy[j] * wx[k] for k in range(shape[2])]
            for j in range(shape[1])
        ]
        for i in range(shape[0])
    ]
    for i in range(shape[0]):
        for j in range(shape[1]):
            for k in range(shape[2]):
                assert out[i][j][k] == pytest.approx(expected[i][j][k])
    assert stream.read() is None
