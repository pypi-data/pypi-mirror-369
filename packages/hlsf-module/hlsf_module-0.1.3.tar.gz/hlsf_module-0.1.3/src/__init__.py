"""Compatibility wrapper exposing ``hlsf_module`` as ``src``.

Some tests expect the project to be importable as ``src``.  This module simply
re-exports everything from :mod:`hlsf_module` and shares its module search
path so that ``import src.foo`` resolves to ``hlsf_module.foo``.
"""

from importlib import import_module

_mod = import_module("hlsf_module")

globals().update(_mod.__dict__)
__all__ = getattr(_mod, "__all__", [])
__path__ = _mod.__path__
