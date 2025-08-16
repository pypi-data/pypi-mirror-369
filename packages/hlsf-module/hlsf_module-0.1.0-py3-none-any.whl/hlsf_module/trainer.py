"""Training loop for mixed-modality datasets."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Iterable, Mapping, List, Tuple
import json

from .llm_weights import TrainingDB
from .weights_bp import update as bp_update
from .resonator import SymbolResonator
from .symbols.schema import SymbolToken

# Dataset items may be provided as a mapping of modality name to token
# iterables or as tuples ``(audio_tokens, text_tokens, image_tokens, ...)``
# which explicitly pair modalities together.
DatasetItem = Mapping[str, Iterable[SymbolToken]]
DatasetTuple = Tuple[Iterable[SymbolToken], ...]


@dataclass
class Trainer:
    """Coordinate updates across training components.

    Parameters
    ----------
    training_db:
        Optional :class:`~hlsf_module.llm_weights.TrainingDB` instance. A new
        database is created when ``None``.
    resonator:
        :class:`~hlsf_module.resonator.SymbolResonator` used to maintain
        per-token prototypes.
    weights_store:
        Mutable mapping updated via :func:`~hlsf_module.weights_bp.update`.
    """

    training_db: TrainingDB = field(default_factory=TrainingDB)
    resonator: SymbolResonator | None = None
    weights_store: Dict[int, Dict[str, float]] = field(default_factory=dict)
    use_gpu: bool = False
    device: str | None = None
    backend: str | None = None

    def __post_init__(self) -> None:
        if self.resonator is None:
            self.resonator = SymbolResonator(
                use_gpu=self.use_gpu, device=self.device, backend=self.backend
            )

    def train(
        self,
        dataset: Iterable[
            DatasetItem | DatasetTuple | Tuple[Iterable[SymbolToken], float]
        ],
        *,
        batch_size: int = 1,
        use_gpu: bool = False,
    ) -> None:
        """Iterate over ``dataset`` updating all training structures.

        Parameters
        ----------
        dataset:
            Iterable yielding either mappings of modality name to token sequences,
            tuples ``(audio_tokens, text_tokens, ...)`` to explicitly pair
            modalities or labelled samples ``(tokens, label)``.
        batch_size:
            Number of samples to accumulate before applying updates.
        use_gpu:
            When ``True`` and PyTorch is available, performs a gradient step on
            a tiny linear model for each labelled sample.
        """

        tokens_batch: List[SymbolToken] = []
        graph_batch: Dict[int, float] = {}
        band_counts: Dict[int, int] = {}
        batch_count = 0

        torch = None
        device = "cpu"
        if use_gpu:
            torch = self.resonator._torch
            if torch is None:
                import torch as _torch

                torch = _torch
            device = (
                self.resonator.device
                if getattr(self.resonator, "device", None)
                else "cuda" if torch.cuda.is_available() else "cpu"
            )
            if not hasattr(self, "_model"):
                self._model = torch.nn.Linear(1, 1).to(device)
                self._optim = torch.optim.SGD(self._model.parameters(), lr=0.01)
                self._loss_fn = torch.nn.MSELoss()

        for sample in dataset:
            label = None
            if (
                isinstance(sample, tuple)
                and len(sample) == 2
                and isinstance(sample[1], (int, float))
            ):
                tokens_part, label = sample
                if isinstance(tokens_part, Mapping):
                    token_groups = tokens_part.values()
                else:
                    token_groups = (tokens_part,)
            elif isinstance(sample, Mapping):
                token_groups = sample.values()
            else:
                token_groups = sample

            for tokens_iter in token_groups:
                tokens_list = list(tokens_iter)
                for tok in tokens_list:
                    tokens_batch.append(tok)
                    band = tok.feat.get("band")
                    if band is not None:
                        band_int = int(band)
                        graph_batch[band_int] = graph_batch.get(band_int, 0.0) + float(
                            tok.feat.get("mag", tok.w)
                        )
                        band_counts[band_int] = band_counts.get(band_int, 0) + 1
                    self.resonator.update(tok)

                if use_gpu and label is not None and torch is not None and tokens_list:
                    x_val = sum(float(t.w) for t in tokens_list) / len(tokens_list)
                    x = torch.tensor([[x_val]], device=device)
                    y = torch.tensor([[label]], device=device)
                    pred = self._model(x)
                    loss = self._loss_fn(pred, y)
                    loss.backward()
                    self._optim.step()
                    self._optim.zero_grad()
                    self.metrics["last_loss"] = float(loss.item())

            batch_count += 1
            if batch_count >= batch_size and tokens_batch:
                self.training_db.update(tokens_batch)
                for band, total in graph_batch.items():
                    count = band_counts.get(band, 1)
                    weight = total / count
                    for _ in range(count):
                        bp_update({band: weight}, [], self.weights_store)
                tokens_batch = []
                graph_batch = {}
                band_counts = {}
                batch_count = 0

        if tokens_batch:
            self.training_db.update(tokens_batch)
            for band, total in graph_batch.items():
                count = band_counts.get(band, 1)
                weight = total / count
                for _ in range(count):
                    bp_update({band: weight}, [], self.weights_store)

    # ------------------------------------------------------------------
    # Checkpoint helpers
    # ------------------------------------------------------------------
    def save_checkpoint(self, path: str | Path) -> None:
        """Persist training database, prototypes, weights and metrics."""

        path = Path(path)
        path.mkdir(parents=True, exist_ok=True)
        self.training_db.save(path / "training_db.json")
        with open(path / "prototypes.json", "w", encoding="utf-8") as fh:
            json.dump(self.resonator.prototypes, fh)
        with open(path / "weights.json", "w", encoding="utf-8") as fh:
            json.dump(self.weights_store, fh)
        with open(path / "metrics.json", "w", encoding="utf-8") as fh:
            json.dump(self.metrics, fh)
        if hasattr(self, "_model"):
            torch = self.resonator._torch
            if torch is None:
                import torch as _torch

                torch = _torch
            torch.save(self._model.state_dict(), path / "model.pt")

    def load_checkpoint(self, path: str | Path) -> None:
        """Restore training state from ``path``."""

        path = Path(path)
        self.training_db.load(path / "training_db.json")
        with open(path / "prototypes.json", "r", encoding="utf-8") as fh:
            data = json.load(fh)
        if (
            self.resonator.use_gpu
            and self.resonator.backend == "torch"
            and self.resonator._torch is not None
        ):
            torch = self.resonator._torch
            self.resonator.prototypes = {
                int(k): torch.tensor(v, device=self.resonator.device)
                for k, v in data.items()
            }
        elif (
            self.resonator.use_gpu
            and self.resonator.backend == "cupy"
            and self.resonator._cupy is not None
        ):
            cp = self.resonator._cupy
            self.resonator.prototypes = {int(k): cp.array(v) for k, v in data.items()}
        else:
            self.resonator.prototypes = {int(k): v for k, v in data.items()}

        with open(path / "weights.json", "r", encoding="utf-8") as fh:
            data_w = json.load(fh)
        self.weights_store = {int(k): v for k, v in data_w.items()}
        with open(path / "metrics.json", "r", encoding="utf-8") as fh:
            self.metrics = json.load(fh)

        model_file = path / "model.pt"
        if model_file.exists():
            torch = self.resonator._torch
            if torch is None:
                import torch as _torch

                torch = _torch
            if not hasattr(self, "_model"):
                device = (
                    self.resonator.device
                    if getattr(self.resonator, "device", None)
                    else "cuda" if torch.cuda.is_available() else "cpu"
                )
                self._model = torch.nn.Linear(1, 1).to(device)
                self._optim = torch.optim.SGD(self._model.parameters(), lr=0.01)
                self._loss_fn = torch.nn.MSELoss()
            self._model.load_state_dict(
                torch.load(model_file, map_location=self.resonator.device)
            )

    def save(self, db_path: str | Path, proto_path: str | Path) -> None:
        """Persist training database and resonator prototypes."""

        self.training_db.save(db_path)
        with open(proto_path, "w", encoding="utf-8") as fh:
            json.dump(self.resonator.prototypes, fh)

    def load(self, db_path: str | Path, proto_path: str | Path) -> None:
        """Restore training database and resonator prototypes from disk."""

        self.training_db.load(db_path)
        with open(proto_path, "r", encoding="utf-8") as fh:
            data = json.load(fh)
        if (
            self.resonator.use_gpu
            and self.resonator.backend == "torch"
            and self.resonator._torch is not None
        ):
            torch = self.resonator._torch
            self.resonator.prototypes = {
                int(k): torch.tensor(v, device=self.resonator.device)
                for k, v in data.items()
            }
        elif (
            self.resonator.use_gpu
            and self.resonator.backend == "cupy"
            and self.resonator._cupy is not None
        ):
            cp = self.resonator._cupy
            self.resonator.prototypes = {int(k): cp.array(v) for k, v in data.items()}
        else:
            self.resonator.prototypes = {int(k): v for k, v in data.items()}
