from __future__ import annotations

"""Audio encoder emitting :class:`~symbols.schema.SymbolToken` objects."""

from pathlib import Path
from typing import List, Sequence

from .fft_tokenizer import FFTTokenizer, Token
from .symbols.schema import SymbolToken
from .symbols.vocab import Vocab
from .resonator import SymbolResonator
from .rh_utils import powerlaw_bands, prime_frequencies


class AudioEncoder:
    def __init__(
        self,
        sr: int = 48000,
        n_fft: int = 2048,
        hop: int = 512,
        bands: int = 64,
        banding: str = "log",
        edges: Sequence[float] | None = None,
        vocab: Vocab | None = None,
        vocab_path: str | None = None,
        resonator: SymbolResonator | None = None,
        *,
        rh_mode: bool = False,
        use_gpu: bool = False,
        device: str | None = None,
    ) -> None:
        self._primes: List[int] | None = None
        self._prime_freqs: List[float] | None = None
        edge_arg = None
        if rh_mode:
            edge_list = powerlaw_bands(sr, n_fft, bands)
            edge_arg = [edge_list]
            self._primes, self._prime_freqs = prime_frequencies(sr, n_fft)
        elif edges is not None:
            edge_arg = [list(edges)]
        self.tokenizer = FFTTokenizer(
            sr=sr,
            n_fft=n_fft,
            hop=hop,
            n_bands=bands,
            banding=banding,
            edges=edge_arg,
            use_gpu=use_gpu,
            device=device,
        )
        if vocab_path:
            vc = Vocab.load(vocab_path) if Path(vocab_path).exists() else (vocab or Vocab())
        else:
            vc = vocab or Vocab()
        self.vocab = vc
        self._vocab_path = vocab_path
        if resonator is not None:
            self.resonator = resonator
        elif use_gpu:
            from os import getenv

            self.resonator = SymbolResonator(
                use_gpu=True, device=device, backend=getenv("HLSF_GPU_BACKEND")
            )
        else:
            self.resonator = None

    def step(self, frame: List[float]) -> List[SymbolToken]:
        raw: List[Token] = self.tokenizer.step(frame)
        out: List[SymbolToken] = []
        for t in raw:
            tok_id = self.vocab.id("audio", t.band)
            feat = {"mag": t.mag, "dphi": t.dphi, "band": t.band}
            if self._prime_freqs is not None and t.centroid is not None:
                idx = min(
                    range(len(self._prime_freqs)),
                    key=lambda i: abs(self._prime_freqs[i] - t.centroid),
                )
                feat["prime_channel"] = self._primes[idx]
            if t.peak_mag is not None:
                feat["peak_mag"] = t.peak_mag
            if t.centroid is not None:
                feat["centroid"] = t.centroid
            if t.bandwidth is not None:
                feat["bandwidth"] = t.bandwidth
            if t.coherence is not None:
                feat["coherence"] = t.coherence
            if t.bands is not None:
                feat["bands"] = list(t.bands)
            feat.update(self.tokenizer.extra_features(t))
            if t.mods:
                feat.update(t.mods)
            tok = SymbolToken(t=t.t_idx, id=tok_id, mod="audio", feat=feat, w=int(t.mag))
            if self.resonator is not None:
                tok.feat["res"] = self.resonator.score(tok)
            out.append(tok)

        if self._vocab_path:
            self.vocab.save(self._vocab_path)
        return out
