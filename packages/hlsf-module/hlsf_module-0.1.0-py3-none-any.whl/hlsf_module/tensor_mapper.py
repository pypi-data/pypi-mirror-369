"""Map token relationships to simple geometry.

The original implementation rendered each token/band relationship as an
equilateral triangle positioned on a unit circle.  This module now exposes a
slightly richer set of features so that more expressive shapes can be derived
from spectral and phase information.  It also allows callers to provide custom
mapping strategies.
"""

from __future__ import annotations

from dataclasses import dataclass
import math
import logging
import os
from typing import Any, Callable, Dict, Iterable, List, Tuple

from .symbols.schema import SymbolToken

Polygon = List[Tuple[float, float]]
Color = List[float]

# Optional vectorised backends
try:  # pragma: no cover - import guard
    import torch as _torch
except ImportError:  # pragma: no cover - torch missing
    _torch = None

try:  # pragma: no cover - import guard
    import cupy as _cupy
except ImportError:  # pragma: no cover - cupy missing
    _cupy = None

try:  # pragma: no cover - import guard
    import numpy as _np
except Exception:  # pragma: no cover - numpy missing
    _np = None

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


@dataclass
class HLSFState:
    triangles: List[List[List[float]]]
    colors: List[List[float]]
    active_motif: int | None = None
    metrics: Dict[str, float] | None = None
    resonance_metrics: Dict[str, float] | None = None
    prototypes: List[Dict[str, Any]] | None = None
    proof_log: List[Dict[str, Any]] | None = None

    def to_hlsf(self) -> Dict[str, Any]:
        """Return a serialisable representation of the current state.

        ``triangles`` contains polygon geometry where each vertex is a list of
        two or three floats representing ``x``, ``y`` and optional ``z`` depth
        coordinates.  The historic name is preserved for backwards
        compatibility even though polygons may have more than three vertices.
        ``active_motif`` and ``metrics`` are included to ease round‑tripping via
        JSON helpers.
        """

        return {
            "triangles": self.triangles,
            "colors": self.colors,
            "active_motif": self.active_motif,
            "metrics": self.metrics or {},
            "resonance_metrics": self.resonance_metrics or {},
            "prototypes": self.prototypes or [],
            "proof_log": self.proof_log or [],
        }

    @classmethod
    def from_hlsf(cls, data: Dict[str, Any]) -> "HLSFState":
        """Construct a :class:`HLSFState` from a JSON-compatible mapping.

        Parameters
        ----------
        data:
            Mapping produced by :meth:`to_hlsf` or equivalent JSON document.

        Missing keys are replaced with sensible defaults so that older schema
        versions remain loadable.  ``triangles`` and ``colors`` default to empty
        lists which mirrors the behaviour of :meth:`to_hlsf`.
        """

        return cls(
            triangles=list(data.get("triangles", [])),
            colors=list(data.get("colors", [])),
            active_motif=data.get("active_motif"),
            metrics=data.get("metrics"),
            resonance_metrics=data.get("resonance_metrics"),
            prototypes=data.get("prototypes"),
            proof_log=data.get("proof_log"),
        )


MappingStrategy = Callable[
    [int, int, Dict[str, float]], Tuple[List[List[float]], List[float]]
]


MAPPING_STRATEGIES: Dict[str, MappingStrategy] = {}


def register_mapper(name: str, mapper: MappingStrategy) -> None:
    """Register ``mapper`` under ``name`` for reuse."""

    MAPPING_STRATEGIES[name] = mapper


def _triangle_mapper(
    idx: int, total: int, metrics: Dict[str, float]
) -> Tuple[List[List[float]], List[float]]:
    """Map metrics to an oriented triangle with basic colouring."""

    scale = metrics.get("scale", 0.0)
    phase = metrics.get("phase", 0.0)
    centroid = metrics.get("centroid", 0.0)
    angle = 2 * math.pi * idx / total + 2 * math.pi * phase
    radial = scale * (1.0 + centroid)
    cx, cy = math.cos(angle) * radial, math.sin(angle) * radial
    tri = [
        [cx, cy + 0.05 * scale],
        [cx - 0.0433 * scale, cy - 0.025 * scale],
        [cx + 0.0433 * scale, cy - 0.025 * scale],
    ]
    color = [idx / total, 0.2 + 0.6 * phase, 0.8 * scale, 0.8]
    return tri, color


