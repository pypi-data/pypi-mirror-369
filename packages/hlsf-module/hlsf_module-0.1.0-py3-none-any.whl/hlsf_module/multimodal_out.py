"""Utilities for exporting pipeline state."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Iterable, List
import math

from .tensor_mapper import HLSFState


def snapshot_state(path: str | Path, state: HLSFState) -> None:
    obj: Dict[str, Any] = {
        "triangles": state.triangles,
        "colors": state.colors,
        "active_motif": state.active_motif,
        "metrics": state.metrics or {},
        "resonance_metrics": state.resonance_metrics or {},
        "prototypes": state.prototypes or [],
        "proof_log": state.proof_log or [],

    }
    Path(path).write_text(json.dumps(obj))


def resynth_bands(bands: Iterable[float], duration: float, sr: int = 48000) -> List[float]:
    t = [i / sr for i in range(int(sr * duration))]
    audio = [0.0 for _ in t]
    for i, mag in enumerate(bands):
        freq = 20 * (2 ** i)
        for n, tt in enumerate(t):
            audio[n] += mag * math.sin(2 * math.pi * freq * tt)
    return audio

