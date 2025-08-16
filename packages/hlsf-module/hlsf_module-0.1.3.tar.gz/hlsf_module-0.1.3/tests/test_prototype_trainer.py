from hlsf_module.prototypes import PrototypeTrainer


def test_min_spectral_distance():
    trainer = PrototypeTrainer(min_distance=1.0)
    assert trainer.add([0.0, 0.0])
    # Too close to the first prototype -> rejected
    assert not trainer.add([0.5, 0.0])
    # Far enough -> accepted
    assert trainer.add([2.0, 0.0])


def test_prototype_round_trip(tmp_path):
    trainer = PrototypeTrainer()
    trainer.add([0.0, 0.0])
    trainer.add([2.0, 0.0])
    path = tmp_path / "prototypes.json"
    trainer.save(path)
    new_trainer = PrototypeTrainer()
    new_trainer.load(path)
    assert new_trainer.prototypes == trainer.prototypes
