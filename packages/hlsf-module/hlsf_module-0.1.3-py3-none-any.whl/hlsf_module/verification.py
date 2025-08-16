"""Inverse synthesis and verification utilities."""
from __future__ import annotations

from typing import Iterable, List
import math

from .fft_tokenizer import Token


class FFTResynthesizer:
    """Reconstruct time-domain frames from :class:`~fft_tokenizer.Token` objects."""

    def __init__(
        self,
        sr: int,
        n_fft: int = 2048,
        n_bands: int = 64,
        banding: str = "log",
    ) -> None:
        self.sr = sr
        self.n_fft = n_fft
        self.n_bands = n_bands
        f_min = sr / n_fft
        f_max = sr / 2
        if banding == "log":
            log_min = math.log10(f_min)
            log_max = math.log10(f_max)
            step = (log_max - log_min) / n_bands
            self._edges = [10 ** (log_min + i * step) for i in range(n_bands + 1)]
        else:
            step = (f_max - f_min) / n_bands
            self._edges = [f_min + i * step for i in range(n_bands + 1)]
        self._phase = [0.0] * n_bands

    def _irfft(self, spec: List[complex]) -> List[float]:
        """Naive inverse real FFT for ``spec`` of length ``n_fft//2 + 1``."""
        N = self.n_fft
        full = [0j] * N
        full[: len(spec)] = spec
        for k in range(1, len(spec) - 1):
            full[N - k] = spec[k].conjugate()
        out: List[float] = []
        for n in range(N):
            s = 0j
            for k, c in enumerate(full):
                angle = 2 * math.pi * k * n / N
                s += c * complex(math.cos(angle), math.sin(angle))
            out.append(s.real / N)
        return out

    def step(self, tokens: Iterable[Token]) -> List[float]:
        """Inverse-transform ``tokens`` to a synthesised frame."""
        spec = [0j] * (self.n_fft // 2 + 1)
        for tok in tokens:
            if not (0 <= tok.band < self.n_bands):
                continue
            self._phase[tok.band] += tok.dphi
            phase = self._phase[tok.band]
            lo, hi = self._edges[tok.band], self._edges[tok.band + 1]
            k_lo = int(lo * self.n_fft / self.sr)
            k_hi = int(hi * self.n_fft / self.sr)
            for k in range(k_lo, min(k_hi, len(spec))):
                spec[k] = complex(tok.mag * math.cos(phase), tok.mag * math.sin(phase))
        return self._irfft(spec)


def residual(a: Iterable[float], b: Iterable[float]) -> float:
    """Return mean squared error between signals ``a`` and ``b``."""
    diff = [(x - y) ** 2 for x, y in zip(a, b)]
    return sum(diff) / len(diff) if diff else 0.0


class SynthVerifier:
    """Simple API exposing synthesis and residual computation."""

    def __init__(self, sr: int, n_fft: int, n_bands: int, banding: str = "log") -> None:
        self._synth = FFTResynthesizer(sr, n_fft=n_fft, n_bands=n_bands, banding=banding)

    def synthesize(self, tokens: Iterable[Token]) -> List[float]:
        return self._synth.step(tokens)

    def compare(self, frame: Iterable[float], tokens: Iterable[Token]) -> float:
        recon = self._synth.step(tokens)
        return residual(frame, recon)
