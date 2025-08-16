import pytest

from hlsf_module.geometry import rotate_state, rotate_batched
from hlsf_module.tensor_mapper import HLSFState


def test_rotate_state_rotates_triangles():
    tri = [[0.0, 0.0], [1.0, 0.0], [0.0, 1.0]]
    state = HLSFState([tri], [[0.0, 0.0, 1.0, 1.0]])
    rotated = rotate_state(state, 90.0)
    xs = [p[0] for p in tri]
    ys = [p[1] for p in tri]
    centre = (sum(xs) / len(xs), sum(ys) / len(ys))
    expected = [list(p) for p in rotate_batched([tri], centre, 90.0)[0]]
    for (x, y), (ex, ey) in zip(rotated.triangles[0], expected):
        assert x == pytest.approx(ex)
        assert y == pytest.approx(ey)


def test_rotate_state_collapses_overlaps():
    tri1 = [[0.0, 0.0], [1.0, 0.0], [0.0, 1.0]]
    tri2 = [[0.1, 0.1], [1.1, 0.1], [0.1, 1.1]]
    state = HLSFState([tri1, tri2], [[0.0, 0.0, 1.0, 1.0], [0.0, 0.0, 3.0, 1.0]])
    collapsed = rotate_state(state, 0.0)
    assert len(collapsed.triangles) == 1
    assert collapsed.triangles[0][0][0] == pytest.approx(0.05)
    assert collapsed.triangles[0][0][1] == pytest.approx(0.05)
    assert collapsed.colors[0][2] == pytest.approx(2.0)
