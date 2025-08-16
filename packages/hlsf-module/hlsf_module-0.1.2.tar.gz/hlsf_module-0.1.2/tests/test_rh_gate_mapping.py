from hlsf_module.rh_gate import RHGate
from hlsf_module.rh_mapping import RHMapping


def test_rh_gate_decision_and_mapping():
    gate = RHGate()
    motif = {"scores": [0.5, 0.1], "duration": 2}
    assert gate.decide(motif, threshold=0.2, sustain=1)

    mapping = RHMapping()
    class Tok:
        def __init__(self, band):
            self.band = band
    tokens = [Tok(1), Tok(3)]
    assert mapping.map(tokens) == [1, 3]
