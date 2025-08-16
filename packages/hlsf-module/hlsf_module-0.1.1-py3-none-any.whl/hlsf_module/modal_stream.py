"""General modal stream utilities for 1D, 2D and 3D data."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable, List, Tuple, Optional, Any
import math


# ---------------------------------------------------------------------------
# window helpers

def _hann_component(n: int) -> List[float]:
    if n < 1:
        return []
    if n == 1:
        return [1.0]
    return [0.5 - 0.5 * math.cos(2 * math.pi * i / (n - 1)) for i in range(n)]


def _hann_window(shape: Tuple[int, ...]):
    if len(shape) == 1:
        return _hann_component(shape[0])
    if len(shape) == 2:
        wy = _hann_component(shape[0])
        wx = _hann_component(shape[1])
        return [[wy[i] * wx[j] for j in range(shape[1])] for i in range(shape[0])]
    if len(shape) == 3:
        wz = _hann_component(shape[0])
        wy = _hann_component(shape[1])
        wx = _hann_component(shape[2])
        return [
            [[wz[i] * wy[j] * wx[k] for k in range(shape[2])] for j in range(shape[1])]
            for i in range(shape[0])
        ]
    raise ValueError("unsupported dimensionality for Hann window")


# ---------------------------------------------------------------------------
# general list utilities

def _listify(data: Any) -> Any:
    if isinstance(data, (list, tuple)):
        return [_listify(x) for x in data]
    return data


def _max_abs(data: Any) -> float:
    if isinstance(data, list):
        return max((_max_abs(x) for x in data), default=0.0)
    return abs(float(data))


def _normalise(data: Any, max_val: float) -> Any:
    if isinstance(data, list):
        return [_normalise(x, max_val) for x in data]
    return float(data) / (max_val or 1.0)


def _shape(data: Any) -> Tuple[int, ...]:
    shape: List[int] = []
    while isinstance(data, list) and data:
        shape.append(len(data))
        data = data[0]
    if isinstance(data, list) and not data:
        shape.append(0)
    return tuple(shape)


def _slice_nd(data: Any, pos: Tuple[int, ...], shape: Tuple[int, ...]) -> Any:
    if len(shape) == 1:
        return data[pos[0] : pos[0] + shape[0]]
    return [
        _slice_nd(d, pos[1:], shape[1:])
        for d in data[pos[0] : pos[0] + shape[0]]
    ]


def _multiply(a: Any, b: Any) -> Any:
    if isinstance(a, list):
        return [_multiply(x, y) for x, y in zip(a, b)]
    return float(a) * float(b)


def _advance_pos(
    pos: Tuple[int, ...],
    hop: Tuple[int, ...],
    data_shape: Tuple[int, ...],
    frame_shape: Tuple[int, ...],
) -> Optional[Tuple[int, ...]]:
    pos_list = list(pos)
    dim = len(frame_shape)
    for i in reversed(range(dim)):
        pos_list[i] += hop[i]
        if pos_list[i] + frame_shape[i] <= data_shape[i]:
            return tuple(pos_list)
        pos_list[i] = 0
    return None


# ---------------------------------------------------------------------------
# core abstraction


@dataclass
class ModalStream:
    """Generic N-dimensional normalised stream with windowing."""

    data: Any
    shape: Tuple[int, ...]
    hop: Tuple[int, ...]
    modality: str = "generic"
    _pos: Tuple[int, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        if not self.shape:
            raise ValueError("shape must be non-empty")
        if len(self.shape) != len(self.hop):
            raise ValueError("shape and hop dimensionality mismatch")
        if not self._pos:
            self._pos = tuple(0 for _ in self.shape)
        self._data_shape = _shape(self.data)

    # ------------------------------------------------------------------
    # factory helpers
    @classmethod
    def from_array(
        cls,
        data: Iterable[Any],
        shape: Tuple[int, ...],
        hop: Tuple[int, ...],
        modality: str = "generic",
    ) -> "ModalStream":
        data_list = _listify(list(data))
        if not data_list:
            raise ValueError("data iterable is empty")
        max_val = _max_abs(data_list) or 1.0
        norm = _normalise(data_list, max_val)
        return cls(norm, shape, hop, modality=modality)

    # ------------------------------------------------------------------
    # reading
    def _preprocess(self, chunk: Any) -> Any:
        return chunk

    def read(self) -> Optional[Any]:
        if any(
            self._pos[i] + self.shape[i] > self._data_shape[i]
            for i in range(len(self.shape))
        ):
            return None
        chunk = _slice_nd(self.data, self._pos, self.shape)
        chunk = self._preprocess(chunk)
        win = _hann_window(self.shape)
        chunk = _multiply(chunk, win)
        next_pos = _advance_pos(self._pos, self.hop, self._data_shape, self.shape)
        if next_pos is None:
            self._pos = tuple(self._data_shape)
        else:
            self._pos = next_pos
        return chunk

