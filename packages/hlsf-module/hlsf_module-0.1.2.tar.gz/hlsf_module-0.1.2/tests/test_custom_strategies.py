from hlsf_module import agency_gates
from hlsf_module.tensor_mapper import TensorMapper


def test_set_mapper_registers_strategy():
    def constant_mapper(idx, total, metrics):
        return [[ [0.0, 0.0], [0.0, 0.0], [0.0, 0.0] ], [0.0, 0.0, 0.0, 1.0]]

    tm = TensorMapper()
    tm.set_mapper(constant_mapper, name="constant")
    tm.graph = {
        1: {
            "weight": 1.0,
            "phase": 0.0,
            "phase_count": 1.0,
            "centroid": 0.0,
            "centroid_count": 1.0,
        }
    }
    state = tm.to_hlsf()
    assert state.triangles[0] == [[0.0, 0.0], [0.0, 0.0], [0.0, 0.0]]

    tm2 = TensorMapper(mapper="constant")
    tm2.graph = tm.graph
    state2 = tm2.to_hlsf()
    assert state2.triangles[0] == state.triangles[0]


def test_register_custom_gate_strategy():
    def low_threshold(scores, motif, cfg):
        return -1.0

    agency_gates.register_strategy("low", low_threshold)
    motif = {"scores": [0.1, 0.05], "duration": 1, "detectors": 1}
    assert agency_gates.decide(motif, strategy="low", margin=0.0)

