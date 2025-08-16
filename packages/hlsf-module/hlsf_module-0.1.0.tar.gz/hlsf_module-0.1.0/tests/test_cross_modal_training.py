import sys
import pathlib

sys.path.append(str(pathlib.Path(__file__).resolve().parents[1]))

from hlsf_module.llm_weights import CheapLLM, TrainingDB
from hlsf_module.symbols.schema import SymbolToken


def test_training_db_cross_modal_pairs() -> None:
    tokens = [
        SymbolToken(t=0, id=1, mod="audio", feat={"x": 1.0}),
        SymbolToken(t=1, id=2, mod="text", feat={"x": 1.0}),
    ]
    db = TrainingDB()
    llm = CheapLLM()
    db.update(tokens, llm)
    assert (1, 2) in db.connections
    assert db.connections[(1, 2)] > 0.0
