from __future__ import annotations

"""N-gram based tokenizer emitting multi-level :class:`~symbols.schema.SymbolToken` lists."""

from pathlib import Path
from typing import List
import re
import zlib

from .symbols.schema import SymbolToken
from .symbols.vocab import Vocab


def tokenize_multilevel(
    text: str,
    vocab: Vocab | None = None,
    vocab_path: str | None = None,
) -> List[List[SymbolToken]]:
    """Tokenize ``text`` into multiple granularities.

    The returned list contains token lists for:
    full string, words, overlapping word pairs, 4-grams, 3-grams,
    bigrams and individual characters.

    Weights ``w`` decrease with shorter n-grams so later pruning can
    prefer higher-level tokens.
    """

    if vocab_path:
        vocab = Vocab.load(vocab_path) if Path(vocab_path).exists() else Vocab()
    else:
        vocab = vocab or Vocab()
    levels: List[List[SymbolToken]] = []

    def make_token(seq: str, start: int, weight: int) -> SymbolToken:
        if len(seq) == 1:
            code = ord(seq)
        else:
            code = zlib.adler32(seq.encode("utf-8"))
        tok_id = vocab.id("text", code)
        feat = {"mag": 1.0, "len": float(len(seq))}
        if len(seq) == 1:
            feat["char"] = ord(seq)
            feat["dphi"] = 0.0
        return SymbolToken(t=start, id=tok_id, mod="text", feat=feat, w=weight)

    # Full string
    levels.append([make_token(text, 0, 7)])

    # Words
    word_matches = list(re.finditer(r"\S+", text))
    word_tokens: List[SymbolToken] = []
    for m in word_matches:
        word_tokens.append(make_token(m.group(0), m.start(), 6))
    levels.append(word_tokens)

    # Overlapping word pairs
    pair_tokens: List[SymbolToken] = []
    for i in range(len(word_matches) - 1):
        start = word_matches[i].start()
        end = word_matches[i + 1].end()
        pair = text[start:end]
        pair_tokens.append(make_token(pair, start, 5))
    levels.append(pair_tokens)

    # Character 4-grams
    four_tokens = [make_token(text[i:i+4], i, 4) for i in range(max(len(text) - 3, 0))]
    levels.append(four_tokens)

    # Character 3-grams
    tri_tokens = [make_token(text[i:i+3], i, 3) for i in range(max(len(text) - 2, 0))]
    levels.append(tri_tokens)

    # Bigrams
    bi_tokens = [make_token(text[i:i+2], i, 2) for i in range(max(len(text) - 1, 0))]
    levels.append(bi_tokens)

    # Characters
    char_tokens = [make_token(ch, idx, 1) for idx, ch in enumerate(text)]
    levels.append(char_tokens)

    if vocab_path:
        vocab.save(vocab_path)
    return levels
