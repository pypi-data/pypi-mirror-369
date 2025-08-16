from fastapi.testclient import TestClient

from hlsf_module.web_api import WeightCache, create_app


def test_web_api_endpoints(tmp_path):
    cache = WeightCache(tmp_path / "weights.json")
    app = create_app(cache)
    client = TestClient(app)

    # set and get weight
    resp = client.post("/weights/foo", json={"weight": 2.5})
    assert resp.status_code == 200
    assert client.get("/weights/foo").json() == {"weight": 2.5}

    # rotate
    assert client.post("/rotate", json={"values": [1, 2, 3], "steps": 1}).json() == {
        "values": [3, 1, 2]
    }

    # collapse
    assert client.post("/collapse", json={"values": [1, 2, 3]}).json() == {
        "value": 6.0
    }

