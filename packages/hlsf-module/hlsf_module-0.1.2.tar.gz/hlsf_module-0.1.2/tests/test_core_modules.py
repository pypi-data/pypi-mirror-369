import sys, pathlib
sys.path.append(str(pathlib.Path(__file__).resolve().parents[1]))

from math import pi
import math
import pytest
import math
import pytest

from hlsf_module import agency_gates, recursion_ctrl, rotation_rules, signal_io, weights_bp


def test_agency_gates_decide():
    assert (
        agency_gates.decide(
            {"scores": [0.9, 0.2], "duration": 2, "detectors": 2},
            threshold=0.5,
            margin=0.1,
            sustain=2,
            detectors=2,
        )
        is True
    )
    assert (
        agency_gates.decide(
            {"scores": [0.4, 0.3], "duration": 2, "detectors": 2},
            threshold=0.5,
            margin=0.1,
            sustain=2,
            detectors=2,
        )
        is False
    )
    assert (
        agency_gates.decide(
            {"scores": [0.9, 0.2], "duration": 1, "detectors": 2},
            threshold=0.5,
            margin=0.1,
            sustain=2,
            detectors=2,
        )
        is False
    )
    assert (
        agency_gates.decide(
            {"scores": [0.9, 0.2], "duration": 2, "detectors": 1},
            threshold=0.5,
            margin=0.1,
            sustain=2,
            detectors=2,
        )
        is False
    )
    assert agency_gates.decide({}) is False


def test_agency_gates_threshold_and_defaults():
    assert agency_gates.decide({"mag": 0.1, "run": 2}) is False
    assert agency_gates.decide({"mag": 0.2}) is True
    assert agency_gates.decide({"run": 2}) is False


def test_recursion_ctrl_update_threshold():
    if hasattr(recursion_ctrl.update, "history"):
        delattr(recursion_ctrl.update, "history")
    assert recursion_ctrl.update(1.0, window=3, threshold=0.5) is True
    assert recursion_ctrl.update(0.8, window=3, threshold=0.5) is True
    assert recursion_ctrl.update(0.4, window=3, threshold=0.5) is False


def test_weights_bp_update_counts_and_clamp():
    graph = {1: 0.5, 2: 0.3}
    pruned = [2, 3]
    store = {1: {"w": 1, "f": 1, "s": 0.0}, 2: {"w": 5, "f": 5, "s": 0.0}}
    weights_bp.update(graph, pruned, store)
    assert store[1] == {"w": 2, "f": 2, "s": pytest.approx(0.5)}
    assert store[2] == {"w": 5, "f": 5, "s": 0.0}
    assert store[3] == {"w": 0, "f": 0, "s": 0.0}


def test_rotation_rules_for_motifs():
    stats = {0: 0.0, 1: pi / 2, 2: -pi / 4}
    angles = rotation_rules.for_motifs(stats)
    assert angles[0] == 0.0
    assert round(angles[1], 5) == 90.0
    assert round(angles[2], 5) == -45.0


def test_resonance_scoring_converts_phase_to_degrees():
    stats = {0: pi / 3, 1: -pi / 6}
    angles = rotation_rules.for_motifs(stats)
    assert round(angles[0], 5) == 60.0
    assert round(angles[1], 5) == -30.0


def test_signal_stream_read_and_preemphasis():
    data = [1, 2, 3, 4]
    stream, _ = signal_io.SignalStream.from_array(
        data, sr=1, frame=4, hop=4, pre_emphasis=0.5
    )
    max_val = max(data)
    assert stream.data == [x / max_val for x in data]
    frame = stream.read()
    expected = [x / max_val for x in data]
    for i in range(3, 0, -1):
        expected[i] -= 0.5 * expected[i - 1]
    win = [0.5 - 0.5 * math.cos(2 * math.pi * i / 3) for i in range(4)]
    expected = [f * w for f, w in zip(expected, win)]
    assert [round(x, 5) for x in frame] == [round(x, 5) for x in expected]
    assert stream.read() is None


def test_signal_stream_normalisation_modes():
    data = [1, 2, 3, 4]
    stream, _ = signal_io.SignalStream.from_array(data, sr=1, frame=4, hop=4)
    assert stream.data == [x / 4 for x in data]
    rms_expected = (sum(x * x for x in data) / len(data)) ** 0.5
    stream_rms, _ = signal_io.SignalStream.from_array(
        data, sr=1, frame=4, hop=4, norm_mode="rms"
    )
    assert [round(x, 6) for x in stream_rms.data] == [
        round(x / rms_expected, 6) for x in data
    ]
    stream_none, _ = signal_io.SignalStream.from_array(
        data, sr=1, frame=4, hop=4, norm_mode="none"
    )
    assert stream_none.data == data

