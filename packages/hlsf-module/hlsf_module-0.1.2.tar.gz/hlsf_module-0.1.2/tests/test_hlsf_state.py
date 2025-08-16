import json
from hlsf_module.tensor_mapper import HLSFState


def test_hlsfstate_roundtrip():
    state = HLSFState(
        triangles=[[[0.0, 0.0], [1.0, 0.0], [0.0, 1.0]]],
        colors=[[1.0, 0.0, 0.0, 1.0]],
        active_motif=0,
        metrics={"a": 1.0},
        resonance_metrics={"b": 2.0},
        prototypes=[{"p": 1}],
        proof_log=[{"hash": "abc"}],
    )
    data = json.loads(json.dumps(state.to_hlsf()))
    loaded = HLSFState.from_hlsf(data)
    assert loaded == state


def test_hlsfstate_roundtrip_with_depth():
    state = HLSFState(
        triangles=[[[0.0, 0.0, 0.0], [1.0, 0.0, 0.0], [0.0, 1.0, 0.5]]],
        colors=[[1.0, 0.0, 0.0, 1.0]],
        metrics={},
        resonance_metrics={},
        prototypes=[],
        proof_log=[],
    )
    data = json.loads(json.dumps(state.to_hlsf()))
    loaded = HLSFState.from_hlsf(data)
    assert loaded == state
