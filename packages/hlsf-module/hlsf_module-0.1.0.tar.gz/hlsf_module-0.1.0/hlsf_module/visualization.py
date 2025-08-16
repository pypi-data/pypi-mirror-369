"""Minimal visualization helpers for geometry output."""

from __future__ import annotations

import argparse
import math
from typing import Sequence

from .tensor_mapper import HLSFState

from .geometry import (
    canonical_start_angle,
    build_base_triangles,
    rotate_batched,
)


def state_to_json_shapes(state: HLSFState) -> list[dict[str, Sequence[float]]]:
    """Return a JSON-serialisable mapping of polygon coordinates and colours.

    Each triangle is expanded into ``{"x": [...], "y": [...], "color": [...]}``
    where the vertex lists are closed to form a patch suitable for web
    frameworks such as Plotly.
    """

    shapes = []
    for tri, col in zip(state.triangles, state.colors):
        xs = [p[0] for p in tri] + [tri[0][0]]
        ys = [p[1] for p in tri] + [tri[0][1]]
        shapes.append({"x": xs, "y": ys, "color": col})
        
    return shapes


def show_polygons(center: Sequence[float], radius: float, sides: int) -> None:
    """Render base triangles of a regular polygon using Matplotlib.

    The function imports Matplotlib lazily so the dependency is optional.
    """

    try:
        import matplotlib.pyplot as plt
        from matplotlib.patches import Polygon
    except Exception as exc:  # pragma: no cover - import error path
        raise RuntimeError(
            "Matplotlib is required for visualization. Install with 'pip install hlsf_module[visualization]'"
        ) from exc

    cx, cy = center
    start_angle = canonical_start_angle(sides)
    angles = [start_angle + 2 * math.pi * i / sides for i in range(sides)]
    vertices = [(cx + radius * math.cos(a), cy + radius * math.sin(a)) for a in angles]
    tris = build_base_triangles(vertices, sides)

    fig, ax = plt.subplots()
    for tri in tris:
        ax.add_patch(Polygon(tri, closed=True, edgecolor="black", facecolor="none"))
    ax.set_aspect("equal")
    plt.show()


class PolygonGUI:
    """Thin wrapper around :func:`show_polygons` for CLI usage."""

    def __init__(
        self, center, radius, sides, levels, is_rotation_animation_running=True
    ):
        self.center = center
        self.radius = radius
        self.sides = sides
        self.levels = levels
        self.is_rotation_animation_running = is_rotation_animation_running

    def run(self) -> None:
        """Render multiple replicated polygon levels with optional rotation.

        The method mirrors :func:`show_polygons` but additionally replicates the
        base triangle motif ``levels`` times, rotating each batch according to
        the number of sides.  When ``is_rotation_animation_running`` is true the
        entire arrangement is continuously rotated using a simple Matplotlib
        animation.
        """

        try:
            import matplotlib.pyplot as plt
            from matplotlib.patches import Polygon
            from matplotlib.animation import FuncAnimation
        except Exception as exc:  # pragma: no cover - import error path
            raise RuntimeError(
                "Matplotlib is required for visualization. Install with 'pip install hlsf_module[visualization]'"
            ) from exc

        cx, cy = self.center
        start_angle = canonical_start_angle(self.sides)
        angles = [start_angle + 2 * math.pi * i / self.sides for i in range(self.sides)]
        vertices = [
            (cx + self.radius * math.cos(a), cy + self.radius * math.sin(a))
            for a in angles
        ]
        base_tris = build_base_triangles(vertices, self.sides)

        # Replicate triangles across levels by rotating batches around the
        # centre.  Level numbering starts at 1 to match ``total_replications``
        # in :mod:`geometry`.
        all_tris = []
        for level in range(1, self.levels + 1):
            reps = self.sides**level
            step = 360.0 / reps
            for i in range(reps):
                all_tris.extend(rotate_batched(base_tris, self.center, step * i))

        fig, ax = plt.subplots()
        patches = [
            Polygon(tri, closed=True, edgecolor="black", facecolor="none")
            for tri in all_tris
        ]
        for patch in patches:
            ax.add_patch(patch)
        ax.set_aspect("equal")

        if self.is_rotation_animation_running:
            # Rotate all triangles about the centre over successive frames.
            def _update(frame):
                rotated = rotate_batched(all_tris, self.center, frame)
                for patch, tri in zip(patches, rotated):
                    patch.set_xy(tri)
                return patches

            FuncAnimation(fig, _update, frames=360, interval=50, blit=True)
            plt.show()
        else:
            plt.show()


