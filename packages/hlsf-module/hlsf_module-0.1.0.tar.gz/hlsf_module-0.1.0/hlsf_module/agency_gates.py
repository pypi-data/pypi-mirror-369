"""Resonance-based gate deciding whether to externalise a motif."""
from __future__ import annotations

from dataclasses import dataclass, field
from itertools import zip_longest
import logging
from typing import Any, Callable, Dict, Optional, Sequence, Union

from .gating_strategies import STRATEGIES, register_strategy

logger = logging.getLogger(__name__)


@dataclass
class GateConfig:
    """Configuration options for :func:`decide`.

    Each field corresponds to a keyword argument on :func:`decide`.  The
    dataclass is provided so that callers can bundle gate parameters together
    and reuse them across calls.
    """

    threshold: float = 0.2
    margin: float = 0.1
    sustain: int = 1
    detectors: int = 1
    coherence: Optional[float] = None
    peak: Optional[float] = None
    detector_var: Optional[float] = None
    strategy: Union[str, Callable[[Sequence[float], Dict[str, Any], "GateConfig"], float]] = "fixed"
    percentile: float = 50.0
    var_factor: float = 1.0
    ema_alpha: float = 0.5
    prev_threshold: Optional[float] = None
    trim_percent: float = 0.0
    slope_window: int = 5
    slope_factor: float = 1.0
    entropy_window: int = 5
    entropy_weight: float = 1.0
    cross_weight: float = 0.5
    k_target: float = 0.0
    weights: Dict[str, float] = field(
        default_factory=lambda: {
            "resonance": 1.0,
            "k_dev": 1.0,
            "prime": 0.0,
            "harmonic": 0.0,
        }
    )
    prime_priority: bool = False


