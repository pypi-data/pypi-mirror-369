"""Minimal FFT tokenizer without external dependencies.

The tokenizer tracks band magnitudes as well as the *unwrapped* phase
delta between consecutive frames.  Phase continuity per band is preserved
by maintaining a running accumulator that unwraps the raw angles before
computing the delta.  This improves downstream modules that rely on
``dphi`` for deterministic rotation or modulation rules.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Tuple
import cmath
import math
from itertools import product
import logging

from . import fft_backends as _fb

# Resolve backend at import time and expose helpers for tests
_fb.select_backend()
_rfft = _fb.rfft
_nd_dft = _fb.nd_fft
_nd_dft_python = _fb.nd_dft_python

try:  # pragma: no cover - optional optimisation
    from numba import njit
    from numba.typed import List as NumbaList
except Exception:  # pragma: no cover
    njit = None
    NumbaList = None

try:
    import torch as _torch  # noqa: F401
except Exception:  # pragma: no cover
    _torch = None

try:  # pragma: no cover
    import numpy as _np
except Exception:  # pragma: no cover
    _np = None

logger = logging.getLogger(__name__)


def _is_prime(n: int) -> bool:
    """Return ``True`` if ``n`` is a prime number."""
    if n < 2:
        return False
    for i in range(2, int(math.sqrt(n)) + 1):
        if n % i == 0:
            return False
    return True


def _lucas_bucket(n: int) -> int:
    """Return the smallest Lucas number greater than or equal to ``n``."""
    a, b = 2, 1
    if n <= 2:
        return 2
    while b < n:
        a, b = b, a + b
    return b


if njit is not None:  # pragma: no cover - heavy optimisation path

    @njit
    def _numba_band_stats(real, imag, freqs, band_bins, total_energy):
        n_bands = len(band_bins)
        out_mag = [0.0] * n_bands
        out_peak = [0.0] * n_bands
        out_cent = [0.0] * n_bands
        out_bw = [0.0] * n_bands
        out_phase = [0.0] * n_bands
        out_coh = [0.0] * n_bands
        for b in range(n_bands):
            bins = band_bins[b]
            total_mag = 0.0
            cnt = 0
            peak = 0.0
            cent = 0.0
            for idx in bins:
                r = real[idx]
                im = imag[idx]
                m = math.sqrt(r * r + im * im)
                total_mag += m
                if m > peak:
                    peak = m
                cent += freqs[idx] * m
                cnt += 1
            if cnt == 0 or total_mag == 0.0:
                continue
            cent = cent / total_mag
            var = 0.0
            energy = 0.0
            ph = 0.0
            for idx in bins:
                r = real[idx]
                im = imag[idx]
                m = math.sqrt(r * r + im * im)
                f = freqs[idx]
                var += (f - cent) ** 2 * m
                energy += m * m
                ph += math.atan2(im, r)
            out_mag[b] = total_mag / cnt
            out_peak[b] = peak
            out_cent[b] = cent
            out_bw[b] = math.sqrt(var / total_mag)
            out_phase[b] = ph / cnt
            out_coh[b] = energy / total_energy
        return out_mag, out_peak, out_cent, out_bw, out_phase, out_coh


@dataclass
class Token:
    t_idx: int
    band: int
    mag: float
    dphi: float
    peak_mag: float | None = None
    centroid: float | None = None
    bandwidth: float | None = None
    coherence: float | None = None
    bands: Tuple[int, ...] | None = None
    mods: Dict[str, float] | None = None


class FFTTokenizer:
    def __init__(
        self,
        sr: int | Tuple[int, ...],
        n_fft: int | Tuple[int, ...] = 2048,
        hop: int | Tuple[int, ...] = 512,
        banding: str = "log",
        n_bands: int | Tuple[int, ...] = 64,
        edges: List[List[float]] | None = None,
        *,
        use_gpu: bool = False,
        device: str | None = None,
        backend: str | None = None,
    ) -> None:
        _fb.select_backend(backend if use_gpu else None, use_gpu=use_gpu)
        self.use_gpu = use_gpu
        self.device = device
        self.sr = (sr,) if isinstance(sr, int) else tuple(sr)
        self.n_fft = (n_fft,) if isinstance(n_fft, int) else tuple(n_fft)
        self.hop = (hop,) if isinstance(hop, int) else tuple(hop)
        self.n_bands = (n_bands,) if isinstance(n_bands, int) else tuple(n_bands)
        self.dims = len(self.sr)
        if len(self.n_fft) != self.dims:
            self.n_fft = self.n_fft + (self.n_fft[-1],) * (self.dims - len(self.n_fft))
        if len(self.n_bands) != self.dims:
            self.n_bands = self.n_bands + (self.n_bands[-1],) * (
                self.dims - len(self.n_bands)
            )
        # pre-compute band edges per dimension
        self._edges: List[List[float]] = []
        for d in range(self.dims):
            sr_d = self.sr[d]
            n_fft_d = self.n_fft[d]
            nb_d = self.n_bands[d]
            if edges is not None:
                self._edges.append(list(edges[d if d < len(edges) else -1]))
                continue
            f_min = sr_d / n_fft_d
            f_max = sr_d / 2
            if banding == "log":
                log_min = math.log10(f_min)
                log_max = math.log10(f_max)
                step = (log_max - log_min) / nb_d
                ed = [10 ** (log_min + i * step) for i in range(nb_d + 1)]
            elif banding == "mel":
                mel_min = 2595 * math.log10(1 + f_min / 700)
                mel_max = 2595 * math.log10(1 + f_max / 700)
                step = (mel_max - mel_min) / nb_d
                ed = [
                    700 * (10 ** ((mel_min + i * step) / 2595) - 1)
                    for i in range(nb_d + 1)
                ]
            else:
                step = (f_max - f_min) / nb_d
                ed = [f_min + i * step for i in range(nb_d + 1)]
            self._edges.append(ed)

        self._prev_phase: Dict[int, float] = {}
        self._t = 0

        # ------------------------------------------------------------------
        # Pre-compute FFT bin indexing and band masks
        # ------------------------------------------------------------------
        k_ranges = [range(self.n_fft[d] // 2 + 1) for d in range(self.dims)]
        self._bin_tuples = list(product(*k_ranges))
        self._band_indices = list(product(*[range(n) for n in self.n_bands]))
        self._bin_freqs_last = [
            self.sr[-1] * k[-1] / self.n_fft[-1] for k in self._bin_tuples
        ]
        self._band_bins: List[List[int]] = []
        for bands in self._band_indices:
            inds: List[int] = []
            for i, k in enumerate(self._bin_tuples):
                include = True
                for d in range(self.dims):
                    freq = self.sr[d] * k[d] / self.n_fft[d]
                    lo, hi = self._edges[d][bands[d]], self._edges[d][bands[d] + 1]
                    if not (lo <= freq < hi):
                        include = False
                        break
                if include:
                    inds.append(i)
            self._band_bins.append(inds)

        self._mask_np = None
        self._freqs_np = None
        self._mask_torch = None
        self._freqs_torch = None
        self._band_bins_nb = None
        self._freqs_nb = None

        self._use_torch = (
            (_torch is not None) and bool(use_gpu) and _torch.cuda.is_available()
        )
        self._use_numpy = (_np is not None) and not self._use_torch
        self._device = device or ("cuda" if self._use_torch else "cpu")
        self._use_numba = (
            not self._use_torch and not self._use_numpy and njit is not None
        )
        if self._use_torch:
            mask = _torch.zeros(
                (len(self._band_bins), len(self._bin_tuples)),
                dtype=_torch.bool,
                device=self._device,
            )
            for i, inds in enumerate(self._band_bins):
                mask[i, inds] = True
            self._mask_torch = mask
            self._freqs_torch = _torch.tensor(
                self._bin_freqs_last, dtype=_torch.float32, device=self._device
            )
        elif self._use_numpy:
            self._mask_np = _np.zeros(
                (len(self._band_bins), len(self._bin_tuples)), dtype=bool
            )
            for i, inds in enumerate(self._band_bins):
                self._mask_np[i, inds] = True
            self._freqs_np = _np.array(self._bin_freqs_last, dtype=float)
        elif self._use_numba and NumbaList is not None:
            self._band_bins_nb = NumbaList()
            for inds in self._band_bins:
                arr = NumbaList()
                for j in inds:
                    arr.append(j)
                self._band_bins_nb.append(arr)
            self._freqs_nb = NumbaList()
            for f in self._bin_freqs_last:
                self._freqs_nb.append(f)

    def _flat_index(self, bands: Tuple[int, ...]) -> int:
        idx = 0
        for b, nb in zip(bands, self.n_bands):
            idx = idx * nb + b
        return idx

    def _calc_extra_features(
        self, flat: int, bands: Tuple[int, ...], centroid: float, phase: float
    ) -> Dict[str, float]:
        centers = [
            (self._edges[d][bands[d]] + self._edges[d][bands[d] + 1]) / 2
            for d in range(self.dims)
        ]
        freq_center = sum(centers) / len(centers)
        base = self.sr[0] / self.n_fft[0] if self.n_fft[0] else 0.0
        harmonic_index = centroid / base if base else 0.0
        k_dev = centroid - freq_center
        feats: Dict[str, float] = {
            "freq_center": freq_center,
            "prime_channel": 1.0 if _is_prime(flat) else 0.0,
            "harmonic_index": harmonic_index,
            "lucas_bucket": float(_lucas_bucket(flat)),
            "phase0": phase,
        }
        if k_dev:
            feats["K_dev"] = k_dev
        return feats

    def extra_features(self, token: Token) -> Dict[str, float]:
        """Compute derived features for ``token``.

        This is used when converting :class:`Token` instances into
        :class:`~symbols.schema.SymbolToken` objects.
        """

        phase = (
            token.mods.get("phase0")
            if token.mods and "phase0" in token.mods
            else token.dphi
        )
        centroid = token.centroid if token.centroid is not None else 0.0
        bands = token.bands if token.bands is not None else (token.band,)
        return self._calc_extra_features(token.band, bands, centroid, phase)

    def step(self, frame: List) -> List[Token]:
        """Tokenize ``frame`` returning a list of :class:`Token` objects."""

        if self.dims == 1:
            spec_vals = _rfft(frame, self.n_fft[0])
        else:
            spec = _nd_dft(frame, self.n_fft)
            spec_vals = [spec[k] for k in self._bin_tuples]

        tokens: List[Token] = []
        if self._use_torch and self._mask_torch is not None:
            spec_t = _torch.tensor(
                spec_vals, dtype=_torch.complex64, device=self._device
            )
            mags = spec_t.abs()
            phs = _torch.angle(spec_t)
            energy = mags**2
            total_energy = energy.sum().item() or 1.0
            mask = self._mask_torch
            masked_mags = mask * mags.unsqueeze(0)
            total_mag = masked_mags.sum(dim=1)
            counts = mask.sum(dim=1)
            valid = (counts > 0) & (total_mag > 0)
            if valid.any():
                mag = total_mag / counts
                peak_mag = (mask * mags.unsqueeze(0)).max(dim=1).values
                centroid = (masked_mags * self._freqs_torch).sum(dim=1) / total_mag
                diff = self._freqs_torch - centroid.unsqueeze(1)
                bandwidth = ((diff**2) * masked_mags).sum(dim=1) / total_mag
                bandwidth = bandwidth.sqrt()
                band_energy = (mask * energy.unsqueeze(0)).sum(dim=1)
                coherence = band_energy / total_energy
                phase = (mask * phs.unsqueeze(0)).sum(dim=1) / counts
                for i, bands in enumerate(self._band_indices):
                    if not valid[i]:
                        continue
                    flat = self._flat_index(bands)
                    ph = phase[i].item()
                    prev = self._prev_phase.get(flat, 0.0)
                    dphi = ph - prev
                    self._prev_phase[flat] = ph
                    mods: Dict[str, float] = {}
                    for d in range(self.dims):
                        lo, hi = self._edges[d][bands[d]], self._edges[d][bands[d] + 1]
                        center = (lo + hi) / 2
                        mel = 2595 * math.log10(1 + center / 700)
                        mods[f"mel{d}"] = mel
                    mods.update(
                        self._calc_extra_features(flat, bands, centroid[i].item(), ph)
                    )
                    tokens.append(
                        Token(
                            self._t,
                            flat,
                            mag[i].item(),
                            dphi,
                            peak_mag=peak_mag[i].item(),
                            centroid=centroid[i].item(),
                            bandwidth=bandwidth[i].item(),
                            coherence=coherence[i].item(),
                            bands=bands,
                            mods=mods,
                        )
                    )
            self._t += 1
            return tokens

        if self._use_numpy and self._mask_np is not None:
            spec_arr = _np.array(spec_vals, dtype=_np.complex128)
            mags = _np.abs(spec_arr)
            phs = _np.angle(spec_arr)
            energy = mags**2
            total_energy = energy.sum() or 1.0
            mask = self._mask_np
            masked_mags = mask * mags
            total_mag = masked_mags.sum(axis=1)
            counts = mask.sum(axis=1)
            valid = (counts > 0) & (total_mag > 0)
            if valid.any():
                mag = _np.divide(
                    total_mag, counts, out=_np.zeros_like(total_mag), where=counts > 0
                )
                peak_mag = _np.where(mask, mags, 0.0).max(axis=1)
                centroid = _np.divide(
                    (masked_mags * self._freqs_np).sum(axis=1),
                    total_mag,
                    out=_np.zeros_like(total_mag),
                    where=total_mag > 0,
                )
                diff = self._freqs_np - centroid[:, None]
                bandwidth = _np.sqrt(
                    _np.divide(
                        ((diff**2) * masked_mags).sum(axis=1),
                        total_mag,
                        out=_np.zeros_like(total_mag),
                        where=total_mag > 0,
                    )
                )
                band_energy = (mask * energy).sum(axis=1)
                coherence = band_energy / total_energy
                phase = _np.divide(
                    (mask * phs).sum(axis=1),
                    counts,
                    out=_np.zeros_like(counts, dtype=float),
                    where=counts > 0,
                )
                for i, bands in enumerate(self._band_indices):
                    if not valid[i]:
                        continue
                    flat = self._flat_index(bands)
                    ph = float(phase[i])
                    prev = self._prev_phase.get(flat, 0.0)
                    dphi = ph - prev
                    self._prev_phase[flat] = ph
                    mods: Dict[str, float] = {}
                    for d in range(self.dims):
                        lo, hi = self._edges[d][bands[d]], self._edges[d][bands[d] + 1]
                        center = (lo + hi) / 2
                        mel = 2595 * math.log10(1 + center / 700)
                        mods[f"mel{d}"] = mel
                    mods.update(
                        self._calc_extra_features(flat, bands, float(centroid[i]), ph)
                    )
                    tokens.append(
                        Token(
                            self._t,
                            flat,
                            float(mag[i]),
                            dphi,
                            peak_mag=float(peak_mag[i]),
                            centroid=float(centroid[i]),
                            bandwidth=float(bandwidth[i]),
                            coherence=float(coherence[i]),
                            bands=bands,
                            mods=mods,
                        )
                    )
            self._t += 1
            return tokens

        # Python/Numba fallback
        if self._use_numba and self._band_bins_nb is not None and njit is not None:
            real_list = NumbaList()
            imag_list = NumbaList()
            for c in spec_vals:
                real_list.append(float(c.real))
                imag_list.append(float(c.imag))
            total_energy = (
                sum(r * r + i * i for r, i in zip(real_list, imag_list)) or 1.0
            )
            mags_out, peaks_out, cent_out, bw_out, phase_out, coh_out = (
                _numba_band_stats(
                    real_list,
                    imag_list,
                    self._freqs_nb,
                    self._band_bins_nb,
                    total_energy,
                )
            )
            for i, bands in enumerate(self._band_indices):
                if not self._band_bins[i] or mags_out[i] == 0.0:
                    continue
                flat = self._flat_index(bands)
                ph = phase_out[i]
                prev = self._prev_phase.get(flat, 0.0)
                dphi = ph - prev
                self._prev_phase[flat] = ph
                mods: Dict[str, float] = {}
                for d in range(self.dims):
                    lo, hi = self._edges[d][bands[d]], self._edges[d][bands[d] + 1]
                    center = (lo + hi) / 2
                    mel = 2595 * math.log10(1 + center / 700)
                    mods[f"mel{d}"] = mel
                mods.update(self._calc_extra_features(flat, bands, cent_out[i], ph))
                tokens.append(
                    Token(
                        self._t,
                        flat,
                        mags_out[i],
                        dphi,
                        peak_mag=peaks_out[i],
                        centroid=cent_out[i],
                        bandwidth=bw_out[i],
                        coherence=coh_out[i],
                        bands=bands,
                        mods=mods,
                    )
                )
            self._t += 1
            return tokens

        mags = [abs(c) for c in spec_vals]
        phs = [cmath.phase(c) for c in spec_vals]
        energy = [m * m for m in mags]
        total_energy = sum(energy) or 1.0
        freqs = self._bin_freqs_last
        for i, bins in enumerate(self._band_bins):
            if not bins:
                continue
            total_mag = sum(mags[j] for j in bins)
            if total_mag == 0.0:
                continue
            mag = total_mag / len(bins)
            peak_mag = max(mags[j] for j in bins)
            centroid = sum(freqs[j] * mags[j] for j in bins) / total_mag
            bandwidth = math.sqrt(
                sum(((freqs[j] - centroid) ** 2) * mags[j] for j in bins) / total_mag
            )
            band_energy = sum(energy[j] for j in bins)
            coherence = band_energy / total_energy
            phase = sum(phs[j] for j in bins) / len(bins)
            bands = self._band_indices[i]
            flat = self._flat_index(bands)
            prev = self._prev_phase.get(flat, 0.0)
            dphi = phase - prev
            self._prev_phase[flat] = phase
            mods: Dict[str, float] = {}
            for d in range(self.dims):
                lo, hi = self._edges[d][bands[d]], self._edges[d][bands[d] + 1]
                center = (lo + hi) / 2
                mel = 2595 * math.log10(1 + center / 700)
                mods[f"mel{d}"] = mel
            mods.update(self._calc_extra_features(flat, bands, centroid, phase))
            tokens.append(
                Token(
                    self._t,
                    flat,
                    mag,
                    dphi,
                    peak_mag=peak_mag,
                    centroid=centroid,
                    bandwidth=bandwidth,
                    coherence=coherence,
                    bands=bands,
                    mods=mods,
                )
            )
        self._t += 1
        return tokens
