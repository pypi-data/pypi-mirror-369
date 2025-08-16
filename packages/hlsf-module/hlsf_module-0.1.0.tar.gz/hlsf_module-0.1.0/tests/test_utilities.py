import sys, pathlib
import math
import pytest

sys.path.append(str(pathlib.Path(__file__).resolve().parents[1]))

from hlsf_module import agency_gates, recursion_ctrl, rotation_rules, weights_bp


def test_agency_gates_decide():
    motif = {"scores": [0.8, 0.3], "duration": 3, "detectors": 2}
    assert (
        agency_gates.decide(motif, threshold=0.5, margin=0.1, sustain=3, detectors=2)
        is True
    )
    assert (
        agency_gates.decide(
            {"scores": [0.4, 0.3], "duration": 3, "detectors": 2},
            threshold=0.5,
            margin=0.1,
            sustain=3,
            detectors=2,
        )
        is False
    )
    assert (
        agency_gates.decide(
            {"scores": [0.8, 0.3], "duration": 1, "detectors": 2},
            threshold=0.5,
            margin=0.1,
            sustain=3,
            detectors=2,
        )
        is False
    )
    assert (
        agency_gates.decide(
            {"scores": [0.8, 0.3], "duration": 3, "detectors": 1},
            threshold=0.5,
            margin=0.1,
            sustain=3,
            detectors=2,
        )
        is False
    )


def test_recursion_ctrl_update_stops_below_threshold():
    if hasattr(recursion_ctrl.update, "history"):
        delattr(recursion_ctrl.update, "history")
    for _ in range(7):
        assert recursion_ctrl.update(1.0) is True
    assert recursion_ctrl.update(0.1) is False


def test_rotation_rules_for_motifs_degrees_conversion():
    stats = {0: math.pi / 2, 1: math.pi}
    angles = rotation_rules.for_motifs(stats)
    assert angles[0] == pytest.approx(90.0)
    assert angles[1] == pytest.approx(180.0)


def test_weights_bp_update_increment_decrement_logic():
    graph = {1: 0.0, 2: 0.0}
    pruned = [2, 3]
    store = {}
    weights_bp.update(graph, pruned, store)
    assert store[1] == {"w": 1, "f": 1, "s": 0.0}
    assert store[2] == {"w": 0, "f": 0, "s": 0.0}
    assert store[3] == {"w": 0, "f": 0, "s": 0.0}
