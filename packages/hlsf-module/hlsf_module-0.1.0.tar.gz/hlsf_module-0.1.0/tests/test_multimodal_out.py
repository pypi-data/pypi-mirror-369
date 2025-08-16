import math
import sys, pathlib

import pytest

sys.path.append(str(pathlib.Path(__file__).resolve().parents[1]))

from hlsf_module.multimodal_out import resynth_bands, snapshot_state
from hlsf_module.tensor_mapper import HLSFState
import json


def test_resynth_bands_tone_frequencies_and_length():
    sr = 800
    duration = 0.1
    bands = [1.0, 0.5]
    audio = resynth_bands(bands, duration, sr=sr)
    assert len(audio) == int(sr * duration)

    N = len(audio)
    for i, mag in enumerate(bands):
        freq = 20 * (2 ** i)
        corr = sum(audio[n] * math.sin(2 * math.pi * freq * n / sr) for n in range(N))
        assert corr == pytest.approx(0.5 * N * mag, rel=1e-4)

    corr = sum(audio[n] * math.sin(2 * math.pi * 60 * n / sr) for n in range(N))
    assert abs(corr) < 1e-10


def test_snapshot_state_writes_proof_log(tmp_path):
    state = HLSFState(triangles=[], colors=[], metrics={}, proof_log=[{"hash": "abc"}])
    path = tmp_path / "state.json"
    snapshot_state(path, state)
    data = json.loads(path.read_text())
    assert data["proof_log"] == [{"hash": "abc"}]
