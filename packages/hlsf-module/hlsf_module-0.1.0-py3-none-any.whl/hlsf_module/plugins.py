"""Plugin interfaces and registration utilities.

This module defines lightweight protocols for core extension points and a
simple registry based discovery mechanism.  External packages can expose
implementations via ``importlib.metadata`` entry points using the following
groups:

``hlsf.encoders``
    Implementations of :class:`Encoder`.
``hlsf.mappers``
    Implementations of :class:`Mapper`.
``hlsf.gaters``
    Implementations of :class:`Gater`.
``hlsf.visualizers``
    Implementations of :class:`Visualizer`.

Packages may also register plugins manually at import time by calling the
``register_*`` functions.
"""

from __future__ import annotations

from importlib import metadata
from typing import Any, Dict, Protocol, Type, runtime_checkable

# ---------------------------------------------------------------------------
# Protocol definitions


@runtime_checkable
class Encoder(Protocol):
    """Protocol for token encoders."""

    name: str

    def encode(self, *args: Any, **kwargs: Any) -> Any:
        """Encode an input into tokens."""


@runtime_checkable
class Mapper(Protocol):
    """Protocol for mapping tokens into geometry or other structures."""

    name: str

    def map(self, *args: Any, **kwargs: Any) -> Any:
        """Map tokens into an output representation."""


@runtime_checkable
class Gater(Protocol):
    """Protocol for gating decisions."""

    name: str

    def decide(self, *args: Any, **kwargs: Any) -> Any:
        """Return a gating decision."""


@runtime_checkable
class Visualizer(Protocol):
    """Protocol for visualisation front-ends."""

    name: str

    def visualize(self, *args: Any, **kwargs: Any) -> Any:
        """Visualise the provided state."""


# ---------------------------------------------------------------------------
# Registries


_encoders: Dict[str, Type[Encoder]] = {}
_mappers: Dict[str, Type[Mapper]] = {}
_gaters: Dict[str, Type[Gater]] = {}
_visualizers: Dict[str, Type[Visualizer]] = {}

# Disabled plugins are kept separately so they can be re-enabled later without
# re-importing their defining packages.  ``load_plugins`` will honour these sets
# when refreshing entry point discovery.
_disabled_encoders: Dict[str, Type[Encoder]] = {}
_disabled_mappers: Dict[str, Type[Mapper]] = {}
_disabled_gaters: Dict[str, Type[Gater]] = {}
_disabled_visualizers: Dict[str, Type[Visualizer]] = {}


def register_encoder(name: str, cls: Type[Encoder]) -> None:
    """Register an :class:`Encoder` implementation under ``name``."""

    if name in _disabled_encoders:
        _disabled_encoders[name] = cls
    else:
        _encoders[name] = cls


def register_mapper(name: str, cls: Type[Mapper]) -> None:
    """Register a :class:`Mapper` implementation under ``name``."""

    if name in _disabled_mappers:
        _disabled_mappers[name] = cls
    else:
        _mappers[name] = cls


def register_gater(name: str, cls: Type[Gater]) -> None:
    """Register a :class:`Gater` implementation under ``name``."""

    if name in _disabled_gaters:
        _disabled_gaters[name] = cls
    else:
        _gaters[name] = cls


def register_visualizer(name: str, cls: Type[Visualizer]) -> None:
    """Register a :class:`Visualizer` implementation under ``name``."""

    if name in _disabled_visualizers:
        _disabled_visualizers[name] = cls
    else:
        _visualizers[name] = cls


# ---------------------------------------------------------------------------
# Registry helpers


def get_encoder(name: str) -> Type[Encoder]:
    return _encoders[name]


def get_mapper(name: str) -> Type[Mapper]:
    return _mappers[name]


def get_gater(name: str) -> Type[Gater]:
    return _gaters[name]


def get_visualizer(name: str) -> Type[Visualizer]:
    return _visualizers[name]


def available_plugins() -> Dict[str, Dict[str, Type[Any]]]:
    """Return a mapping of plugin types to registered implementations."""

    return {
        "encoders": dict(_encoders),
        "mappers": dict(_mappers),
        "gaters": dict(_gaters),
        "visualizers": dict(_visualizers),
    }


def disable(name: str) -> None:
    """Disable the plugin with ``name`` regardless of its type."""

    for reg, disabled in [
        (_encoders, _disabled_encoders),
        (_mappers, _disabled_mappers),
        (_gaters, _disabled_gaters),
        (_visualizers, _disabled_visualizers),
    ]:
        if name in reg:
            disabled[name] = reg.pop(name)
            return
    raise KeyError(name)


def enable(name: str) -> None:
    """Re-enable a previously disabled plugin with ``name``."""

    for reg, disabled in [
        (_encoders, _disabled_encoders),
        (_mappers, _disabled_mappers),
        (_gaters, _disabled_gaters),
        (_visualizers, _disabled_visualizers),
    ]:
        if name in disabled:
            reg[name] = disabled.pop(name)
            return
    raise KeyError(name)


# ---------------------------------------------------------------------------
# Discovery


def _iter_entry_points(group: str):
    """Yield entry points for ``group`` across Python versions."""

    try:
        eps = metadata.entry_points()  # type: ignore[attr-defined]
    except Exception:  # pragma: no cover - importlib metadata failure
        return []

    # Python 3.10+ exposes ``select``.  Older versions use dict access.
    if hasattr(eps, "select"):
        return eps.select(group=group)  # type: ignore[call-arg]
    return eps.get(group, [])  # type: ignore[return-value]


def load_plugins() -> None:
    """Discover and register plugins exposed via entry points."""

    groups = {
        "hlsf.encoders": (_encoders, _disabled_encoders),
        "hlsf.mappers": (_mappers, _disabled_mappers),
        "hlsf.gaters": (_gaters, _disabled_gaters),
        "hlsf.visualizers": (_visualizers, _disabled_visualizers),
    }

    for group, (registry, disabled) in groups.items():
        for ep in _iter_entry_points(group):
            if ep.name in registry or ep.name in disabled:
                continue
            try:
                obj = ep.load()
            except Exception:  # pragma: no cover - third-party failures
                continue
            registry[ep.name] = obj


# Automatically load any entry-point plugins on import
load_plugins()

