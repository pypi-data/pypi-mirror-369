from __future__ import annotations

"""Utilities for resonance harmonic mode band generation and prime frequencies."""

from typing import List, Tuple
import math


def powerlaw_bands(sr: int, n_fft: int, n_bands: int, power: float = 2.0) -> List[float]:
    """Return band edges spaced by a simple power law.

    The distribution concentrates more bands at lower frequencies for
    ``power > 1``.
    """
    f_min = sr / n_fft
    f_max = sr / 2
    span = f_max - f_min
    return [f_min + span * ((i / n_bands) ** power) for i in range(n_bands + 1)]


def prime_frequencies(sr: int, n_fft: int) -> Tuple[List[int], List[float]]:
    """Compute frequencies for all FFT bins corresponding to prime indices.

    Returns a tuple of the prime indices and the corresponding frequencies.
    """
    bin_hz = sr / n_fft
    max_bin = n_fft // 2
    primes: List[int] = []
    for n in range(2, max_bin + 1):
        is_prime = True
        limit = int(math.sqrt(n)) + 1
        for p in range(2, limit):
            if n % p == 0:
                is_prime = False
                break
        if is_prime:
            primes.append(n)
    freqs = [p * bin_hz for p in primes]
    return primes, freqs
