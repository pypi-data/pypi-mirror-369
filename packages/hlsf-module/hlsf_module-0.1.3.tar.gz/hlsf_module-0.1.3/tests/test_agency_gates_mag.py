import sys
import pathlib

sys.path.append(str(pathlib.Path(__file__).resolve().parents[1]))

from hlsf_module.agency_gates import decide


def test_decide_uses_mag_when_scores_missing():
    motif = {"mag": 0.3, "duration": 1, "detectors": 1}
    assert decide(motif, threshold=0.2) is True
    assert decide({**motif, "mag": 0.1}, threshold=0.2) is False
