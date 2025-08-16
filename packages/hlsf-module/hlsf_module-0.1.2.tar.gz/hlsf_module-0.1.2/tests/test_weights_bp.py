import sys, pathlib
import pytest

sys.path.append(str(pathlib.Path(__file__).resolve().parents[1]))

from hlsf_module import weights_bp


def test_update_handles_metric_dicts():
    graph = {1: {"weight": 0.5, "extra": 1.0}, 2: {"weight": 0.7}, 3: 0.2}
    store = {1: {"w": 0, "f": 0, "s": 1.0}}
    weights_bp.update(graph, [], store)
    assert store[1]["s"] == pytest.approx(1.5)
    assert store[2]["s"] == pytest.approx(0.7)
    assert store[3]["s"] == pytest.approx(0.2)
    assert store[1]["w"] == 1 and store[1]["f"] == 1
    assert store[2]["w"] == 1 and store[2]["f"] == 1
    assert store[3]["w"] == 1 and store[3]["f"] == 1
