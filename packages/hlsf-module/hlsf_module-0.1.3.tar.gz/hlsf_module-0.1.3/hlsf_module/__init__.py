"""High-Level Space Field toolkit."""

from importlib.metadata import PackageNotFoundError, version

from .trainer import Trainer

try:
    __version__ = version("hlsf_module")
except PackageNotFoundError:
    __version__ = "0.1.3"

__all__ = ["Trainer", "__version__"]