# Register the default strategy
register_mapper("triangle", _triangle_mapper)


def _square_mapper(
    idx: int, total: int, metrics: Dict[str, float]
) -> Tuple[List[List[float]], List[float]]:
    """Map metrics to a centred square."""

    scale = metrics.get("scale", 0.0)
    phase = metrics.get("phase", 0.0)
    centroid = metrics.get("centroid", 0.0)
    angle = 2 * math.pi * idx / total + 2 * math.pi * phase
    radial = scale * (1.0 + centroid)
    cx, cy = math.cos(angle) * radial, math.sin(angle) * radial
    half = 0.05 * scale
    sq = [
        [cx - half, cy - half],
        [cx - half, cy + half],
        [cx + half, cy + half],
        [cx + half, cy - half],
    ]
    color = [idx / total, 0.2 + 0.6 * phase, 0.6 * scale, 0.8]
    return sq, color


def _pentagon_mapper(
    idx: int, total: int, metrics: Dict[str, float]
) -> Tuple[List[List[float]], List[float]]:
    """Map metrics to a regular pentagon."""

    scale = metrics.get("scale", 0.0)
    phase = metrics.get("phase", 0.0)
    centroid = metrics.get("centroid", 0.0)
    angle = 2 * math.pi * idx / total + 2 * math.pi * phase
    radial = scale * (1.0 + centroid)
    cx, cy = math.cos(angle) * radial, math.sin(angle) * radial
    r = 0.06 * scale
    pts: List[List[float]] = []
    for i in range(5):
        a = angle + 2 * math.pi * i / 5
        pts.append([cx + r * math.cos(a), cy + r * math.sin(a)])
    color = [idx / total, 0.4 + 0.4 * phase, 0.7 * scale, 0.8]
    return pts, color


def _radial_bar_mapper(
    idx: int, total: int, metrics: Dict[str, float]
) -> Tuple[List[List[float]], List[float]]:
    """Map metrics to a thin radial bar extending from the origin."""

    scale = metrics.get("scale", 0.0)
    phase = metrics.get("phase", 0.0)
    centroid = metrics.get("centroid", 0.0)
    angle = 2 * math.pi * idx / total + 2 * math.pi * phase
    radial = scale * (1.0 + centroid)
    width = 0.02 * scale
    dx, dy = math.cos(angle), math.sin(angle)
    ox, oy = -dy * width / 2, dx * width / 2
    bar = [
        [ox, oy],
        [-ox, -oy],
        [-ox + dx * radial, -oy + dy * radial],
        [ox + dx * radial, oy + dy * radial],
    ]
    color = [idx / total, 0.2 + 0.6 * phase, scale, 0.8]
    return bar, color


def _pyramid_mapper(
    idx: int, total: int, metrics: Dict[str, float]
) -> Tuple[List[List[float]], List[float]]:
    """Map metrics to a small 3‑D pyramid."""

    scale = metrics.get("scale", 0.0)
    phase = metrics.get("phase", 0.0)
    centroid = metrics.get("centroid", 0.0)
    angle = 2 * math.pi * idx / total + 2 * math.pi * phase
    radial = scale * (1.0 + centroid)
    cx, cy = math.cos(angle) * radial, math.sin(angle) * radial
    half = 0.04 * scale
    base = [
        [cx - half, cy - half, 0.0],
        [cx - half, cy + half, 0.0],
        [cx + half, cy + half, 0.0],
        [cx + half, cy - half, 0.0],
    ]
    apex = [cx, cy, 0.08 * scale]
    color = [idx / total, 0.2 + 0.6 * phase, 0.9 * scale, 0.8]
    return base + [apex], color


# Register additional strategies
register_mapper("square", _square_mapper)
register_mapper("pentagon", _pentagon_mapper)
register_mapper("bar", _radial_bar_mapper)
register_mapper("pyramid", _pyramid_mapper)


