import pathlib
import sys

sys.path.append(str(pathlib.Path(__file__).resolve().parents[1]))

from hlsf_module.trainer import Trainer
from hlsf_module.symbols.schema import SymbolToken


def make_dataset():
    return [
        {
            "audio": [
                SymbolToken(t=0, id=1, mod="audio", feat={"band": 1, "mag": 0.5})
            ],
            "text": [SymbolToken(t=0, id=2, mod="text", feat={"band": 2, "mag": 0.5})],
        },
        {
            "audio": [
                SymbolToken(t=1, id=1, mod="audio", feat={"band": 1, "mag": 0.5})
            ],
            "text": [SymbolToken(t=1, id=3, mod="text", feat={"band": 3, "mag": 0.5})],
        },
    ]


def make_tuple_dataset():
    return [
        (
            [SymbolToken(t=0, id=1, mod="audio", feat={"band": 1, "mag": 0.5})],
            [SymbolToken(t=0, id=2, mod="text", feat={"band": 2, "mag": 0.5})],
        ),
        (
            [SymbolToken(t=1, id=1, mod="audio", feat={"band": 1, "mag": 0.5})],
            [SymbolToken(t=1, id=3, mod="text", feat={"band": 3, "mag": 0.5})],
        ),
    ]


def test_trainer_updates_all_components():
    trainer = Trainer()
    trainer.train(make_dataset())

    # TrainingDB should contain cross-modal connections
    assert (1, 2) in trainer.training_db.connections
    assert (1, 3) in trainer.training_db.connections

    # weights_bp store should track band statistics
    assert trainer.weights_store[1]["w"] == 2
    assert trainer.weights_store[2]["w"] == 1
    assert trainer.weights_store[3]["w"] == 1

    # Resonator should learn prototypes for all token ids
    assert 1 in trainer.resonator.prototypes
    assert 2 in trainer.resonator.prototypes
    assert 3 in trainer.resonator.prototypes


def test_trainer_handles_tuple_dataset_and_batch(tmp_path):
    trainer = Trainer()
    trainer.train(make_tuple_dataset(), batch_size=2)

    assert (1, 2) in trainer.training_db.connections
    assert trainer.weights_store[1]["w"] == 2

    db_file = tmp_path / "db.json"
    proto_file = tmp_path / "proto.json"
    trainer.save(db_file, proto_file)

    new_trainer = Trainer()
    new_trainer.load(db_file, proto_file)

    assert (1, 2) in new_trainer.training_db.connections
    assert 1 in new_trainer.resonator.prototypes