def decide(
    motif: Dict[str, Any],
    *,
    threshold: float = 0.2,
    margin: float = 0.1,
    sustain: int = 1,
    detectors: int = 1,
    coherence: Optional[float] = None,
    peak: Optional[float] = None,
    detector_var: Optional[float] = None,
    strategy: Union[str, Callable[[Sequence[float], Dict[str, Any], GateConfig], float]] = "fixed",
    percentile: float = 50.0,
    var_factor: float = 1.0,
    ema_alpha: float = 0.5,
    prev_threshold: Optional[float] = None,
    trim_percent: float = 0.0,
    slope_window: int = 5,
    slope_factor: float = 1.0,
    entropy_window: int = 5,
    entropy_weight: float = 1.0,
    cross_weight: float = 0.5,
    k_target: float = 0.0,
    weights: Optional[Dict[str, float]] = None,
    prime_priority: bool = False,
    config: Optional[GateConfig] = None,
) -> bool:
    """Return ``True`` when resonance is strong and sustained.

    Parameters
    ----------
    motif:
        Expected to contain ``scores`` (an iterable of resonance scores for
        candidate symbols), ``duration`` (how long the best symbol has
        remained dominant) and ``detectors`` (how many detectors agree on the
        leading symbol).  Optional keys ``coherence``, ``peak`` and
        ``detector_var`` can be supplied when the corresponding gating
        thresholds are used.
    threshold:
        Minimum resonance score required for the best symbol.
    margin:
        Required difference between the best and second-best score.
    sustain:
        Number of consecutive steps the resonance must be sustained.
    detectors:
        Minimum number of detectors that must agree on the symbol.
    coherence:
        Minimum coherence value required.  The motif must provide a
        ``coherence`` field.
    peak:
        Minimum peak magnitude.  The motif must provide a ``peak`` field.
    detector_var:
        Maximum allowed variance between detectors.  The motif must provide a
        ``detector_var`` field.
    strategy:
        Name of the thresholding strategy or a custom callable.  Built-in
        strategies are registered in :mod:`hlsf_module.gating_strategies`.
    percentile:
        Percentile value used when ``strategy="percentile"``.  Expressed in the
        range ``[0, 100]``.
    var_factor:
        Multiplier applied to the score variance when ``strategy="variance"``.
    ema_alpha:
        Smoothing factor for ``strategy='ema'``.  Values in ``(0, 1]`` weight the
        current best score versus the previous threshold.
    prev_threshold:
        Previous threshold value used with ``strategy='ema'``.
    cross_weight:
        Weight applied to ``cross_scores`` provided in ``motif`` when combining
        cross-modal resonance with ``scores``.
    k_target:
        Target ``K`` value used to compute deviation penalties when
        ``strategy='rh'``.
    weights:
        Weighting factors for ``strategy='rh'``.  Expected keys are
        ``"resonance"``, ``"k_dev"``, ``"prime"`` and ``"harmonic"``.
    prime_priority:
        When ``True`` prime rewards take precedence over harmonic rewards in
        ``strategy='rh'``.
    config:
        Optional :class:`GateConfig` instance.  If supplied it overrides the
        individual keyword arguments.
    """

    if config is None:
        config = GateConfig(
            threshold=threshold,
            margin=margin,
            sustain=sustain,
            detectors=detectors,
            coherence=coherence,
            peak=peak,
            detector_var=detector_var,
            strategy=strategy,
            percentile=percentile,
            var_factor=var_factor,
            ema_alpha=ema_alpha,
            prev_threshold=prev_threshold,
            trim_percent=trim_percent,
            slope_window=slope_window,
            slope_factor=slope_factor,
            entropy_window=entropy_window,
            entropy_weight=entropy_weight,
            cross_weight=cross_weight,
            k_target=k_target,
            weights=weights or {
                "resonance": 1.0,
                "k_dev": 1.0,
                "prime": 0.0,
                "harmonic": 0.0,
            },
            prime_priority=prime_priority,
        )

    scores: Sequence[float] = motif.get("scores", []) or []
    if not scores and "mag" in motif:
        scores = [motif["mag"], 0.0]
    cross_scores: Sequence[float] = motif.get("cross_scores", []) or []
    if cross_scores:
        scores = [
            (1 - config.cross_weight) * s + config.cross_weight * c
            for s, c in zip_longest(scores, cross_scores, fillvalue=0.0)
        ]
    if not scores:
        return False
    # Sort scores to find best and runner-up values.
    sorted_scores_desc = sorted(scores, reverse=True)
    best = sorted_scores_desc[0]
    second = sorted_scores_desc[1] if len(sorted_scores_desc) > 1 else 0.0

    strat = config.strategy
    if callable(strat):
        threshold_val = strat(scores, motif, config)
    else:
        threshold_fn = STRATEGIES.get(strat, STRATEGIES["fixed"])
        threshold_val = threshold_fn(scores, motif, config)

    decision = True
    if best < threshold_val:
        decision = False
    if best - second < config.margin:
        decision = False
    duration_val = motif.get("duration", motif.get("run", 1))
    if duration_val < config.sustain:
        decision = False
    if motif.get("detectors", motif.get("det", 1)) < config.detectors:
        decision = False
    if config.coherence is not None and motif.get("coherence", 0.0) < config.coherence:
        decision = False
    if config.peak is not None and motif.get("peak", 0.0) < config.peak:
        decision = False
    if config.detector_var is not None and motif.get("detector_var", float("inf")) > config.detector_var:
        decision = False

    _update_adaptive_stats(motif, scores)
    logger.info(
        "gating decision",
        extra={"decision": decision, "best": best, "threshold": threshold_val},
    )
    return decision


def _update_adaptive_stats(motif: Dict[str, Any], scores: Sequence[float]) -> None:
    """Maintain running averages used by the adaptive threshold strategy."""

    stats = motif.setdefault("adaptive_stats", {"avg": [], "n": []})
    avgs = stats.setdefault("avg", [])
    counts = stats.setdefault("n", [])
    if len(avgs) < len(scores):
        avgs.extend([0.0] * (len(scores) - len(avgs)))
        counts.extend([0] * (len(scores) - len(counts)))
    for i, score in enumerate(scores):
        n = counts[i]
        avgs[i] = (avgs[i] * n + score) / (n + 1)
        counts[i] = n + 1

