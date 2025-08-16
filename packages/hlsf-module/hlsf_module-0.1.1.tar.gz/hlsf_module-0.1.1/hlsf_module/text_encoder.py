from __future__ import annotations

"""Text encoder converting characters to :class:`~symbols.schema.SymbolToken`."""

from pathlib import Path
from typing import List

from .symbols.schema import SymbolToken
from .symbols.vocab import Vocab


class TextEncoder:
    """Encode plain text into symbolic tokens.

    Each character is mapped to a deterministic ID in the shared
    :class:`~symbols.vocab.Vocab`.  The magnitude feature is fixed to ``1.0``
    so that downstream heuristics like ``agency_gates.decide`` can operate on
    text tokens in the same manner as audio tokens.
    """

    def __init__(self, vocab: Vocab | None = None, vocab_path: str | None = None) -> None:
        if vocab_path:
            vc = Vocab.load(vocab_path) if Path(vocab_path).exists() else (vocab or Vocab())
        else:
            vc = vocab or Vocab()
        self.vocab = vc
        self._vocab_path = vocab_path

    def step(self, text: str) -> List[SymbolToken]:
        tokens: List[SymbolToken] = []
        for idx, ch in enumerate(text):
            code = ord(ch)
            tok_id = self.vocab.id("text", code)
            feat = {"char": code, "mag": 1.0, "dphi": 0.0}
            tokens.append(SymbolToken(t=idx, id=tok_id, mod="text", feat=feat, w=1))
        if self._vocab_path:
            self.vocab.save(self._vocab_path)
        return tokens
