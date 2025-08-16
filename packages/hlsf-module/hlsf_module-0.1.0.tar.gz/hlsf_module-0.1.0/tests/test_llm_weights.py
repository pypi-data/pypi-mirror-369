import math
import math
import pytest
import math

from hlsf_module.llm_weights import CheapLLM, TrainingDB
from hlsf_module.symbols.schema import SymbolToken


def test_training_db_accumulates_weights() -> None:
    tokens = [
        SymbolToken(t=0, id=1, mod="m", feat={"a": 1.0, "b": 0.0}),
        SymbolToken(t=1, id=2, mod="m", feat={"a": 1.0, "b": 1.0}),
    ]
    db = TrainingDB()
    llm = CheapLLM()
    db.update(tokens, llm)
    pair = (1, 2)
    expected = 1 / math.sqrt(2)
    assert db.connections[pair] == pytest.approx(expected)
    db.update(tokens, llm)
    assert db.connections[pair] == pytest.approx(expected * 2)


def test_training_db_round_trip(tmp_path) -> None:
    tokens = [
        SymbolToken(t=0, id=1, mod="m", feat={"a": 1.0}),
        SymbolToken(t=1, id=2, mod="m", feat={"a": 1.0}),
    ]
    db = TrainingDB()
    db.update(tokens)
    json_path = tmp_path / "connections.json"
    csv_path = tmp_path / "connections.csv"
    db.save(json_path)
    db.save(csv_path)
    json_db = TrainingDB()
    json_db.load(json_path)
    csv_db = TrainingDB()
    csv_db.load(csv_path)
    assert json_db.connections == db.connections
    assert csv_db.connections == db.connections


def test_training_db_merge() -> None:
    db1 = TrainingDB()
    db1.connections = {(1, 2): 1.0, (2, 3): 0.5}
    db2 = TrainingDB()
    db2.connections = {(1, 2): 2.0, (3, 4): 1.0}
    db1.merge(db2)
    assert db1.connections[(1, 2)] == pytest.approx(3.0)
    assert db1.connections[(2, 3)] == pytest.approx(0.5)
    assert db1.connections[(3, 4)] == pytest.approx(1.0)


def test_custom_weight_extractor() -> None:
    tokens = [
        SymbolToken(t=0, id=1, mod="m", feat={}),
        SymbolToken(t=1, id=2, mod="m", feat={}),
    ]

    def constant_weight(a: SymbolToken, b: SymbolToken) -> float:
        return 0.5

    llm = CheapLLM(weight_extractor=constant_weight)
    db = TrainingDB()
    db.update(tokens, llm)
    assert db.connections[(1, 2)] == 0.5
