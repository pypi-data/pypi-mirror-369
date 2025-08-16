from __future__ import annotations

"""Encode symbol IDs across multiple bands with sentinel markers and phase flags."""

from typing import List, Sequence, Tuple
import math

BandPhase = Tuple[int, float]


def encode_symbol(
    symbol_id: int,
    *,
    bits: int = 8,
    band_offset: int = 0,
    sentinel_lo: int = 62,
    sentinel_hi: int = 63,
) -> List[BandPhase]:
    """Encode ``symbol_id`` into ``bits`` bands with sentinels and phase flags.

    The integer is expanded into binary with ``bits`` least-significant bits.
    Each bit is mapped to a unique band starting at ``band_offset``.  A phase of
    ``0`` encodes bit ``0`` while ``pi`` encodes ``1``.  Two sentinel bands are
    inserted at the beginning and end to delimit the sequence.
    """

    seq: List[BandPhase] = [(sentinel_lo, 0.0)]
    for i in range(bits):
        band = band_offset + i
        bit = (symbol_id >> i) & 1
        phase = 0.0 if bit == 0 else math.pi
        seq.append((band, phase))
    seq.append((sentinel_hi, 0.0))
    return seq


def decode_symbol(
    seq: Sequence[BandPhase],
    *,
    bits: int = 8,
    band_offset: int = 0,
    sentinel_lo: int = 62,
    sentinel_hi: int = 63,
) -> int:
    """Decode a band/phase sequence back to the original integer."""

    if len(seq) != bits + 2:
        raise ValueError("unexpected sequence length")
    if seq[0][0] != sentinel_lo or seq[-1][0] != sentinel_hi:
        raise ValueError("missing sentinel bands")
    value = 0
    for i, (_, phase) in enumerate(seq[1:-1]):
        bit = 1 if abs(phase - math.pi) < 1e-6 else 0
        value |= bit << i
    return value
