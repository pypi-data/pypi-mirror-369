from __future__ import annotations

"""Simple Tkinter frame hosting pipeline controls."""

import json
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox
from typing import Any, Dict

from .multimodal_out import snapshot_state
from .tensor_mapper import HLSFState


class PipelineFrame(tk.Frame):
    """Minimal frame exposing save/load controls for HLSF snapshots."""

    def __init__(self, master: tk.Misc | None = None, **kwargs: Any) -> None:
        super().__init__(master, **kwargs)
        self.hlsf_state = HLSFState([], [])
        self.viewer = None  # viewer implementing ``update``

        btn_save = tk.Button(self, text="Save HLSF…", command=self._save_hlsf)
        btn_load = tk.Button(self, text="Load HLSF…", command=self._load_hlsf)
        btn_save.pack(side=tk.LEFT, padx=5, pady=5)
        btn_load.pack(side=tk.LEFT, padx=5, pady=5)

        self.token_box = tk.Text(self, height=4)
        self.token_box.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    def set_viewer(self, viewer: Any) -> None:
        """Attach a viewer implementing ``update`` to mirror state changes."""

        self.viewer = viewer

    def update_state(self, state: HLSFState) -> None:
        """Replace current state and refresh displays."""

        self.hlsf_state = state
        if self.viewer:
            self.viewer.update(state)
        self.token_box.delete("1.0", tk.END)
        if state.metrics:
            self.token_box.insert("end", json.dumps(state.metrics))

    # ------------------------------------------------------------------
    # Button callbacks
    # ------------------------------------------------------------------
    def _save_hlsf(self) -> None:
        path = filedialog.asksaveasfilename(
            defaultextension=".json", filetypes=[("JSON", "*.json")]
        )
        if not path:
            return
        try:
            snapshot_state(path, self.hlsf_state)
        except Exception as exc:  # pragma: no cover - UI path
            messagebox.showerror("Save Error", str(exc))

    def _load_hlsf(self) -> None:
        path = filedialog.askopenfilename(filetypes=[("JSON", "*.json")])
        if not path:
            return
        try:
            data: Dict[str, Any] = json.loads(Path(path).read_text())
            state = HLSFState.from_hlsf(data)
        except Exception as exc:  # pragma: no cover - UI path
            messagebox.showerror("Load Error", str(exc))
            return
        self.update_state(state)
