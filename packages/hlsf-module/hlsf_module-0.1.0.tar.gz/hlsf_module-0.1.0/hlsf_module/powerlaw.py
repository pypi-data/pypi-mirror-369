from __future__ import annotations

from typing import List


def powerlaw_bands(sr: int, n_fft: int, n_bands: int, *, exponent: float = 1.0) -> List[float]:
    """Return ``n_bands + 1`` frequency edges spaced by a power law.

    The lowest edge corresponds to ``sr / n_fft`` (the minimum resolvable
    frequency) and the highest edge reaches the Nyquist limit ``sr / 2``.
    Increasing ``exponent`` concentrates more bands at lower frequencies.
    """
    if n_bands <= 0:
        raise ValueError("n_bands must be positive")
    if exponent <= 0:
        raise ValueError("exponent must be positive")
    f_min = sr / n_fft
    f_max = sr / 2
    span = f_max - f_min
    edges = [f_min + span * (i / n_bands) ** exponent for i in range(n_bands + 1)]
    edges[-1] = f_max
    return edges
