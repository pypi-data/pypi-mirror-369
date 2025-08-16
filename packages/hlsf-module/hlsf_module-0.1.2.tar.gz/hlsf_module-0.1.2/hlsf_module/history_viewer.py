from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from typing import Any, Dict, List

from .tensor_mapper import HLSFState

try:  # Optional dependency
    from .visualization import HLSFViewer
except ImportError:  # pragma: no cover - missing matplotlib
    HLSFViewer = None  # type: ignore


class TokenHistoryViewer:
    """Simple Tk viewer for navigating token history snapshots."""

    def __init__(self, history: List[Dict[str, Any]]):
        self._history = history
        self._root = tk.Tk()
        self._root.title("Token History")

        self._list = tk.Listbox(self._root, exportselection=False)
        self._list.pack(side=tk.LEFT, fill=tk.Y)
        for snap in history:
            self._list.insert(tk.END, snap.get("name", "step"))
        self._list.bind("<<ListboxSelect>>", self._on_select)

        right = ttk.Frame(self._root)
        right.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        self._tokens = tk.Text(right, height=10)
        self._tokens.pack(fill=tk.BOTH, expand=True)
        self._adj = tk.Text(right, height=10)
        self._adj.pack(fill=tk.BOTH, expand=True)

        self._viewer = HLSFViewer() if HLSFViewer is not None else None

        if history:
            self._list.selection_set(0)
            self._on_select()

    def _on_select(self, _event: Any | None = None) -> None:
        if not self._list.curselection():
            return
        idx = self._list.curselection()[0]
        snap = self._history[idx]
        self._tokens.delete("1.0", tk.END)
        token_lines = [str(t) for t in snap.get("tokens", [])]
        self._tokens.insert(tk.END, "\n".join(token_lines))
        self._adj.delete("1.0", tk.END)
        adj = snap.get("adjacency", {})
        for key, val in adj.items():
            self._adj.insert(tk.END, f"{key}: {val}\n")
        if self._viewer and isinstance(snap.get("state"), HLSFState):
            self._viewer.update(snap["state"])

    def show(self) -> None:
        """Block until the viewer window is closed."""
        self._root.mainloop()
