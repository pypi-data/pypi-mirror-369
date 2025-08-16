from __future__ import annotations

"""Symbol resonance via prototype correlation."""

from typing import Dict, Iterable, List
from math import sqrt
import logging
import os

from .symbols.schema import SymbolToken

# Optional GPU backends
try:  # pragma: no cover - import guard
    import torch as _torch
except ImportError:  # pragma: no cover - torch missing
    _torch = None

try:  # pragma: no cover - import guard
    import cupy as _cupy
except ImportError:  # pragma: no cover - cupy missing
    _cupy = None

_backend_env = os.getenv("HLSF_GPU_BACKEND", "").lower()

def _select_backend(requested: str | None) -> str:
    order = [requested or _backend_env, "torch", "cupy"]
    for name in order:
        if name == "torch" and _torch is not None:
            return "torch"
        if name == "cupy" and _cupy is not None:
            return "cupy"
    return "cpu"

logger = logging.getLogger(__name__)


class SymbolResonator:
    """Maintain symbol prototypes and compute resonance scores.

    Prototypes are stored per symbol ``id`` as floating point vectors. The
    :meth:`update` methods maintain an exponential moving average of features
    and :meth:`score` returns the normalised correlation between an input token
    and its prototype.
    """

    def __init__(
        self,
        decay: float = 0.99,
        *,
        use_gpu: bool = False,
        device: str | None = None,
        backend: str | None = None,
    ) -> None:
        self.decay = decay
        self.prototypes: Dict[int, List[float] | object] = {}
        self.use_gpu = False
        self.device = "cpu"
        self.backend = _select_backend(backend if use_gpu else None)
        self._torch = None
        self._cupy = None
        if self.backend == "torch" and _torch is not None:
            dev = device or ("cuda" if _torch.cuda.is_available() else "cpu")
            if dev != "cpu" and _torch.cuda.is_available():
                self.device = dev
                self._torch = _torch
                self.use_gpu = True
            else:
                self._torch = _torch
                logger.warning("GPU requested but CUDA unavailable; using CPU")
        elif self.backend == "cupy" and _cupy is not None:
            self._cupy = _cupy
            self.use_gpu = True
        elif use_gpu and self.backend == "cpu":
            logger.warning("Requested GPU backend not available; using CPU")

    def _vector(self, feat: Dict[str, float]):
        vec = [
            float(v)
            for k, v in sorted(feat.items())
            if k != "res" and isinstance(v, (int, float))
        ]
        if self.use_gpu and self.backend == "torch" and self._torch is not None:
            return self._torch.tensor(vec, device=self.device)
        if self.use_gpu and self.backend == "cupy" and self._cupy is not None:
            return self._cupy.array(vec)
        return vec

    def score(self, token: SymbolToken) -> float:
        vec = self._vector(token.feat)
        proto = self.prototypes.get(token.id)
        if proto is None:
            return 0.0
        if self.use_gpu and self.backend == "torch" and self._torch is not None:
            if proto.shape != vec.shape:  # type: ignore[attribute-defined-outside-init]
                return 0.0
            dot = (vec * proto).sum()
            norm = vec.norm() * proto.norm()
            if norm.item() == 0:
                return 0.0
            return (dot / norm).item()
        if self.use_gpu and self.backend == "cupy" and self._cupy is not None:
            cp = self._cupy
            if proto.shape != vec.shape:  # type: ignore[attribute-defined-outside-init]
                return 0.0
            dot = (vec * proto).sum()
            norm = cp.linalg.norm(vec) * cp.linalg.norm(proto)
            norm_val = float(cp.asnumpy(norm))
            if norm_val == 0:
                return 0.0
            return float(cp.asnumpy(dot / norm))
        if len(proto) != len(vec):  # type: ignore[arg-type]
            return 0.0
        dot = sum(a * b for a, b in zip(vec, proto))  # type: ignore[arg-type]
        norm_v = sqrt(sum(a * a for a in vec))
        norm_p = sqrt(sum(b * b for b in proto))  # type: ignore[arg-type]
        if norm_v == 0 or norm_p == 0:
            return 0.0
        return dot / (norm_v * norm_p)

    def update(self, token: SymbolToken) -> float:
        vec = self._vector(token.feat)
        proto = self.prototypes.get(token.id)
        if self.use_gpu and self.backend == "torch" and self._torch is not None:
            if proto is None or proto.shape != vec.shape:  # type: ignore[union-attr]
                self.prototypes[token.id] = vec
            else:
                self.prototypes[token.id] = self.decay * proto + (1 - self.decay) * vec
            return self.score(token)
        if self.use_gpu and self.backend == "cupy" and self._cupy is not None:
            if proto is None or proto.shape != vec.shape:  # type: ignore[union-attr]
                self.prototypes[token.id] = vec
            else:
                self.prototypes[token.id] = self.decay * proto + (1 - self.decay) * vec
            return self.score(token)
        if proto is None or len(proto) != len(vec):  # type: ignore[arg-type]
            self.prototypes[token.id] = vec  # type: ignore[assignment]
        else:
            self.prototypes[token.id] = [
                self.decay * p + (1 - self.decay) * v for p, v in zip(proto, vec)  # type: ignore[arg-type]
            ]
        return self.score(token)

    def update_batch(self, tokens: Iterable[SymbolToken]) -> List[float]:
        return [self.update(t) for t in tokens]

