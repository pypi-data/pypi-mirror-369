from __future__ import annotations

import sys, pathlib
sys.path.append(str(pathlib.Path(__file__).resolve().parents[1]))

from hlsf_module.ngram_text_encoder import tokenize_multilevel


def test_tokenize_multilevel_counts_and_weights():
    text = "hello world!"
    levels = tokenize_multilevel(text)
    assert len(levels) == 7
    sizes = [len(lvl) for lvl in levels]
    assert sizes == [1, 2, 1, 9, 10, 11, 12]
    weights = [lvl[0].w for lvl in levels]
    assert weights == [7, 6, 5, 4, 3, 2, 1]
    assert all("char" in tok.feat for tok in levels[-1])
