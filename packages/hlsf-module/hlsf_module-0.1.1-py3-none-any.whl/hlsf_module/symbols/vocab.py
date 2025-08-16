from __future__ import annotations

"""Deterministic vocabulary for symbol IDs across modalities.

The vocabulary assigns unique integer identifiers for ``(modality, code)``
pairs.  It now supports text, audio and image modalities by default, allowing
callers to mix token streams without risking ID collisions.
"""

import json
from pathlib import Path
from typing import Dict, Tuple


class Vocab:
    def __init__(self) -> None:
        self._forward: Dict[Tuple[str, int], int] = {}
        self._reverse: Dict[int, Tuple[str, int]] = {}
        self._next_id: int = 0

    def id(self, mod: str, code: int) -> int:
        key = (mod, code)
        if key not in self._forward:
            self._forward[key] = self._next_id
            self._reverse[self._next_id] = key
            self._next_id += 1
        return self._forward[key]

    def decode(self, idx: int) -> Tuple[str, int]:
        return self._reverse[idx]

    def __len__(self) -> int:  # pragma: no cover - trivial
        return self._next_id

    def save(self, path: str | Path) -> None:
        """Serialise the vocabulary to ``path``.

        The mapping from token information to integer ids is stored so that
        subsequent runs can reproduce identical ids.  The file format is a
        simple JSON object mapping id strings to ``[mod, code]`` pairs.
        """

        data = {str(idx): [mod, code] for idx, (mod, code) in self._reverse.items()}
        with Path(path).open("w", encoding="utf-8") as fh:
            json.dump(data, fh)

    @classmethod
    def load(cls, path: str | Path) -> "Vocab":
        """Load a vocabulary previously produced by :meth:`save`."""

        with Path(path).open("r", encoding="utf-8") as fh:
            raw: Dict[str, Tuple[str, int]] = json.load(fh)
        vocab = cls()
        for idx_str, (mod, code) in raw.items():
            idx = int(idx_str)
            code = int(code)
            vocab._forward[(mod, code)] = idx
            vocab._reverse[idx] = (mod, code)
            if idx >= vocab._next_id:
                vocab._next_id = idx + 1
        return vocab
