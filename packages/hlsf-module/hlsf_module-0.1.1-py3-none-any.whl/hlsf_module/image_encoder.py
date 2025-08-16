from __future__ import annotations

"""Image encoder producing :class:`~symbols.schema.SymbolToken` sequences."""

from pathlib import Path
from typing import List, Tuple
import math

from PIL import Image

from .fft_tokenizer import _nd_dft
from .symbols.schema import SymbolToken
from .symbols.vocab import Vocab
from .modal_stream import ModalStream


class ImageEncoder:
    """Encode images into ``SymbolToken`` sequences via 2-D FFT.

    ``mode`` selects how input images are interpreted:

    ``"L"``
        Standard grayscale processing (default).
    ``"RGB"``
        Process three colour channels independently and emit the channel index
        in each token's ``feat``.
    ``"3D"``
        Volumetric mode where the provided image contains multiple slices. Each
        slice is processed independently and the slice index is emitted in the
        resulting ``SymbolToken`` objects.
    """

    def __init__(
        self,
        frame: Tuple[int, int] | None = None,
        hop: Tuple[int, int] | None = None,
        vocab: Vocab | None = None,
        vocab_path: str | None = None,
        mode: str = "L",
    ) -> None:
        if vocab_path:
            vc = (
                Vocab.load(vocab_path)
                if Path(vocab_path).exists()
                else (vocab or Vocab())
            )
        else:
            vc = vocab or Vocab()
        self.vocab = vc
        self._vocab_path = vocab_path
        self.frame = frame
        self.hop = hop
        self.mode = mode.upper()

    # ------------------------------------------------------------------
    def _to_array(self, img: Image.Image) -> List:
        """Return ``img`` as a list of floats.

        Depending on ``self.mode`` this may yield a 2-D array (grayscale) or a
        3-D array with the leading dimension representing colour channels or
        volumetric slices.
        """
        mode = self.mode
        if mode == "RGB":
            img = img.convert("RGB")
            w, h = img.size
            chans = img.split()
            arrays: List[List[List[float]]] = []
            for ch in chans:
                data = list(ch.getdata())
                arrays.append([data[i * w : (i + 1) * w] for i in range(h)])
            return arrays
        if mode == "3D":
            frames: List[Image.Image] = []
            if getattr(img, "n_frames", 1) > 1:
                for i in range(img.n_frames):
                    img.seek(i)
                    frames.append(img.convert("L"))
            else:
                frames.append(img.convert("L"))
            arrays_3d: List[List[List[float]]] = []
            for frame in frames:
                w, h = frame.size
                data = list(frame.getdata())
                arrays_3d.append([data[i * w : (i + 1) * w] for i in range(h)])
            return arrays_3d
        # default grayscale
        img = img.convert("L")
        w, h = img.size
        data = list(img.getdata())
        return [data[i * w : (i + 1) * w] for i in range(h)]

    # ------------------------------------------------------------------
    def step(self, path: str | Image.Image) -> List[SymbolToken]:
        """Tokenise the image at ``path`` and return ``SymbolToken`` objects."""
        if isinstance(path, Image.Image):
            img = path
        else:
            img = Image.open(path)
        array = self._to_array(img)
        slices = array if self.mode in {"RGB", "3D"} else [array]

        h, w = len(slices[0]), len(slices[0][0])
        frame_shape = self.frame or (h, w)
        hop = self.hop or frame_shape
        streams = [ModalStream.from_array(s, shape=frame_shape, hop=hop) for s in slices]
        tokens: List[SymbolToken] = []
        t_idx = 0
        while True:
            frames = [s.read() for s in streams]
            if all(f is None for f in frames):
                break
            for c_idx, frame in enumerate(frames):
                if frame is None:
                    continue
                spec = _nd_dft(frame, frame_shape)
                for (fy, fx), val in spec.items():
                    idx = fy * frame_shape[1] + fx
                    tok_id = self.vocab.id("image", idx)
                    mag = abs(val)
                    phase = math.atan2(val.imag, val.real)
                    tokens.append(
                        SymbolToken(
                            t=t_idx,
                            id=tok_id,
                            mod="image",
                            feat={
                                "mag": mag,
                                "phase": phase,
                                "y": fy,
                                "x": fx,
                                "c": c_idx,
                            },
                            w=int(mag),
                        )
                    )
            t_idx += 1
        if self._vocab_path:
            self.vocab.save(self._vocab_path)
        return tokens
