import asyncio
import json
import pathlib
import sys

import pytest

sys.path.append(str(pathlib.Path(__file__).resolve().parents[1]))

from hlsf_module.adjacency_expander import expand, clear_cache
from hlsf_module.symbols.schema import SymbolToken
from hlsf_module.llm_client import StubLLMClient
from hlsf_module.llm_weights import TrainingDB


def _expand(token: SymbolToken, **kwargs):
    return asyncio.run(expand(token, **kwargs))


def test_expand_caches_results():
    clear_cache()
    token = SymbolToken(t=0, id=1, mod="x", feat={})
    stub = StubLLMClient(["foo", "bar"])
    first = _expand(token, llm=stub)
    second = _expand(token, llm=stub)
    assert first == second
    assert stub.calls == 1


def test_weight_calibration_and_filtering():
    clear_cache()
    token1 = SymbolToken(t=0, id=1, mod="x", feat={})
    token2 = SymbolToken(t=0, id=2, mod="x", feat={})
    stub = StubLLMClient(["foo", "badword"])
    db = TrainingDB()

    out1 = [json.loads(t) for t in _expand(token1, llm=stub, training_db=db, update=True)]
    assert [t["feat"]["text"] for t in out1] == ["foo"]
    assert out1[0]["w"] == 1.0
    assert len(db.adj_edges) == 1

    stub.responses = ["foo"]
    out2 = [json.loads(t) for t in _expand(token2, llm=stub, training_db=db, update=True)]
    assert out2[0]["w"] == 0.5


def test_embedding_fallback_uses_training_db():
    clear_cache()
    tok_a = SymbolToken(t=0, id=1, mod="x", feat={"v": 1.0})
    tok_b = SymbolToken(t=0, id=2, mod="x", feat={"v": 1.0})
    tok_c = SymbolToken(t=0, id=3, mod="x", feat={"v": -1.0})
    db = TrainingDB()
    db.update([tok_a, tok_b, tok_c])

    out = [json.loads(t) for t in _expand(tok_a, llm=None, training_db=db)]
    ids = {t["id"] for t in out}
    assert ids <= {2, 3}
    assert len(out) <= 2
