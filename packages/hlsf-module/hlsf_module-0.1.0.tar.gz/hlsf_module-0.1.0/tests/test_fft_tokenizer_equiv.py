import math
from typing import List
from itertools import product
import cmath

import pytest

from hlsf_module.fft_tokenizer import FFTTokenizer, Token, _rfft, _nd_dft


def reference_step(tok: FFTTokenizer, frame: List[float]) -> List[Token]:
    if tok.dims == 1:
        spec_list = _rfft(frame, tok.n_fft[0])
        spec = {(k,): c for k, c in enumerate(spec_list)}
    else:
        spec = _nd_dft(frame, tok.n_fft)
    tokens: List[Token] = []
    band_ranges = [range(n) for n in tok.n_bands]
    total_energy = sum(abs(c) ** 2 for c in spec.values()) or 1.0
    for bands in product(*band_ranges):
        mags: List[float] = []
        phs: List[float] = []
        freqs: List[float] = []
        for k, c in spec.items():
            include = True
            for d in range(tok.dims):
                freq = tok.sr[d] * k[d] / tok.n_fft[d]
                lo, hi = tok._edges[d][bands[d]], tok._edges[d][bands[d] + 1]
                if not (lo <= freq < hi):
                    include = False
                    break
            if include:
                mags.append(abs(c))
                phs.append(cmath.phase(c))
                freqs.append(freq)
        total_mag = sum(mags)
        if not mags or total_mag == 0.0:
            continue
        mag = total_mag / len(mags)
        peak_mag = max(mags)
        centroid = sum(f * m for f, m in zip(freqs, mags)) / total_mag
        bandwidth = math.sqrt(
            sum(((f - centroid) ** 2) * m for f, m in zip(freqs, mags)) / total_mag
        )
        band_energy = sum(m * m for m in mags)
        coherence = band_energy / total_energy
        phase = sum(phs) / len(phs)
        flat = tok._flat_index(bands)
        prev = tok._prev_phase.get(flat, 0.0)
        dphi = phase - prev
        tok._prev_phase[flat] = phase
        mods = {}
        for d in range(tok.dims):
            lo, hi = tok._edges[d][bands[d]], tok._edges[d][bands[d] + 1]
            center = (lo + hi) / 2
            mel = 2595 * math.log10(1 + center / 700)
            mods[f"mel{d}"] = mel
        mods.update(tok._calc_extra_features(flat, bands, centroid, phase))
        tokens.append(
            Token(
                tok._t,
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
    tok._t += 1
    return tokens


def _compare_tokens(a: List[Token], b: List[Token]) -> None:
    assert len(a) == len(b)
    for t1, t2 in zip(a, b):
        assert t1.band == t2.band
        assert t1.bands == t2.bands
        for attr in (
            "mag",
            "dphi",
            "peak_mag",
            "centroid",
            "bandwidth",
            "coherence",
        ):
            v1 = getattr(t1, attr)
            v2 = getattr(t2, attr)
            if v1 is None and v2 is None:
                continue
            assert v1 == pytest.approx(v2, rel=1e-6, abs=1e-6)


def test_vectorized_step_equivalent():
    sr, n_fft, hop, bands = 48000, 128, 64, 16
    freq = 440
    frame = [math.sin(2 * math.pi * freq * n / sr) for n in range(n_fft)]

    tok_vec = FFTTokenizer(sr=sr, n_fft=n_fft, hop=hop, n_bands=bands)
    tok_ref = FFTTokenizer(sr=sr, n_fft=n_fft, hop=hop, n_bands=bands)

    ref_tokens1 = reference_step(tok_ref, frame)
    vec_tokens1 = tok_vec.step(frame)
    _compare_tokens(vec_tokens1, ref_tokens1)

    # second frame for phase continuity
    frame2 = [math.sin(2 * math.pi * freq * (n + hop) / sr) for n in range(n_fft)]
    ref_tokens2 = reference_step(tok_ref, frame2)
    vec_tokens2 = tok_vec.step(frame2)
    _compare_tokens(vec_tokens2, ref_tokens2)