class TensorMapper:
    """Collect token metrics and map them to simple geometric primitives."""

    def _default_mapper(
        self, idx: int, total: int, metrics: Dict[str, float]
    ) -> Tuple[List[List[float]], List[float]]:
        return _triangle_mapper(idx, total, metrics)

    def __init__(
        self,
        mapper: str | MappingStrategy | None = None,
        *,
        use_gpu: bool = False,
        device: str | None = None,
        backend: str | None = None,
        mapping_strategy: str | None = None,
        rh_mode: bool = False,
    ) -> None:
        """Initialise the mapper.

        Parameters
        ----------
        mapper:
            Optional mapping callback used to convert band metrics to geometry
            and colour information.  When ``None`` a simple triangle mapper is
            used.
        use_gpu:
            Attempt to use a GPU backend for accumulation when available.
        device:
            Optional device string for the GPU backend.
        backend:
            Explicitly select ``"torch"`` or ``"cupy"``.  When ``None`` the
            first available backend is chosen.
        """

        # Store per-band metrics such as weight, phase, centroid etc.
        # ``graph`` previously only accumulated weight; the structure is now a
        # dictionary keyed by band with metric dictionaries as values.
        self.graph: Dict[int, Dict[str, float]] = {}
        # Map ``(modality, token_id)`` pairs to band indices so that tokens from
        # different modalities do not collide even if they share the same
        # identifier.  This allows callers to mix text, audio and image tokens
        # without merging their metric accumulators.
        self._id_to_band: Dict[Tuple[str, int], int] = {}
        self._next_band: int = 1
        # Allow callers to override the mapping strategy.  The strategy receives
        # the band index, total band count and a metrics dictionary and returns a
        # pair of ``(polygon, colour)``.
        if mapper is not None:
            if isinstance(mapper, str):
                self._mapper = MAPPING_STRATEGIES[mapper]
            else:
                self._mapper = mapper
        elif rh_mode or (mapping_strategy and mapping_strategy.lower() == "rh"):
            from .rh_mapping import rh_mapper

            self._mapper = rh_mapper
        else:
            self._mapper = _triangle_mapper
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

    def _default_mapper(
        self, idx: int, total: int, metrics: Dict[str, float]
    ) -> Tuple[List[List[float]], List[float]]:
        """Fallback mapping strategy using simple triangles."""

        return _triangle_mapper(idx, total, metrics)

    def update(self, tokens: Iterable[SymbolToken]) -> None:
        """Accumulate metrics from ``SymbolToken`` instances.

        Parameters
        ----------
        tokens : Iterable[SymbolToken]
            Tokens containing modality ``mod`` and identifier ``id`` fields.
            Optional ``w`` or ``feat`` entries such as ``mag``, ``phase`` and
            ``centroid`` contribute to the accumulated metrics.

        Returns
        -------
        None

        Side Effects
        ------------
        Updates :attr:`graph` with aggregated metrics and maintains an internal
        mapping of ``(modality, id)`` pairs to band indices.  New bands are
        assigned incrementally via ``_next_band``.
        """
        if self.use_gpu and self.backend == "torch" and self._torch is not None:
            bands: List[int] = []
            weights: List[float] = []
            phases: List[float] = []
            phase_mask: List[float] = []
            cents: List[float] = []
            cent_mask: List[float] = []
            harmonics: List[float] = []
            harm_mask: List[float] = []
            primes: List[float] = []
            prime_mask: List[float] = []
            kdevs: List[float] = []
            kdev_mask: List[float] = []
            for t in tokens:
                key = (t.mod, t.id)
                if key not in self._id_to_band:
                    self._id_to_band[key] = self._next_band
                    self._next_band += 1
                band = self._id_to_band[key]
                bands.append(band)
                weights.append(t.w if t.w else float(t.feat.get("mag", 0.0)))
                ph = t.feat.get("phase")
                phases.append(float(ph) if ph is not None else 0.0)
                phase_mask.append(1.0 if ph is not None else 0.0)
                ce = t.feat.get("centroid")
                cents.append(float(ce) if ce is not None else 0.0)
                cent_mask.append(1.0 if ce is not None else 0.0)
                h = t.feat.get("harmonic")
                harmonics.append(float(h) if h is not None else 0.0)
                harm_mask.append(1.0 if h is not None else 0.0)
                pc = t.feat.get("prime_channel")
                primes.append(float(pc) if pc is not None else 0.0)
                prime_mask.append(1.0 if pc is not None else 0.0)
                kd = t.feat.get("K_dev")
                kdevs.append(float(kd) if kd is not None else 0.0)
                kdev_mask.append(1.0 if kd is not None else 0.0)
            if bands:
                b_t = self._torch.tensor(bands, dtype=self._torch.long, device=self.device)
                w_t = self._torch.tensor(weights, device=self.device)
                p_t = self._torch.tensor(phases, device=self.device)
                pm_t = self._torch.tensor(phase_mask, device=self.device)
                c_t = self._torch.tensor(cents, device=self.device)
                cm_t = self._torch.tensor(cent_mask, device=self.device)
                h_t = self._torch.tensor(harmonics, device=self.device)
                hm_t = self._torch.tensor(harm_mask, device=self.device)
                pc_t = self._torch.tensor(primes, device=self.device)
                pcm_t = self._torch.tensor(prime_mask, device=self.device)
                kd_t = self._torch.tensor(kdevs, device=self.device)
                kdm_t = self._torch.tensor(kdev_mask, device=self.device)
                unique = self._torch.unique(b_t)
                for b in unique.tolist():
                    idx = b_t == b

                    metrics = self.graph.setdefault(
                        b,
                        {
                            "weight": 0.0,
                            "phase": 0.0,
                            "phase_count": 0.0,
                            "centroid": 0.0,
                            "centroid_count": 0.0,
                            "harmonic": 0.0,
                            "harmonic_count": 0.0,
                            "prime_channel": 0.0,
                            "prime_channel_count": 0.0,
                            "K_dev": 0.0,
                            "K_dev_count": 0.0,
                        },
                    )
                    metrics["weight"] += w_t[idx].sum().item()
                    metrics["phase"] += p_t[idx].sum().item()
                    metrics["phase_count"] += pm_t[idx].sum().item()
                    metrics["centroid"] += c_t[idx].sum().item()
                    metrics["centroid_count"] += cm_t[idx].sum().item()
                    metrics["harmonic"] += h_t[idx].sum().item()
                    metrics["harmonic_count"] += hm_t[idx].sum().item()
                    metrics["prime_channel"] += pc_t[idx].sum().item()
                    metrics["prime_channel_count"] += pcm_t[idx].sum().item()
                    metrics["K_dev"] += kd_t[idx].sum().item()
                    metrics["K_dev_count"] += kdm_t[idx].sum().item()
        elif self.use_gpu and self.backend == "cupy" and self._cupy is not None:
            bands: List[int] = []
            weights: List[float] = []
            phases: List[float] = []
            phase_mask: List[float] = []
            cents: List[float] = []
            cent_mask: List[float] = []
            harmonics: List[float] = []
            harm_mask: List[float] = []
            primes: List[float] = []
            prime_mask: List[float] = []
            kdevs: List[float] = []
            kdev_mask: List[float] = []
            for t in tokens:
                key = (t.mod, t.id)
                if key not in self._id_to_band:
                    self._id_to_band[key] = self._next_band
                    self._next_band += 1
                band = self._id_to_band[key]
                bands.append(band)
                weights.append(t.w if t.w else float(t.feat.get("mag", 0.0)))
                ph = t.feat.get("phase")
                phases.append(float(ph) if ph is not None else 0.0)
                phase_mask.append(1.0 if ph is not None else 0.0)
                ce = t.feat.get("centroid")
                cents.append(float(ce) if ce is not None else 0.0)
                cent_mask.append(1.0 if ce is not None else 0.0)
                h = t.feat.get("harmonic")
                harmonics.append(float(h) if h is not None else 0.0)
                harm_mask.append(1.0 if h is not None else 0.0)
                pc = t.feat.get("prime_channel")
                primes.append(float(pc) if pc is not None else 0.0)
                prime_mask.append(1.0 if pc is not None else 0.0)
                kd = t.feat.get("K_dev")
                kdevs.append(float(kd) if kd is not None else 0.0)
                kdev_mask.append(1.0 if kd is not None else 0.0)
            if bands:
                cp = self._cupy
                b_t = cp.array(bands, dtype=cp.int64)
                w_t = cp.array(weights)
                p_t = cp.array(phases)
                pm_t = cp.array(phase_mask)
                c_t = cp.array(cents)
                cm_t = cp.array(cent_mask)
                h_t = cp.array(harmonics)
                hm_t = cp.array(harm_mask)
                pc_t = cp.array(primes)
                pcm_t = cp.array(prime_mask)
                kd_t = cp.array(kdevs)
                kdm_t = cp.array(kdev_mask)
                unique = cp.unique(b_t)
                for b in unique.tolist():
                    idx = b_t == b
                    metrics = self.graph.setdefault(
                        b,
                        {
                            "weight": 0.0,
                            "phase": 0.0,
                            "phase_count": 0.0,
                            "centroid": 0.0,
                            "centroid_count": 0.0,
                            "harmonic": 0.0,
                            "harmonic_count": 0.0,
                            "prime_channel": 0.0,
                            "prime_channel_count": 0.0,
                            "K_dev": 0.0,
                            "K_dev_count": 0.0,
                        },
                    )
                    metrics["weight"] += float(cp.asnumpy(w_t[idx].sum()))
                    metrics["phase"] += float(cp.asnumpy(p_t[idx].sum()))
                    metrics["phase_count"] += float(cp.asnumpy(pm_t[idx].sum()))
                    metrics["centroid"] += float(cp.asnumpy(c_t[idx].sum()))
                    metrics["centroid_count"] += float(cp.asnumpy(cm_t[idx].sum()))
                    metrics["harmonic"] += float(cp.asnumpy(h_t[idx].sum()))
                    metrics["harmonic_count"] += float(cp.asnumpy(hm_t[idx].sum()))
                    metrics["prime_channel"] += float(cp.asnumpy(pc_t[idx].sum()))
                    metrics["prime_channel_count"] += float(cp.asnumpy(pcm_t[idx].sum()))
                    metrics["K_dev"] += float(cp.asnumpy(kd_t[idx].sum()))
                    metrics["K_dev_count"] += float(cp.asnumpy(kdm_t[idx].sum()))
        else:
            bands: List[int] = []
            weights: List[float] = []
            phases: List[float] = []
            phase_mask: List[float] = []
            cents: List[float] = []
            cent_mask: List[float] = []
            for t in tokens:
                key = (t.mod, t.id)
                if key not in self._id_to_band:
                    self._id_to_band[key] = self._next_band
                    self._next_band += 1
                band = self._id_to_band[key]
                weight = t.w if t.w else float(t.feat.get("mag", 0.0))
                metrics = self.graph.setdefault(
                    band,
                    {
                        "weight": 0.0,
                        "phase": 0.0,
                        "phase_count": 0.0,
                        "centroid": 0.0,
                        "centroid_count": 0.0,
                        "harmonic": 0.0,
                        "harmonic_count": 0.0,
                        "prime_channel": 0.0,
                        "prime_channel_count": 0.0,
                        "K_dev": 0.0,
                        "K_dev_count": 0.0,
                    },
                )
                metrics["weight"] += weight
                if "phase" in t.feat:
                    metrics["phase"] += float(t.feat.get("phase", 0.0))
                    metrics["phase_count"] += 1
                if "centroid" in t.feat:
                    metrics["centroid"] += float(t.feat.get("centroid", 0.0))
                    metrics["centroid_count"] += 1
                if "harmonic" in t.feat:
                    metrics["harmonic"] += float(t.feat.get("harmonic", 0.0))
                    metrics["harmonic_count"] += 1
                if "prime_channel" in t.feat:
                    metrics["prime_channel"] += float(t.feat.get("prime_channel", 0.0))
                    metrics["prime_channel_count"] += 1
                if "K_dev" in t.feat:
                    metrics["K_dev"] += float(t.feat.get("K_dev", 0.0))
                    metrics["K_dev_count"] += 1
                if "embedding" in t.feat:
                    emb = t.feat.get("embedding", [])
                    store = metrics.setdefault("embedding", [0.0] * len(emb))
                    if len(store) < len(emb):
                        store.extend([0.0] * (len(emb) - len(store)))
                    for i, val in enumerate(emb):
                        store[i] += float(val)
                    metrics["embedding_count"] = metrics.get("embedding_count", 0.0) + 1

    def symbolic_resonance_index(self) -> float:
        """Return an embedding-based resonance index when available."""

        if not self.graph:
            return 0.0

        # Group averaged embeddings by token ``id`` across modalities.
        id_embeddings: Dict[int, Dict[str, List[float]]] = {}
        for (mod, tok_id), band in self._id_to_band.items():
            metrics = self.graph.get(band)
            if not metrics or "embedding" not in metrics:
                continue
            count = metrics.get("embedding_count", 1)
            emb = [v / count for v in metrics["embedding"]]
            id_embeddings.setdefault(tok_id, {})[mod] = emb

        sims: List[float] = []
        for mod_emb in id_embeddings.values():
            mods = list(mod_emb.keys())
            if len(mods) < 2:
                continue
            for i in range(len(mods)):
                for j in range(i + 1, len(mods)):
                    a = mod_emb[mods[i]]
                    b = mod_emb[mods[j]]
                    dot = sum(x * y for x, y in zip(a, b))
                    norm_a = math.sqrt(sum(x * x for x in a))
                    norm_b = math.sqrt(sum(x * x for x in b))
                    if norm_a and norm_b:
                        sims.append(dot / (norm_a * norm_b))
        if sims:
            return sum(sims) / len(sims)

        mags = [
            abs(v) if isinstance(v, (int, float)) else abs(float(v.get("weight", 0.0)))
            for v in self.graph.values()
        ]
        return sum(mags) / len(mags)

    def to_hlsf(self) -> HLSFState:
        # ``graph`` is treated as read‑only to keep this method pure so that
        # multiple invocations yield identical results.
        bands = sorted(self.graph)
        tris: List[List[List[float]]] = []
        colors: List[List[float]] = []
        n = len(bands) or 1
        max_w = max((abs(self.graph[b]["weight"]) for b in bands), default=1.0)
        for i, b in enumerate(bands):
            raw = self.graph[b]
            weight = abs(raw.get("weight", 0.0))
            scale = weight / max_w if max_w else 0.0
            phase = raw["phase"] / raw["phase_count"] if raw.get("phase_count") else 0.0
            centroid = (
                raw["centroid"] / raw["centroid_count"]
                if raw.get("centroid_count")
                else 0.0
            )
            harmonic = (
                raw["harmonic"] / raw["harmonic_count"]
                if raw.get("harmonic_count")
                else i
            )
            prime_channel = (
                raw["prime_channel"] / raw["prime_channel_count"]
                if raw.get("prime_channel_count")
                else 0.0
            )
            k_dev = (
                raw["K_dev"] / raw["K_dev_count"]
                if raw.get("K_dev_count")
                else None
            )
            metrics = {
                "weight": weight,
                "scale": scale,
                "phase": phase,
                "centroid": centroid,
                "harmonic": harmonic,
                "prime_channel": prime_channel,
            }
            if k_dev is not None:
                metrics["K_dev"] = k_dev
            poly, colour = self._mapper(i, n, metrics)
            tris.append(poly)
            colors.append(colour)
        return HLSFState(tris, colors, active_motif=bands[0] if bands else None)

    def triangle_count(self) -> int:
        """Return the number of bands currently tracked."""

        return len(self.graph)

    # ------------------------------------------------------------------
    # Default mapping
    def _default_mapper(
        self, band: int, n: int, metrics: Dict[str, float]
    ) -> Tuple[Polygon, Color]:
        """Fallback mapping strategy producing a simple triangle."""

        w = metrics.get("weight", 0.0)
        tri: Polygon = [(band, 0.0), (band + 0.5, w), (band + 1.0, 0.0)]
        color: Color = [0.0, 0.0, 1.0, min(1.0, w)]
        return tri, color

    # ------------------------------------------------------------------
    # Mapping strategies
    # ------------------------------------------------------------------
    def set_mapper(
        self, mapper: str | MappingStrategy, *, name: str | None = None
    ) -> None:
        """Select or register a mapping strategy.

        Parameters
        ----------
        mapper:
            Either a callable implementing :class:`MappingStrategy` or the name
            of a previously registered strategy.
        name:
            When ``mapper`` is a callable, registers it under this name before
            use.
        """

        if isinstance(mapper, str):
            self._mapper = MAPPING_STRATEGIES[mapper]
        else:
            if name:
                register_mapper(name, mapper)
            self._mapper = mapper

    def _default_mapper(
        self, idx: int, total: int, metrics: Dict[str, float]
    ) -> Tuple[List[List[float]], List[float]]:
        """Fallback mapper used when no explicit strategy is provided."""

        return MAPPING_STRATEGIES["triangle"](idx, total, metrics)
