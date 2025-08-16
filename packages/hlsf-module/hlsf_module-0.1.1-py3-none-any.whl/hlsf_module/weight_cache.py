"""Simple persistent weight cache and deterministic list helpers.

This module exposes a small ``WeightCache`` class storing floating point
weights in a JSON file.  Two functional helpers ``rotate`` and ``collapse``
provide deterministic operations used by the web API and tests.

The cache API is intentionally tiny:

``WeightCache(path)``
    Create a cache backed by ``path``.  Existing data is loaded on
    initialisation.  By default every :meth:`set` call flushes immediately but
    the behaviour can be configured to batch writes.

``WeightCache.get(key, default=0.0)``
    Retrieve a stored weight or ``default``.

``WeightCache.set(key, value)``
    Store ``value`` under ``key``.  Depending on the batching parameters the
    cache may not be written to disk immediately.

``rotate(values, steps)``
    Return a new list where ``values`` has been rotated ``steps`` positions to
    the right.  The input list is not modified.

``collapse(values)``
    Collapse a sequence of numbers into a single floating point sum.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import json
import os
from pathlib import Path
import time
from typing import ClassVar, Dict, Iterable, List


def _lock_file(f):
    """Platform agnostic file locking."""

    if os.name == "nt":  # pragma: no cover - windows only
        import msvcrt

        msvcrt.locking(f.fileno(), msvcrt.LK_LOCK, 1)
    else:  # pragma: no cover - unix
        import fcntl

        fcntl.flock(f, fcntl.LOCK_EX)


def _unlock_file(f):
    if os.name == "nt":  # pragma: no cover - windows only
        import msvcrt

        msvcrt.locking(f.fileno(), msvcrt.LK_UNLCK, 1)
    else:  # pragma: no cover - unix
        import fcntl

        fcntl.flock(f, fcntl.LOCK_UN)


@dataclass
class WeightCache:
    """Persist weights in a JSON file with simple locking and batching.

    Parameters
    ----------
    path:
        Location of the JSON file.  If the file exists it is loaded during
        initialisation.
    flush_every:
        Number of :meth:`set` calls before an automatic flush.  Defaults to
        ``1`` to preserve the original eager persistence semantics.
    flush_interval:
        Maximum time in seconds that can pass before a flush is forced on the
        next :meth:`set` call.
    """

    VERSION: ClassVar[int] = 1

    path: Path = Path("weights.json")
    weights: Dict[str, float] = field(default_factory=dict)
    flush_every: int = 1
    flush_interval: float = 0.0
    version: int = VERSION

    _pending: int = field(default=0, init=False, repr=False)
    _last_flush: float = field(default_factory=time.monotonic, init=False, repr=False)

    def __post_init__(self) -> None:
        if self.path.exists():
            try:
                with open(self.path, "r") as f:
                    _lock_file(f)
                    try:
                        data = json.load(f)
                    finally:
                        _unlock_file(f)
                if isinstance(data, dict) and "weights" in data:
                    self.version = data.get("version", self.VERSION)
                    self.weights = data.get("weights", {})
                elif isinstance(data, dict):
                    self.weights = data
                else:
                    self.weights = {}
            except json.JSONDecodeError:
                # Corrupt cache – start fresh
                self.weights = {}

    def save(self) -> None:
        """Write the current cache contents to disk with locking."""

        payload = {"version": self.VERSION, "weights": {}}
        if self.path.exists():
            with open(self.path, "r+") as f:
                _lock_file(f)
                try:
                    try:
                        data = json.load(f)
                        if isinstance(data, dict) and "weights" in data:
                            payload = data
                        elif isinstance(data, dict):
                            payload["weights"].update(data)
                    except json.JSONDecodeError:
                        pass
                    payload["weights"].update(self.weights)
                    payload["version"] = self.VERSION
                    f.seek(0)
                    f.truncate()
                    json.dump(payload, f)
                finally:
                    _unlock_file(f)
        else:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.path, "w") as f:
                _lock_file(f)
                try:
                    payload["weights"].update(self.weights)
                    json.dump(payload, f)
                finally:
                    _unlock_file(f)
        self.weights = payload["weights"]

    def flush(self) -> None:
        self.save()
        self._pending = 0
        self._last_flush = time.monotonic()

    def get(self, key: str, default: float = 0.0) -> float:
        """Return the weight for ``key`` or ``default`` if missing."""

        return self.weights.get(key, default)

    def set(self, key: str, value: float) -> None:
        """Store ``value`` under ``key`` and lazily persist the cache."""

        self.weights[key] = float(value)
        self._pending += 1
        now = time.monotonic()
        if (
            self._pending >= self.flush_every
            or (self.flush_interval and now - self._last_flush >= self.flush_interval)
        ):
            self.flush()

    @classmethod
    def merge(cls, dest: Path, *paths: Path) -> "WeightCache":
        """Merge multiple cache files into ``dest`` and return the new cache."""

        combined: Dict[str, float] = {}
        for path in paths:
            tmp = cls(path)
            combined.update(tmp.weights)
        cache = cls(dest)
        cache.weights = combined
        cache.flush()
        return cache


def rotate(values: List[float], steps: int) -> List[float]:
    """Rotate ``values`` to the right by ``steps`` positions.

    The function is pure – it never mutates the input ``values`` and always
    returns the same result for the same input.
    """

    if not values:
        return []
    steps = steps % len(values)
    if steps == 0:
        return list(values)
    return values[-steps:] + values[:-steps]


def collapse(values: Iterable[float]) -> float:
    """Collapse ``values`` into a deterministic sum."""

    return float(sum(values))

