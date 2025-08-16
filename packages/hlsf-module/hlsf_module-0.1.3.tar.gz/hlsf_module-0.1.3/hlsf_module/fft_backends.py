import os
import math
import cmath
import logging
from functools import lru_cache
from itertools import product
from typing import Dict, List, Tuple

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Backend selection
# ---------------------------------------------------------------------------
_backend_env = os.getenv("HLSF_GPU_BACKEND", "").lower()

try:  # pragma: no cover
    import numpy as _np  # type: ignore
except ImportError:  # pragma: no cover
    _np = None

try:  # pragma: no cover
    from scipy.fft import fftn as _scipy_fftn, rfft as _scipy_rfft  # type: ignore
except ImportError:  # pragma: no cover
    _scipy_fftn = None
    _scipy_rfft = None

try:  # pragma: no cover
    import torch as _torch  # type: ignore
except ImportError:  # pragma: no cover
    _torch = None

try:  # pragma: no cover
    import cupy as _cupy  # type: ignore
except ImportError:  # pragma: no cover
    _cupy = None

try:  # pragma: no cover
    import jax.numpy as _jnp  # type: ignore
    from jax import device_get as _jax_device_get  # type: ignore
except ImportError:  # pragma: no cover
    _jnp = None
    _jax_device_get = None

_backend = "python"


def select_backend(requested: str | None = None, *, use_gpu: bool | None = None) -> str:
    """Select numerical backend for FFT operations.

    Parameters
    ----------
    requested:
        Explicit backend name such as ``"torch"`` or ``"cupy"``.  When ``None``
        the value of :envvar:`HLSF_GPU_BACKEND` is honoured.
    use_gpu:
        When ``True`` prefer GPU backends.  When ``False`` restrict selection to
        CPU libraries.  ``None`` considers all available options.
    """

    global _backend

    order: List[str] = []
    if requested or _backend_env:
        order.append((requested or _backend_env).lower())
    if use_gpu is True:
        order.extend(["torch", "cupy"])
    elif use_gpu is False:
        order.extend(["numpy", "scipy", "jax"])
    else:
        order.extend(["torch", "cupy", "numpy", "scipy", "jax"])

    for name in order:
        if name == "torch" and _torch is not None:
            _backend = "torch"
            break
        if name == "cupy" and _cupy is not None:
            _backend = "cupy"
            break
        if name == "numpy" and _np is not None:
            _backend = "numpy"
            break
        if name == "scipy" and _scipy_fftn is not None and _np is not None:
            _backend = "scipy"
            break
        if name == "jax" and _jnp is not None:
            _backend = "jax"
            break
    else:
        _backend = "python"

    logger.debug("FFT backend selected: %s", _backend)
    return _backend


# Initial backend resolution at import time
select_backend()

# ---------------------------------------------------------------------------
# Pure Python helpers
# ---------------------------------------------------------------------------

@lru_cache(maxsize=32)
def _get_twiddles(n: int) -> List[complex]:
    return [cmath.exp(-2j * math.pi * k / n) for k in range(n)]


def _mixed_radix_fft(x: List[complex]) -> List[complex]:
    N = len(x)
    spec: List[complex] = []
    for k in range(N):
        s = 0j
        for n, xn in enumerate(x):
            angle = -2j * math.pi * k * n / N
            s += xn * cmath.exp(angle)
        spec.append(s)
    return spec


