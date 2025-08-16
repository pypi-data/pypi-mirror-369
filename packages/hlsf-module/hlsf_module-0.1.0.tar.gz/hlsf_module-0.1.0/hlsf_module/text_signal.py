from __future__ import annotations

"""Helpers for representing text tokens as synthetic audio signals."""

from pathlib import Path
from typing import Iterable, List

from .fft_tokenizer import FFTTokenizer, Token
from .signal_io import SignalStream
from .symbols.schema import SymbolToken
from .symbols.vocab import Vocab
from .resonator import SymbolResonator


def text_to_signal_tokens(
    tokens: Iterable[str],
    sr: int = 48000,
    n_fft: int = 32,
    bands: int = 8,
    vocab: Vocab | None = None,
    vocab_path: str | None = None,
    resonator: SymbolResonator | None = None,
) -> List[SymbolToken]:
    """Encode text tokens into ``audio``-like :class:`SymbolToken` objects.

    Each input token is converted to a frame of floating point values based on
    the character codes it contains.  The frame is normalised via
    :class:`~signal_io.SignalStream` and analysed by
    :class:`~fft_tokenizer.FFTTokenizer` to obtain band and magnitude
    information.  The resulting tokens mirror those produced by the audio
    encoder so they can be fed into downstream components expecting an audio
    token stream.
    """

    tokenizer = FFTTokenizer(sr=sr, n_fft=n_fft, hop=n_fft, n_bands=bands)
    if vocab_path:
        vc = Vocab.load(vocab_path) if Path(vocab_path).exists() else Vocab()
    else:
        vc = vocab or Vocab()
    out: List[SymbolToken] = []

    for token in tokens:
        codes = [float(ord(ch)) for ch in token][:n_fft]
        if len(codes) < n_fft:
            codes += [0.0] * (n_fft - len(codes))
        stream, _ = SignalStream.from_iterable(
            codes, sr=sr, frame=n_fft, hop=n_fft
        )
        frame = stream.read()
        if frame is None:
            continue
        raw: List[Token] = tokenizer.step(frame)
        for t in raw:
            tok_id = vc.id("audio", t.band)
            feat = {"mag": t.mag, "dphi": t.dphi, "band": t.band}
            if t.bands is not None:
                feat["bands"] = list(t.bands)
            if t.mods:
                feat.update(t.mods)
            tok = SymbolToken(
                t=t.t_idx, id=tok_id, mod="audio", feat=feat, w=int(t.mag)
            )
            if resonator is not None:
                tok.feat["res"] = resonator.score(tok)
            out.append(tok)

    if vocab_path:
        vc.save(vocab_path)
    return out

