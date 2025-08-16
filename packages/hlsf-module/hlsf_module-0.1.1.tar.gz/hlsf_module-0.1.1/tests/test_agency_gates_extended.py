import sys, pathlib

sys.path.append(str(pathlib.Path(__file__).resolve().parents[1]))

from hlsf_module.agency_gates import GateConfig, decide


def test_decide_with_additional_features():
    motif = {
        "scores": [0.9, 0.3],
        "duration": 3,
        "detectors": 4,
        "coherence": 0.8,
        "peak": 1.2,
        "detector_var": 0.05,
    }
    assert (
        decide(
            motif,
            threshold=0.5,
            margin=0.1,
            sustain=3,
            detectors=4,
            coherence=0.7,
            peak=1.0,
            detector_var=0.1,
        )
        is True
    )
    assert (
        decide(
            {**motif, "coherence": 0.5},
            threshold=0.5,
            margin=0.1,
            sustain=3,
            detectors=4,
            coherence=0.7,
            peak=1.0,
            detector_var=0.1,
        )
        is False
    )
    assert (
        decide(
            {**motif, "peak": 0.5},
            threshold=0.5,
            margin=0.1,
            sustain=3,
            detectors=4,
            coherence=0.7,
            peak=1.0,
            detector_var=0.1,
        )
        is False
    )
    assert (
        decide(
            {**motif, "detector_var": 0.2},
            threshold=0.5,
            margin=0.1,
            sustain=3,
            detectors=4,
            coherence=0.7,
            peak=1.0,
            detector_var=0.1,
        )
        is False
    )


def test_decide_with_config_object():
    cfg = GateConfig(
        threshold=0.5,
        margin=0.1,
        sustain=2,
        detectors=2,
        coherence=0.6,
        peak=1.0,
        detector_var=0.2,
    )
    motif = {
        "scores": [0.8, 0.2],
        "duration": 2,
        "detectors": 2,
        "coherence": 0.7,
        "peak": 1.1,
        "detector_var": 0.1,
    }
    assert decide(motif, config=cfg) is True
    assert decide({**motif, "peak": 0.5}, config=cfg) is False


def test_threshold_strategies() -> None:
    motif = {"scores": [0.3, 0.1, 0.0], "duration": 1, "detectors": 1}
    # Percentile-based threshold lowers the effective threshold below 0.5
    assert (
        decide(
            motif,
            threshold=0.5,
            strategy="percentile",
            percentile=50,
        )
        is True
    )
    motif2 = {"scores": [0.4, 0.3, 0.2], "duration": 1, "detectors": 1}
    assert (
        decide(
            motif2,
            threshold=0.5,
            strategy="variance",
            var_factor=5.0,
        )
        is True
    )
    assert (
        decide(
            motif2,
            threshold=0.5,
            strategy="variance",
            var_factor=20.0,
        )
        is False
    )


def test_dynamic_threshold_ema() -> None:
    motif = {
        "scores": [0.5, 0.3],
        "duration": 2,
        "detectors": 1,
        "prev_threshold": 0.4,
    }
    assert (
        decide(
            motif,
            threshold=0.6,
            strategy="ema",
            ema_alpha=0.5,
            sustain=2,
        )
        is True
    )


def test_cross_modal_weighting() -> None:
    motif = {
        "scores": [0.3, 0.2],
        "cross_scores": [0.7, 0.1],
        "duration": 1,
        "detectors": 1,
    }
    assert (
        decide({**motif, "cross_scores": []}, threshold=0.4, cross_weight=0.5)
        is False
    )
    assert decide(motif, threshold=0.4, cross_weight=0.5) is True