def _rfft_python(frame: List[float], n_fft: int) -> List[complex]:
    N = n_fft
    padded = frame + [0.0] * (N - len(frame))
    if N & (N - 1):
        x = [complex(v, 0.0) for v in padded]
        spec = _mixed_radix_fft(x)
        return spec[: N // 2 + 1]
    table = _get_twiddles(N)
    x = [complex(v, 0.0) for v in padded]
    j = 0
    for i in range(1, N):
        bit = N >> 1
        while j & bit:
            j ^= bit
            bit >>= 1
        j ^= bit
        if i < j:
            x[i], x[j] = x[j], x[i]
    size = 2
    while size <= N:
        half = size // 2
        step = N // size
        for i in range(0, N, size):
            k = 0
            for j in range(i, i + half):
                twiddle = table[k]
                t = twiddle * x[j + half]
                x[j + half] = x[j] - t
                x[j] = x[j] + t
                k += step
        size *= 2
    return x[: N // 2 + 1]


@lru_cache(maxsize=128)
def _rfft_cached(frame: Tuple[float, ...], n_fft: int) -> List[complex]:
    """Cached wrapper around :func:`_rfft_python`.

    ``functools.lru_cache`` requires hashable arguments so the frame is
    represented as a tuple.  This helper is only used for the pure Python
    backend where repeated calls with identical input are common in tests.
    """

    return _rfft_python(list(frame), n_fft)


def _nd_dft_python(frame: List, n_fft: Tuple[int, ...]) -> Dict[Tuple[int, ...], complex]:
    dims = len(n_fft)

    def get_value(idx: Tuple[int, ...]) -> float:
        val = frame
        for i in idx:
            if isinstance(val, list) and i < len(val):
                val = val[i]
            else:
                return 0.0
        return float(val)

    spec: Dict[Tuple[int, ...], complex] = {}
    k_ranges = [range(n_fft[d] // 2 + 1) for d in range(dims)]
    n_ranges = [range(n_fft[d]) for d in range(dims)]
    for k in product(*k_ranges):
        s = 0j
        for n in product(*n_ranges):
            x = get_value(n)
            angle = -2 * math.pi * sum(k[d] * n[d] / n_fft[d] for d in range(dims))
            s += x * complex(math.cos(angle), math.sin(angle))
        spec[k] = s
    return spec


def _to_tuple(x):
    return tuple(_to_tuple(v) for v in x) if isinstance(x, list) else x


@lru_cache(maxsize=32)
def _nd_dft_cached(frame: Tuple, n_fft: Tuple[int, ...]) -> Dict[Tuple[int, ...], complex]:
    """Cached wrapper for :func:`_nd_dft_python` using tuple inputs."""

    def _to_list(v):
        return [_to_list(i) for i in v] if isinstance(v, tuple) else v

    return _nd_dft_python(_to_list(frame), n_fft)

# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def rfft(frame: List[float], n_fft: int) -> List[complex]:
    if _backend == "numpy" and _np is not None:
        arr = _np.array(frame, dtype=float)
        return [_np.complex128(v) for v in _np.fft.rfft(arr, n_fft)]
    if _backend == "scipy" and _scipy_rfft is not None and _np is not None:
        arr = _np.array(frame, dtype=float)
        return [_np.complex128(v) for v in _scipy_rfft(arr, n_fft)]
    if _backend == "torch" and _torch is not None:
        device = "cuda" if _torch.cuda.is_available() else "cpu"
        t = _torch.tensor(frame, dtype=_torch.float32, device=device)
        if t.numel() < n_fft:
            t = _torch.nn.functional.pad(t, (0, n_fft - t.numel()))
        spec = _torch.fft.rfft(t, n=n_fft)
        if device != "cpu":
            spec = spec.cpu()
        return [complex(v) for v in spec.numpy()]
    if _backend == "cupy" and _cupy is not None:
        arr = _cupy.array(frame, dtype=_cupy.float32)
        if arr.size < n_fft:
            arr = _cupy.pad(arr, (0, n_fft - arr.size))
        spec = _cupy.fft.rfft(arr, n_fft)
        return [complex(v) for v in _cupy.asnumpy(spec)]
    if _backend == "jax" and _jnp is not None and _jax_device_get is not None:
        arr = _jnp.array(frame, dtype=_jnp.float32)
        if arr.size < n_fft:
            arr = _jnp.pad(arr, (0, n_fft - arr.size))
        spec = _jnp.fft.rfft(arr, n_fft)
        spec_np = _jax_device_get(spec)
        return [complex(v) for v in spec_np]
    if _backend == "python":
        return _rfft_cached(tuple(frame), n_fft)
    return _rfft_python(frame, n_fft)


def nd_fft(frame: List, n_fft: Tuple[int, ...]) -> Dict[Tuple[int, ...], complex]:
    if _backend in {"numpy", "scipy"} and _np is not None:
        arr = _np.zeros(n_fft, dtype=float)
        def _fill(sub, idx: Tuple[int, ...]) -> None:
            if isinstance(sub, list):
                dim = len(idx)
                if dim >= len(n_fft):
                    return
                limit = n_fft[dim]
                for i, v in enumerate(sub):
                    if i < limit:
                        _fill(v, idx + (i,))
            else:
                arr[idx] = float(sub)
        _fill(frame, ())
        if _backend == "scipy" and _scipy_fftn is not None:
            spec_full = _scipy_fftn(arr, n_fft)
        else:
            spec_full = _np.fft.fftn(arr, n_fft)
        slices = tuple(slice(0, n_fft[d] // 2 + 1) for d in range(len(n_fft)))
        spec = spec_full[slices]
        out: Dict[Tuple[int, ...], complex] = {}
        for idx in _np.ndindex(spec.shape):
            out[tuple(idx)] = complex(spec[idx])
        return out
    if _backend == "torch" and _torch is not None:
        device = "cuda" if _torch.cuda.is_available() else "cpu"
        arr = _torch.zeros(n_fft, dtype=_torch.float32, device=device)
        def _fill(sub, idx: Tuple[int, ...]) -> None:
            if isinstance(sub, list):
                dim = len(idx)
                if dim >= len(n_fft):
                    return
                limit = n_fft[dim]
                for i, v in enumerate(sub):
                    if i < limit:
                        _fill(v, idx + (i,))
            else:
                arr[idx] = float(sub)
        _fill(frame, ())
        spec_full = _torch.fft.fftn(arr, s=n_fft)
        slices = tuple(slice(0, n_fft[d] // 2 + 1) for d in range(len(n_fft)))
        spec = spec_full[slices]
        if device != "cpu":
            spec = spec.cpu()
        spec_np = spec.numpy()
        out: Dict[Tuple[int, ...], complex] = {}
        for idx in _np.ndindex(spec_np.shape):  # type: ignore[arg-type]
            out[tuple(idx)] = complex(spec_np[idx])
        return out
    if _backend == "cupy" and _cupy is not None:
        arr = _cupy.zeros(n_fft, dtype=_cupy.float32)
        def _fill(sub, idx: Tuple[int, ...]) -> None:
            if isinstance(sub, list):
                dim = len(idx)
                if dim >= len(n_fft):
                    return
                limit = n_fft[dim]
                for i, v in enumerate(sub):
                    if i < limit:
                        _fill(v, idx + (i,))
            else:
                arr[idx] = float(sub)
        _fill(frame, ())
        spec_full = _cupy.fft.fftn(arr, s=n_fft)
        slices = tuple(slice(0, n_fft[d] // 2 + 1) for d in range(len(n_fft)))
        spec = spec_full[slices]
        spec_np = _cupy.asnumpy(spec)
        out: Dict[Tuple[int, ...], complex] = {}
        for idx in _np.ndindex(spec_np.shape):  # type: ignore[arg-type]
            out[tuple(idx)] = complex(spec_np[idx])
        return out
    if _backend == "jax" and _jnp is not None and _jax_device_get is not None:
        arr = _jnp.zeros(n_fft, dtype=_jnp.float32)
        def _fill(sub, idx: Tuple[int, ...]) -> None:
            if isinstance(sub, list):
                dim = len(idx)
                if dim >= len(n_fft):
                    return
                limit = n_fft[dim]
                for i, v in enumerate(sub):
                    if i < limit:
                        _fill(v, idx + (i,))
            else:
                arr = arr_at(idx, float(sub))  # type: ignore
        def arr_at(idx, value):
            nonlocal arr
            arr = arr.at[idx].set(value)
            return arr
        _fill(frame, ())
        spec_full = _jnp.fft.fftn(arr, n_fft)
        slices = tuple(slice(0, n_fft[d] // 2 + 1) for d in range(len(n_fft)))
        spec = spec_full[slices]
        spec_np = _jax_device_get(spec)
        out: Dict[Tuple[int, ...], complex] = {}
        for idx in _np.ndindex(spec_np.shape):  # type: ignore[arg-type]
            out[tuple(idx)] = complex(spec_np[idx])
        return out
    logger.warning(
        "No numerical backend available for FFT; falling back to slow pure Python implementation"
    )
    if _backend == "python":
        return _nd_dft_cached(_to_tuple(frame), n_fft)
    return _nd_dft_python(frame, n_fft)

# Expose python fallback for tests
nd_dft_python = _nd_dft_python
BACKEND = _backend
