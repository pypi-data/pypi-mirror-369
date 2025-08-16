"""Lightweight LLM bridge for building a training database."""

from __future__ import annotations

from typing import Dict, Iterable, Tuple, Protocol, List
import time
from pathlib import Path
import json
import math

from .symbols.schema import SymbolToken


class WeightExtractor(Protocol):
    """Callable protocol returning a weight for two tokens."""

    def __call__(self, a: SymbolToken, b: SymbolToken) -> float:  # pragma: no cover - protocol
        ...


class CheapLLM:
    """Very small stand‑in for an external LLM service.

    The implementation deliberately keeps the logic simple so unit tests can run
    deterministically without network access.  By default it assigns weights
    using the cosine similarity of the token feature vectors.  Users may supply
    a custom ``weight_extractor`` callback to override this behaviour or select
    one of the built‑in strategies: temperature scaled cosine, softmax
    normalisation or contrastive loss.
    """

    def __init__(
        self,
        weight_extractor: WeightExtractor | None = None,
        *,
        strategy: str = "cosine",
        temperature: float = 1.0,
    ) -> None:
        self.weight_extractor = weight_extractor or self._embedding_weight
        self.strategy = strategy
        self.temperature = temperature

    def _embedding_weight(self, a: SymbolToken, b: SymbolToken) -> float:
        """Compute cosine similarity between two tokens' feature vectors."""

        if not a.feat or not b.feat:
            return 0.0
        shared_keys = set(a.feat) & set(b.feat)
        dot = sum(a.feat[k] * b.feat[k] for k in shared_keys)
        norm_a = math.sqrt(sum(v * v for v in a.feat.values()))
        norm_b = math.sqrt(sum(v * v for v in b.feat.values()))
        if norm_a == 0.0 or norm_b == 0.0:
            return 0.0
        return dot / (norm_a * norm_b)

    def extract(
        self,
        tokens: Iterable[SymbolToken],
        weight_extractor: WeightExtractor | None = None,
    ) -> Dict[Tuple[int, int], float]:
        token_list = list(tokens)
        extractor = weight_extractor or self.weight_extractor
        raw_scores: List[float] = []
        pair_index: List[Tuple[int, int]] = []
        for i, a in enumerate(token_list):
            for b in token_list[i + 1 :]:
                pair = tuple(sorted((a.id, b.id)))
                score = extractor(a, b)
                raw_scores.append(score)
                pair_index.append(pair)

        scores: List[float] = raw_scores
        if self.strategy in {"temperature", "softmax", "contrastive"}:
            scale = self.temperature if self.temperature != 0 else 1.0
            scores = [s / scale for s in raw_scores]
            if self.strategy in {"softmax", "contrastive"}:
                max_s = max(scores) if scores else 0.0
                exps = [math.exp(s - max_s) for s in scores]
                denom = sum(exps) or 1.0
                probs = [e / denom for e in exps]
                if self.strategy == "softmax":
                    scores = probs
                else:  # contrastive
                    scores = [-math.log(p) for p in probs]

        pairs: Dict[Tuple[int, int], float] = {}
        for pair, score in zip(pair_index, scores):
            pairs[pair] = pairs.get(pair, 0.0) + score
        return pairs


class TrainingDB:
    """In‑memory storage for weighted connections.

    Repeated updates accumulate weights for each token pair.
    """

    def __init__(self) -> None:
        self.connections: Dict[Tuple[int, int], float] = {}
        # Store adjacency edges as (src, dst, mod) -> (weight, timestamp)
        self.adj_edges: Dict[Tuple[int, int, str], Tuple[float, float]] = {}

    def update(
        self, tokens: Iterable[SymbolToken], llm: CheapLLM | None = None
    ) -> None:
        llm = llm or CheapLLM()
        weights = llm.extract(tokens)
        for pair, w in weights.items():
            self.connections[pair] = self.connections.get(pair, 0.0) + w

    def save(self, path: str | Path) -> None:
        """Persist database contents to ``path``.

        The JSON format stores a mapping with two keys: ``connections`` holding
        ``[a, b, w]`` triples and ``adjacency`` storing
        ``[a, b, mod, w, ts]`` entries.  The CSV format only writes the
        ``connections`` for backwards compatibility.
        """

        path = Path(path)
        if path.suffix.lower() == ".csv":
            import csv

            data = [[a, b, w] for (a, b), w in self.connections.items()]
            with open(path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["a", "b", "w"])
                writer.writerows(data)
        else:
            data = {
                "connections": [[a, b, w] for (a, b), w in self.connections.items()],
                "adjacency": [
                    [a, b, mod, w, ts] for (a, b, mod), (w, ts) in self.adj_edges.items()
                ],
            }
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f)

    def load(self, path: str | Path) -> None:
        """Load database contents from ``path`` overwriting current data."""

        path = Path(path)
        self.connections = {}
        self.adj_edges = {}
        if path.suffix.lower() == ".csv":
            import csv

            with open(path, "r", newline="", encoding="utf-8") as f:
                reader = csv.reader(f)
                for row in reader:
                    if not row or row[0] == "a":
                        continue
                    a, b, w = int(row[0]), int(row[1]), float(row[2])
                    self.connections[(a, b)] = w
        else:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, list):  # legacy format
                self.connections = {(a, b): w for a, b, w in data}
            else:
                self.connections = {
                    (a, b): w for a, b, w in data.get("connections", [])
                }
                self.adj_edges = {
                    (a, b, mod): (w, ts)
                    for a, b, mod, w, ts in data.get("adjacency", [])
                }

    def merge(self, *others: "TrainingDB") -> None:
        """Combine weights from *others* into this database.

        Existing weights are incremented; unseen pairs are added.  Duplicate
        entries therefore accumulate rather than multiply.
        """

        for other in others:
            for pair, weight in other.connections.items():
                self.connections[pair] = self.connections.get(pair, 0.0) + weight
            for key, (w, ts) in other.adj_edges.items():
                w0, _ = self.adj_edges.get(key, (0.0, ts))
                self.adj_edges[key] = (w0 + w, ts)

    # ------------------------------------------------------------------
    # Adjacency edge helpers
    # ------------------------------------------------------------------
    def add_edge(
        self,
        source: SymbolToken,
        target: SymbolToken,
        weight: float,
        *,
        timestamp: float | None = None,
    ) -> None:
        """Record an adjacency edge between ``source`` and ``target``."""

        key = (source.id, target.id, source.mod)
        ts = timestamp if timestamp is not None else time.time()
        prev, _ = self.adj_edges.get(key, (0.0, ts))
        self.adj_edges[key] = (prev + weight, ts)
