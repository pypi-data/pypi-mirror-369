import math
import sys, pathlib
sys.path.append(str(pathlib.Path(__file__).resolve().parents[1]))

from hlsf_module import geometry


def test_canonical_start_angle():
    assert geometry.canonical_start_angle(3) == math.pi / 2
    assert geometry.canonical_start_angle(4) == 0.0


def test_total_replications():
    assert geometry.total_replications(3, 2) == 12
    assert geometry.total_replications(4, 3) == 84
    assert geometry.total_replications(5, 0) == 0


def test_build_base_triangles_square():
    sides = 4
    center = (0.0, 0.0)
    radius = 1.0
    angles = [geometry.canonical_start_angle(sides) + 2 * math.pi * i / sides for i in range(sides)]
    vertices = [(center[0] + radius * math.cos(a), center[1] + radius * math.sin(a)) for a in angles]
    tris = geometry.build_base_triangles(vertices, sides)
    assert len(tris) == 2
    assert all(len(tri) == 3 for tri in tris)


def test_calculate_symmetry_point_adjusted():
    center = (0.0, 0.0)
    radius = 1.0
    sides = 4
    assert geometry.HLSFGenerator.calculate_symmetry_point_adjusted(center, radius, sides, 1) == (
        0.0,
        0.0,
        0.0,
    )
    assert geometry.HLSFGenerator.calculate_symmetry_point_adjusted(center, radius, sides, 2) == (
        0.0,
        1.0,
        0.0,
    )


def test_rotate_batched_rotates_triangles():
    tri = [[(1.0, 0.0), (0.0, 1.0), (0.0, 0.0)]]
    rotated = geometry.rotate_batched(tri, (0.0, 0.0), 90.0)
    expected = [(0.0, 1.0), (-1.0, 0.0), (0.0, 0.0)]
    for (rx, ry), (ex, ey) in zip(rotated[0], expected):
        assert round(rx, 5) == round(ex, 5)
        assert round(ry, 5) == round(ey, 5)
