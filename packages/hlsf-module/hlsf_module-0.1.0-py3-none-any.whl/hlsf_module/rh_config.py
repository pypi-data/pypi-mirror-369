"""Configuration helpers and constants for simple analytic demos.

This module groups together a handful of numerical sequences and
constants used by the tests.  The intent is to keep the values in a
single location while also providing tiny helper utilities that operate
on them.

None of the helpers are meant to be fast – they simply provide clear and
predictable behaviour for small inputs.
"""
from __future__ import annotations

from math import pi
from typing import List, Sequence, Tuple

# --- basic frequency constants -------------------------------------------------

#: Fundamental frequency used by a number of toy calculations (A4).
f0_hz: float = 440.0

#: Angular frequency corresponding to :data:`f0_hz`.
omega_rad_s: float = 2.0 * pi * f0_hz

# --- numerical sequences -------------------------------------------------------

#: Coefficients ``(a, b)`` for a simple power‑law ``a * n**b`` model.
POWER_LAW_COEFFS: Tuple[float, float] = (1.0, -1.0)

#: Seed values for the Lucas sequence; the list is extended on demand.
LUCAS_SEQUENCE: List[int] = [2, 1, 3, 4, 7, 11, 18, 29, 47, 76]

#: Prime numbers used as frequency bands; extended as required.
PRIME_BANDS: List[int] = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29]

# --- additional constants ------------------------------------------------------

#: Generic scaling constant used by :func:`compute_K`.
k_target: float = 1.0

#: Phase offset added by :func:`compute_K`.
berry_phase: float = 0.0

# --- helper functions ----------------------------------------------------------

def powerlaw_bands(count: int,
                   *,
                   coeffs: Tuple[float, float] = POWER_LAW_COEFFS,
                   base_freq: float = f0_hz) -> List[float]:
    """Return ``count`` frequency bands following a power law.

    Each band ``n`` (1-indexed) is computed as ``base_freq * a * n**b``
    where ``(a, b)`` are the supplied power-law coefficients.
    ``count`` may be zero, in which case an empty list is returned.
    """

    if count < 0:
        raise ValueError("count must be non-negative")

    a, b = coeffs
    return [base_freq * a * (n ** b) for n in range(1, count + 1)]


def lucas_bucket(index: int) -> int:
    """Return the ``index``\ th Lucas number (1-indexed).

    The function maintains a small cache of previously computed numbers in
    :data:`LUCAS_SEQUENCE` and extends the list if necessary.
    """

    if index < 1:
        raise ValueError("index must be >= 1")

    while len(LUCAS_SEQUENCE) < index:
        LUCAS_SEQUENCE.append(LUCAS_SEQUENCE[-1] + LUCAS_SEQUENCE[-2])
    return LUCAS_SEQUENCE[index - 1]


def prime_channel(index: int) -> int:
    """Return the ``index``\ th prime number (1-indexed).

    A minimal incremental sieve is used which is perfectly adequate for
    the small indices exercised by the tests.  The list of known primes is
    stored in :data:`PRIME_BANDS` and extended on demand.
    """

    if index < 1:
        raise ValueError("index must be >= 1")

    candidate = PRIME_BANDS[-1] + 1
    while len(PRIME_BANDS) < index:
        for p in PRIME_BANDS:
            if candidate % p == 0:
                break
        else:
            PRIME_BANDS.append(candidate)
        candidate += 1
    return PRIME_BANDS[index - 1]


def compute_K(index: int,
              *,
              k0: float = k_target,
              berry: float = berry_phase) -> float:
    """Compute a toy ``K`` value coupling primes and Lucas numbers.

    The returned value uses the shared ``index`` for both sequences::

        K = k0 * prime_channel(index) / lucas_bucket(index) + berry

    Parameters
    ----------
    index:
        The position within the prime and Lucas sequences.
    k0:
        Scaling constant applied to the prime/Lucas ratio.
    berry:
        Phase offset added to the scaled ratio.
    """

    prime = prime_channel(index)
    lucas = lucas_bucket(index)
    return k0 * prime / lucas + berry

__all__ = [
    "f0_hz",
    "omega_rad_s",
    "POWER_LAW_COEFFS",
    "LUCAS_SEQUENCE",
    "PRIME_BANDS",
    "k_target",
    "berry_phase",
    "powerlaw_bands",
    "lucas_bucket",
    "prime_channel",
    "compute_K",
]
