from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict

from .agency_gates import decide
from .plugins import register_gater


@dataclass
class RHGate:
    """Lightweight gater delegating to :func:`agency_gates.decide`.

    The gate simply exposes a ``decide`` method compatible with the plugin
    interface.  It forwards all keyword arguments to
    :func:`agency_gates.decide` allowing callers to leverage existing
    thresholds and strategies.
    """

    name: str = "rh"

    def decide(self, motif: Dict[str, Any], **kwargs: Any) -> bool:  # pragma: no cover - simple delegate
        return decide(motif, **kwargs)


# register plugin at import time
register_gater("rh", RHGate)