class HLSFViewer:
    """Display triangles produced by :class:`TensorMapper` in real time.

    The viewer is intentionally lightweight.  It maintains a set of Matplotlib
    ``Polygon`` patches which are updated in-place whenever new triangle data is
    supplied via :meth:`update`.  ``state.active_motif`` is interpreted as the
    index of the active triangle and is highlighted with a red outline.  Callers
    should subtract one from band identifiers returned by
    :meth:`TensorMapper.to_hlsf` if required.
    """

    def __init__(self, state: HLSFState | None = None) -> None:
        try:  # pragma: no cover - import error path
            import matplotlib.pyplot as plt
            from matplotlib.patches import Polygon
        except Exception as exc:  # pragma: no cover - import error path
            raise RuntimeError(
                "Matplotlib is required for visualization. Install with 'pip install hlsf_module[visualization]'"
            ) from exc

        self._plt = plt
        self._Polygon = Polygon
        self._fig, self._ax = plt.subplots()
        self._patches: list[Polygon] = []
        self._ax.set_aspect("equal")

        if state is not None:
            self.update(state)

    def update(self, state: HLSFState) -> None:
        """Update the viewer with new triangle geometry and colours."""

        if len(self._patches) != len(state.triangles):
            for patch in self._patches:
                patch.remove()
            self._patches = []
            for tri, col in zip(state.triangles, state.colors):
                patch = self._Polygon(tri, closed=True, facecolor=col[:3], alpha=col[3])
                self._ax.add_patch(patch)
                self._patches.append(patch)
        else:
            for patch, tri, col in zip(self._patches, state.triangles, state.colors):
                patch.set_xy(tri)
                patch.set_facecolor(col[:3])
                patch.set_alpha(col[3])

        active = state.active_motif
        for idx, patch in enumerate(self._patches):
            if active is not None and idx == active:
                patch.set_edgecolor("red")
                patch.set_linewidth(2.0)
            else:
                patch.set_edgecolor("black")
                patch.set_linewidth(1.0)

        self._fig.canvas.draw_idle()
        # ``pause`` allows live updates without blocking the main thread.
        self._plt.pause(0.001)

    def show(self) -> None:
        """Block until the visualisation window is closed."""

        self._plt.show()


