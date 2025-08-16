"""Monitor diminishing returns for recursion."""

from __future__ import annotations

from collections import deque
import statistics
from typing import Deque


class RecursionController:
    """Sliding-window heuristic that decides when to stop recursion.

    Symbolic Resonance Index (SRI) values are appended to :attr:`history`.  Once
    the relative gain between the newest entry and a reference value derived
    from the history falls below ``threshold`` recursion should stop.  The
    reference value is determined by ``gain_metric`` which may be ``"first"``
    (the oldest entry), ``"mean"`` or ``"median"``.
    """

    def __init__(
        self,
        window: int = 8,
        threshold: float = 1 / 3.636,
        gain_metric: str = "first",
    ) -> None:
        self.window = window
        self.threshold = threshold
        self.gain_metric = gain_metric
        self.history: Deque[float] = deque(maxlen=window)

    def reset(self) -> None:
        """Clear the stored metric history."""

        self.history.clear()

    def update(self, resonance_index: float) -> bool:
        """Append ``resonance_index`` and return ``True`` to continue recursion."""

        self.history.append(resonance_index)
        if len(self.history) < self.window:
            return True
        if self.gain_metric == "mean":
            ref = statistics.mean(self.history)
        elif self.gain_metric == "median":
            ref = statistics.median(self.history)
        else:
            ref = self.history[0]
        ref = ref or 1e-9
        gain = (self.history[-1] - ref) / abs(ref)
        return gain >= self.threshold


__all__ = ["RecursionController"]


_GLOBAL_CTRL: RecursionController | None = None


def update(
    resonance_index: float,
    window: int = 8,
    threshold: float = 1 / 3.636,
    gain_metric: str = "first",
) -> bool:
    """Module-level helper mirroring :class:`RecursionController.update`.

    A singleton controller instance is used to maintain history across calls,
    allowing simple stateful recursion control without explicitly creating a
    :class:`RecursionController`.  The function exposes its ``history`` via an
    attribute so tests can reset it when needed.
    """

    global _GLOBAL_CTRL
    if (
        _GLOBAL_CTRL is None
        or _GLOBAL_CTRL.window != window
        or _GLOBAL_CTRL.threshold != threshold
        or _GLOBAL_CTRL.gain_metric != gain_metric
    ):
        _GLOBAL_CTRL = RecursionController(
            window=window, threshold=threshold, gain_metric=gain_metric
        )
    result = _GLOBAL_CTRL.update(resonance_index)
    update.history = _GLOBAL_CTRL.history  # type: ignore[attr-defined]
    return result


__all__.append("update")
