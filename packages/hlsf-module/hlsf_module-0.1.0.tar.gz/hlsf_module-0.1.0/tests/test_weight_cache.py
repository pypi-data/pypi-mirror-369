import json
import threading
import time

from hlsf_module.weight_cache import WeightCache, collapse, rotate


def test_weight_cache_persistence(tmp_path):
    path = tmp_path / "weights.json"
    cache = WeightCache(path)
    cache.set("a", 1.0)

    cache2 = WeightCache(path)
    assert cache2.get("a") == 1.0


def test_lazy_flush_after_n(tmp_path):
    path = tmp_path / "weights.json"
    cache = WeightCache(path, flush_every=2)
    cache.set("a", 1.0)
    assert not path.exists()
    cache.set("b", 2.0)
    data = json.loads(path.read_text())
    assert data["weights"] == {"a": 1.0, "b": 2.0}


def test_flush_interval(tmp_path):
    path = tmp_path / "weights.json"
    cache = WeightCache(path, flush_every=10, flush_interval=0.2)
    cache.set("a", 1.0)
    time.sleep(0.25)
    cache.set("b", 2.0)
    data = json.loads(path.read_text())
    assert data["weights"] == {"a": 1.0, "b": 2.0}


def test_concurrent_writes_locked(tmp_path):
    path = tmp_path / "weights.json"
    cache1 = WeightCache(path, flush_every=1)
    cache2 = WeightCache(path, flush_every=1)

    t1 = threading.Thread(target=lambda: cache1.set("a", 1.0))
    t2 = threading.Thread(target=lambda: cache2.set("b", 2.0))
    t1.start()
    t2.start()
    t1.join()
    t2.join()

    merged = WeightCache(path)
    assert merged.get("a") == 1.0
    assert merged.get("b") == 2.0


def test_merge(tmp_path):
    path1 = tmp_path / "w1.json"
    path2 = tmp_path / "w2.json"
    cache1 = WeightCache(path1)
    cache1.set("a", 1.0)
    cache2 = WeightCache(path2)
    cache2.set("b", 2.0)

    dest = tmp_path / "merged.json"
    merged = WeightCache.merge(dest, path1, path2)
    assert merged.get("a") == 1.0
    assert merged.get("b") == 2.0
    meta = json.loads(dest.read_text())
    assert meta["version"] == WeightCache.VERSION


def test_rotation_and_collapse_deterministic():
    values = [1, 2, 3, 4]
    rotated1 = rotate(values, 1)
    rotated2 = rotate(values, 1)
    assert rotated1 == rotated2 == [4, 1, 2, 3]

    collapsed1 = collapse(rotated1)
    collapsed2 = collapse(rotated1)
    assert collapsed1 == collapsed2 == sum(rotated1)
