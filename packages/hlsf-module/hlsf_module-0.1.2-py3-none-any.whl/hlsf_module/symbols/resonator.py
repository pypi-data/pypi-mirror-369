from __future__ import annotations

"""Modal symbol resonance with learnable modality weights."""

from typing import Dict, Iterable, List, Mapping


class SymbolResonator:
    """Resonate input vectors against modality prototypes.

    Each modality owns a set of prototype vectors.  During :meth:`resonance`
    we compute a score for every modality and return a weighted combination of
    those scores.  The weights are learnable through :meth:`train` which uses a
    simple delta rule to fit the weights to a target output.
    """

    def __init__(
        self,
        prototypes: Mapping[str, Iterable[Iterable[float]]],
        weights: Mapping[str, float] | None = None,
    ) -> None:
        # Normalise prototypes into lists for mutability and repeated access.
        self.prototypes: Dict[str, List[List[float]]] = {
            mod: [list(p) for p in protos] for mod, protos in prototypes.items()
        }
        # Default every modality weight to 1.0 if not provided.
        self.weights: Dict[str, float] = {
            mod: float(weights[mod]) if weights and mod in weights else 1.0
            for mod in self.prototypes
        }
        # Cache of per-modal scores from the most recent resonance call.
        self._last_scores: Dict[str, float] = {}

    def _modal_score(self, mod: str, vec: Iterable[float]) -> float:
        """Return the best (maximum dot product) score for ``mod``."""
        protos = self.prototypes.get(mod, [])
        if not protos:
            return 0.0
        vec_l = list(vec)
        best = max(
            sum(v * p for v, p in zip(vec_l, proto)) for proto in protos
        )
        return best

    def resonance(self, inputs: Mapping[str, Iterable[float]]) -> float:
        """Compute the weighted resonance for provided modality vectors."""
        scores: Dict[str, float] = {}
        for mod, vec in inputs.items():
            scores[mod] = self._modal_score(mod, vec)
        # Store for training use and return weighted sum.
        self._last_scores = scores
        return sum(self.weights.get(m, 0.0) * s for m, s in scores.items())

    def train(
        self,
        inputs: Mapping[str, Iterable[float]],
        target: float,
        lr: float = 0.1,
    ) -> float:
        """Update modality weights towards ``target`` and return the error."""
        pred = self.resonance(inputs)
        error = target - pred
        for mod, score in self._last_scores.items():
            self.weights[mod] = self.weights.get(mod, 0.0) + lr * error * score
        return error
