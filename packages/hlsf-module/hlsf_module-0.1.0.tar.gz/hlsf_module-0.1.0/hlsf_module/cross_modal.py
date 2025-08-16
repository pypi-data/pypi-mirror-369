from __future__ import annotations

"""Simple cross-modal embedding model for audio and text motifs."""

from dataclasses import dataclass
from typing import Iterable, List, Sequence, Tuple
import json
import math
import random


@dataclass
class CrossModalEmbedder:
    """Learn linear projections into a shared embedding space.

    The model maintains separate weight matrices for audio and text vectors.
    Training minimises the squared distance between paired embeddings using a
    very small stochastic gradient descent routine so that unit tests can train
    the model quickly without external dependencies.
    """

    audio_dim: int
    text_dim: int
    embed_dim: int = 8
    lr: float = 0.01

    def __post_init__(self) -> None:
        rnd = random.Random(0)
        self.audio_W = [[rnd.uniform(-0.1, 0.1) for _ in range(self.audio_dim)] for _ in range(self.embed_dim)]
        self.text_W = [[rnd.uniform(-0.1, 0.1) for _ in range(self.text_dim)] for _ in range(self.embed_dim)]

    def _matvec(self, W: Sequence[Sequence[float]], vec: Sequence[float]) -> List[float]:
        return [sum(w * v for w, v in zip(row, vec)) for row in W]

    def encode_audio(self, vec: Sequence[float]) -> List[float]:
        return self._matvec(self.audio_W, vec)

    def encode_text(self, vec: Sequence[float]) -> List[float]:
        return self._matvec(self.text_W, vec)

    # ------------------------------------------------------------------
    # Training utilities
    # ------------------------------------------------------------------
    def _train_pair(self, a_vec: Sequence[float], t_vec: Sequence[float]) -> None:
        a_emb = self.encode_audio(a_vec)
        t_emb = self.encode_text(t_vec)
        diff = [ae - te for ae, te in zip(a_emb, t_emb)]
        for i in range(self.embed_dim):
            for j in range(self.audio_dim):
                self.audio_W[i][j] -= self.lr * 2 * diff[i] * a_vec[j]
            for j in range(self.text_dim):
                self.text_W[i][j] += self.lr * 2 * diff[i] * t_vec[j]

    def train(self, pairs: Iterable[Tuple[Sequence[float], Sequence[float]]], epochs: int = 1) -> None:
        for _ in range(epochs):
            for a_vec, t_vec in pairs:
                self._train_pair(a_vec, t_vec)

    # ------------------------------------------------------------------
    # Similarity helpers and serialisation
    # ------------------------------------------------------------------
    def similarity(self, a_vec: Sequence[float], t_vec: Sequence[float]) -> float:
        a_emb = self.encode_audio(a_vec)
        t_emb = self.encode_text(t_vec)
        dot = sum(a * b for a, b in zip(a_emb, t_emb))
        norm_a = math.sqrt(sum(a * a for a in a_emb))
        norm_b = math.sqrt(sum(b * b for b in t_emb))
        if norm_a == 0.0 or norm_b == 0.0:
            return 0.0
        return dot / (norm_a * norm_b)

    def to_json(self) -> str:
        data = {"audio_W": self.audio_W, "text_W": self.text_W, "embed_dim": self.embed_dim,
                "audio_dim": self.audio_dim, "text_dim": self.text_dim}
        return json.dumps(data)

    @classmethod
    def from_json(cls, data: str, lr: float = 0.01) -> "CrossModalEmbedder":
        obj = json.loads(data)
        model = cls(obj["audio_dim"], obj["text_dim"], obj["embed_dim"], lr=lr)
        model.audio_W = obj["audio_W"]
        model.text_W = obj["text_W"]
        return model
