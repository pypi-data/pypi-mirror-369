
from hlsf_module.symbols.resonator import SymbolResonator


def make_resonator():
    prototypes = {
        "text": [[1.0, 0.0], [0.5, 0.5]],
        "audio": [[0.0, 1.0]],
    }
    weights = {"text": 1.0, "audio": 1.0}
    return SymbolResonator(prototypes, weights)


def test_weighted_sum_resonance():
    r = make_resonator()
    inputs = {"text": [1.0, 0.0], "audio": [0.0, 1.0]}
    # For the given inputs scores are 1.0 for both modalities
    assert r.resonance(inputs) == 2.0
    r.weights["text"] = 2.0
    r.weights["audio"] = 0.5
    assert r.resonance(inputs) == 2.5


def test_training_adjusts_weights():
    r = make_resonator()
    inputs = {"text": [1.0, 0.0], "audio": [0.0, 1.0]}
    r.weights["text"] = 2.0
    r.weights["audio"] = 0.5
    # Current resonance is 2.5; target is higher which should increase weights.
    r.train(inputs, target=4.0, lr=0.1)
    assert r.weights["text"] > 2.0
    assert r.weights["audio"] > 0.5

