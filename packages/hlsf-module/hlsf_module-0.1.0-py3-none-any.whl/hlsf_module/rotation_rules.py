"""Derive rotation angles for motifs.

The angles are based on the ``dphi`` values emitted by
``fft_tokenizer.FFTTokenizer`` which now maintains a per-band phase
accumulator and unwraps raw angles before differencing.  This ensures the
average ``dphi`` supplied here represents a continuous phase change that
can be converted directly into degrees.
"""
from __future__ import annotations

from typing import Dict


def for_motifs(stats: Dict[int, float]) -> Dict[int, float]:
    """Compute a rotation angle per band.

    ``stats`` is expected to map band -> average ``dphi``.  The return value
    is a mapping band -> angle in degrees.  This helper is deliberately
    minimal yet deterministic.
    """

    return {band: dphi * 180.0 / 3.141592653589793 for band, dphi in stats.items()}