class PipelineGUI:
    """Tk-based viewer exposing token and adjacency lists.

    A simple helper used by examples and demos to inspect the output of the
    text/FFT pipeline.  A Matplotlib figure displays the generated triangles
    while two scrollable listboxes show the individual tokens and expanded
    adjacency mappings.  Selecting a token highlights the corresponding triangle
    in the plot.
    """

    def __init__(self, text: str, vocab_path: str | None = None) -> None:
        import tkinter as tk
        from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
        from matplotlib.patches import Polygon

        from .text_fft import tokenize_text_fft, expand_adjacency_sync
        from .tensor_mapper import TensorMapper
        from .symbols.vocab import Vocab

        # --- setup window and frames -------------------------------------------------
        self._tk = tk
        self._root = tk.Tk()
        self._root.title("Text / Audio Pipeline")

        pipeline_frame = tk.LabelFrame(self._root, text="Text / Audio Pipeline")
        pipeline_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        token_frame = tk.Frame(pipeline_frame)
        token_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.token_list = tk.Listbox(token_frame, width=40)
        token_scroll = tk.Scrollbar(token_frame, command=self.token_list.yview)
        self.token_list.config(yscrollcommand=token_scroll.set)
        self.token_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        token_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        adj_frame = tk.Frame(pipeline_frame)
        adj_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.adj_list = tk.Listbox(adj_frame, width=40)
        adj_scroll = tk.Scrollbar(adj_frame, command=self.adj_list.yview)
        self.adj_list.config(yscrollcommand=adj_scroll.set)
        self.adj_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        adj_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        try:  # Matplotlib import can fail on systems without the backend
            import matplotlib.pyplot as plt
        except Exception as exc:  # pragma: no cover - optional dependency
            raise RuntimeError(
                "Matplotlib is required for PipelineGUI. Install with 'pip install hlsf_module[visualization]'"
            ) from exc

        self._plt = plt
        self._Polygon = Polygon
        self._fig, self._ax = plt.subplots()
        self._ax.set_aspect("equal")
        canvas = FigureCanvasTkAgg(self._fig, master=self._root)
        canvas.get_tk_widget().pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self._canvas = canvas

        # --- run pipeline -----------------------------------------------------------
        tokens = tokenize_text_fft(text, vocab_path=vocab_path)
        adj = expand_adjacency_sync(tokens)
        mapper = TensorMapper()
        mapper.update(tokens)
        state = mapper.to_hlsf()

        bands = sorted(mapper.graph)
        band_lookup = {b: i for i, b in enumerate(bands)}
        vocab = Vocab()
        self._token_ids: list[int] = []
        self._token_to_tri: dict[int, int] = {}

        for t in tokens:
            char = ""
            try:
                mod, code = vocab.decode(t.id)
                if mod == "text":
                    char = f" '{chr(code)}'"
            except (KeyError, ValueError):  # pragma: no cover - vocab may be empty
                pass
            band = t.feat.get("band", "")
            weight = t.w if t.w else t.feat.get("mag", 0.0)
            phase = t.feat.get("phase", t.feat.get("dphi", 0.0))
            centroid = t.feat.get("centroid", 0.0)
            self.token_list.insert(
                tk.END,
                f"{t.id}{char} b:{band} w:{weight:.2f} p:{phase:.2f} c:{centroid:.2f}",
            )
            self._token_ids.append(t.id)
            b = mapper._id_to_band[(t.mod, t.id)]
            self._token_to_tri[t.id] = band_lookup[b]

        for tid, neigh in adj.items():
            self.adj_list.insert(tk.END, f"{tid}: {neigh}")

        self._patches: list[Polygon] = []
        for tri in state.triangles:
            patch = self._Polygon(tri, closed=True, edgecolor="black", facecolor="none")
            self._ax.add_patch(patch)
            self._patches.append(patch)
        self._canvas.draw()

        self.token_list.bind("<<ListboxSelect>>", self._on_select)

    # ------------------------------------------------------------------
    def _on_select(self, _event: object) -> None:
        sel = self.token_list.curselection()
        if not sel:
            return
        token_id = self._token_ids[sel[0]]
        tri_idx = self._token_to_tri.get(token_id)
        if tri_idx is None:
            return
        for idx, patch in enumerate(self._patches):
            if idx == tri_idx:
                patch.set_edgecolor("red")
                patch.set_linewidth(2.0)
            else:
                patch.set_edgecolor("black")
                patch.set_linewidth(1.0)
        self._canvas.draw_idle()

    def run(self) -> None:  # pragma: no cover - GUI loop
        """Enter the Tk main loop."""

        self._root.mainloop()


def _parse_args() -> argparse.Namespace:
    """Parse command-line arguments for the polygon viewer."""

    parser = argparse.ArgumentParser(description="Render replicated polygons")
    parser.add_argument(
        "--center",
        type=float,
        nargs=2,
        default=(0.0, 0.0),
        metavar=("X", "Y"),
        help="centre of the polygon",
    )
    parser.add_argument("--radius", type=float, default=1.0, help="radius of the polygon")
    parser.add_argument("--sides", type=int, default=3, help="number of sides")
    parser.add_argument("--levels", type=int, default=1, help="replication levels")
    parser.add_argument(
        "--no-animate",
        action="store_true",
        help="disable rotation animation",
    )
    return parser.parse_args()


def main() -> None:
    """Entry point for ``python -m hlsf_module.visualization``."""

    args = _parse_args()
    gui = PolygonGUI(
        tuple(args.center),
        args.radius,
        args.sides,
        args.levels,
        is_rotation_animation_running=not args.no_animate,
    )
    gui.run()


if __name__ == "__main__":  # pragma: no cover - CLI integration
    main()
