import statistics

import pytest

from hlsf_module.agency_gates import GateConfig, decide
from hlsf_module.gating_strategies import STRATEGIES


def test_strategy_registry_contains_defaults() -> None:
    assert set(
        [
            "fixed",
            "percentile",
            "variance",
            "ema",
            "adaptive",
            "rh",
            "median",
            "trimmed_mean",
            "dynamic_slope",
            "entropy",
        ]
    ).issubset(STRATEGIES)


def test_percentile_variance_ema_strategies() -> None:
    cfg = GateConfig(percentile=50.0, var_factor=1.0, ema_alpha=0.5)
    scores = [0.1, 0.2, 0.3]
    assert STRATEGIES["percentile"](scores, {}, cfg) == 0.2
    assert STRATEGIES["variance"](scores, {}, cfg) == statistics.mean(scores) + cfg.var_factor * statistics.pvariance(scores)
    assert STRATEGIES["ema"](scores, {"prev_threshold": 0.1}, cfg) == (1 - cfg.ema_alpha) * 0.1 + cfg.ema_alpha * max(scores)


def test_adaptive_strategy_updates_threshold_over_steps() -> None:
    cfg = GateConfig()
    motif = {"scores": [0.2, 0.1], "duration": 1, "detectors": 1}
    # No running statistics yet; fallback to fixed threshold
    assert STRATEGIES["adaptive"](motif["scores"], motif, cfg) == cfg.threshold
    decide(motif, strategy="adaptive", threshold=cfg.threshold, margin=0.0)
    motif["scores"] = [0.4, 0.1]
    # Threshold adapts to average of first modality (0.2)
    assert STRATEGIES["adaptive"](motif["scores"], motif, cfg) == pytest.approx(0.2)
    decide(motif, strategy="adaptive", threshold=cfg.threshold, margin=0.0)
    motif["scores"] = [0.5, 0.1]
    # Running average updated to (0.2 + 0.4)/2 = 0.3
    assert STRATEGIES["adaptive"](motif["scores"], motif, cfg) == pytest.approx(0.3)


def test_rh_gate_combines_metrics() -> None:
    cfg = GateConfig(threshold=0.2)
    scores = [0.6, 0.1]
    expected = 0.5 * (max(scores) + cfg.threshold)
    assert STRATEGIES["rh"](scores, {"scores": scores}, cfg) == pytest.approx(expected)
