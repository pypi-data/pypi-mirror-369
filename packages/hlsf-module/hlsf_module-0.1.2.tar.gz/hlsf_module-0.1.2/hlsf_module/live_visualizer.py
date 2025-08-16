"""Asynchronous matplotlib visualizer for live FFT pipeline."""

from __future__ import annotations

import queue
import threading
from typing import Dict

from .tensor_mapper import HLSFState


class LiveVisualizer:
    """Display resonance scores and triangle geometry in a background thread."""

    def __init__(self) -> None:
        self._queue: "queue.Queue[tuple[Dict[int, float], HLSFState] | None]" = queue.Queue()
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def _run(self) -> None:  # pragma: no cover - event loop
        try:
            import matplotlib.pyplot as plt
            from matplotlib.patches import Polygon
            from matplotlib.animation import FuncAnimation
        except Exception as exc:  # pragma: no cover - import error
            raise RuntimeError(
                "Matplotlib is required for live visualisation. Install with 'pip install hlsf_module[visualization]'"
            ) from exc

        fig, (ax_scores, ax_geom) = plt.subplots(1, 2)
        ax_scores.set_title("Resonance")
        ax_geom.set_title("Geometry")
        ax_geom.set_aspect("equal")

        data: tuple[Dict[int, float], HLSFState] | None = None

        def _update(_):
            nonlocal data
            try:
                item = self._queue.get_nowait()
            except queue.Empty:
                item = None
            if item is None:
                if data is None:
                    return []
            else:
                data = item
            if data is None:
                return []
            scores, state = data
            ax_scores.clear()
            ax_scores.set_title("Resonance")
            if scores:
                bands = list(scores.keys())
                mags = list(scores.values())
                ax_scores.bar(bands, mags)
            ax_geom.clear()
            ax_geom.set_title("Geometry")
            ax_geom.set_aspect("equal")
            for tri in state.triangles:
                ax_geom.add_patch(
                    Polygon(tri, closed=True, edgecolor="black", facecolor="none")
                )
            return []

        FuncAnimation(fig, _update, interval=100)
        plt.show()

    def update(self, scores: Dict[int, float], state: HLSFState) -> None:
        """Queue new data for display."""
        self._queue.put((scores, state))

    def close(self) -> None:
        """Signal the visualiser to close."""
        self._queue.put(None)
        self._thread.join(timeout=0.1)
