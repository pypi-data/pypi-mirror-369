"""Threshold computation strategies for :mod:`hlsf_module.agency_gates`."""

from __future__ import annotations

import statistics
from typing import Any, Callable, Dict, Sequence, TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover - only for type checkers
    from .agency_gates import GateConfig


def compute_K(scores: Sequence[float]) -> float:
    """Compute a simple harmonic metric ``K`` from ``scores``."""

    return statistics.mean(scores) if scores else 0.0


def fixed(scores: Sequence[float], motif: Dict[str, Any], cfg: "GateConfig") -> float:
    """Return the fixed threshold from ``cfg``."""

    return cfg.threshold


def percentile(scores: Sequence[float], motif: Dict[str, Any], cfg: "GateConfig") -> float:
    """Return the ``cfg.percentile``-th percentile of ``scores``."""

    if not scores:
        return cfg.threshold
    sorted_scores = sorted(scores)
    idx = int(round((len(sorted_scores) - 1) * cfg.percentile / 100.0))
    return sorted_scores[idx]


def variance(scores: Sequence[float], motif: Dict[str, Any], cfg: "GateConfig") -> float:
    """Return ``mean(scores) + cfg.var_factor * variance(scores)``."""

    if not scores:
        return cfg.threshold
    mean = statistics.mean(scores)
    var = statistics.pvariance(scores)
    return mean + cfg.var_factor * var


def ema(scores: Sequence[float], motif: Dict[str, Any], cfg: "GateConfig") -> float:
    """Exponentially smoothed threshold following the best score."""

    if scores:
        best = max(scores)
    else:  # pragma: no cover - defensive
        best = 0.0
    prev = motif.get("prev_threshold", cfg.prev_threshold if cfg.prev_threshold is not None else cfg.threshold)
    alpha = cfg.ema_alpha
    return (1 - alpha) * prev + alpha * best


def adaptive(scores: Sequence[float], motif: Dict[str, Any], cfg: "GateConfig") -> float:
    """Return a threshold based on running averages stored in ``motif``.

    The function expects ``motif`` to contain an ``"adaptive_stats"`` entry
    with per-modality running averages under the ``"avg"`` key.  The
    :func:`hlsf_module.agency_gates.decide` function is responsible for
    maintaining these statistics across calls.

    If no statistics are available, ``cfg.threshold`` is used as a fallback.
    """

    stats = motif.get("adaptive_stats") or {}
    avgs = stats.get("avg", [])
    if not avgs:
        return cfg.threshold
    best_idx = max(range(len(scores)), key=lambda i: scores[i]) if scores else 0
    if best_idx >= len(avgs):
        return cfg.threshold
    return avgs[best_idx]


def rh(scores: Sequence[float], motif: Dict[str, Any], cfg: "GateConfig") -> float:
    """Intermediate threshold between best score and fixed threshold."""

    if scores:
        return 0.5 * (max(scores) + cfg.threshold)
    return cfg.threshold


def median(scores: Sequence[float], motif: Dict[str, Any], cfg: "GateConfig") -> float:
    """Return the median of ``scores`` or ``cfg.threshold`` when empty."""

    return statistics.median(scores) if scores else cfg.threshold


def trimmed_mean(scores: Sequence[float], motif: Dict[str, Any], cfg: "GateConfig") -> float:
    """Return the mean of ``scores`` after trimming extremes."""

    if not scores:
        return cfg.threshold
    if cfg.trim_percent <= 0:
        return statistics.mean(scores)
    sorted_scores = sorted(scores)
    k = int(len(sorted_scores) * cfg.trim_percent / 100.0)
    trimmed = sorted_scores[k: len(sorted_scores) - k] or sorted_scores
    return statistics.mean(trimmed)


def dynamic_slope(scores: Sequence[float], motif: Dict[str, Any], cfg: "GateConfig") -> float:
    """Adjust threshold based on slope of recent best scores."""

    history = motif.setdefault("slope_history", [])
    best = max(scores) if scores else 0.0
    history.append(best)
    if len(history) > cfg.slope_window:
        del history[:-cfg.slope_window]
    if len(history) < 2:
        return cfg.threshold
    slope = (history[-1] - history[0]) / (len(history) - 1)
    return history[-1] - cfg.slope_factor * slope


def entropy(scores: Sequence[float], motif: Dict[str, Any], cfg: "GateConfig") -> float:
    """Scale threshold by the entropy of ``scores`` over a rolling window."""

    if not scores:
        return cfg.threshold
    total = sum(scores)
    if total <= 0:
        return cfg.threshold
    probs = [s / total for s in scores if s > 0]
    import math

    ent = -sum(p * math.log(p, 2) for p in probs)
    max_ent = math.log(len(scores), 2) if scores else 1.0
    norm_ent = ent / max_ent if max_ent else 0.0
    history = motif.setdefault("entropy_history", [])
    history.append(norm_ent)
    if len(history) > cfg.entropy_window:
        del history[:-cfg.entropy_window]
    avg_ent = sum(history) / len(history)
    return cfg.threshold * (1 + cfg.entropy_weight * avg_ent)

STRATEGIES: Dict[str, Callable[[Sequence[float], Dict[str, Any], "GateConfig"], float]] = {
    "fixed": fixed,
    "percentile": percentile,
    "variance": variance,
    "ema": ema,
    "adaptive": adaptive,
    "rh": rh,
    "median": median,
    "trimmed_mean": trimmed_mean,
    "dynamic_slope": dynamic_slope,
    "entropy": entropy,
}


def register_strategy(
    name: str,
    func: Callable[[Sequence[float], Dict[str, Any], "GateConfig"], float],
) -> None:
    """Register ``func`` as a gating strategy under ``name``."""

    STRATEGIES[name] = func

