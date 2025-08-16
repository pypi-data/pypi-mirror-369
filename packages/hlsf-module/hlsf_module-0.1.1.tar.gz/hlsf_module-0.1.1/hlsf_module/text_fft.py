from __future__ import annotations

"""Text-driven FFT pipeline utilities."""

from pathlib import Path

from typing import Any, Dict, Iterable, List, Sequence, Tuple
import asyncio
import json


from .fft_tokenizer import FFTTokenizer
from .multimodal_out import resynth_bands
from .geometry import rotate_state
from .signal_io import SignalStream
from .symbols.schema import SymbolToken
from .symbols.vocab import Vocab
from .text_encoder import TextEncoder
from .tensor_mapper import TensorMapper, HLSFState, MAPPING_STRATEGIES
from . import pruning
from .adjacency_expander import expand as expand_neighbors
from .llm_client import LLMClient
from .llm_weights import TrainingDB
from .rh_utils import powerlaw_bands, prime_frequencies

# Runtime helpers for optional RH mode features
rh_mode = False
prime_freqs: List[float] = []
primes: List[int] = []

class TextFFTPipeline:
    """Simple wrapper collecting token history for testing."""

    def __init__(self, vocab_path: str | None = None, *, rh_mode: bool = False) -> None:
        self.vocab_path = vocab_path
        self.rh_mode = rh_mode
        self.token_history: list = []

    def run(self, text: str, **kwargs):
        tokens, adj, graph, state = text_fft_pipeline(
            text, vocab_path=self.vocab_path, **kwargs
        )
        self.token_history.append({"name": "tokens", "tokens": tokens})
        self.token_history.append({"name": "adjacency", "adj": adj})
        self.token_history.append({"name": "state", "state": state})
        return tokens, adj, graph, state


def tokenize_text_fft(
    text: str,
    sr: int = 48000,
    frame: int = 2048,
    hop: int = 512,
    n_bands: int = 8,
    vocab_path: str | None = None,
    edges: Sequence[float] | None = None,
) -> List[SymbolToken]:
    """Tokenise ``text`` and return FFT-based :class:`SymbolToken` objects."""
    base_tokens = TextEncoder(vocab_path=vocab_path).step(text)
    if edges is not None:
        n_bands = len(edges) - 1
    mags = [0.0] * n_bands
    for tok in base_tokens:
        band = tok.id % n_bands
        mags[band] += 1.0
    audio = resynth_bands(mags, 0.1, sr)
    stream, frames = SignalStream.from_array(audio, sr=sr, frame=frame, hop=hop)
    tokenizer = FFTTokenizer(sr=sr, n_fft=frame, hop=hop, n_bands=n_bands, edges=edges)
    if vocab_path:
        vocab = Vocab.load(vocab_path) if Path(vocab_path).exists() else Vocab()
    else:
        vocab = Vocab()
    fft_tokens: List[SymbolToken] = []
    for frame_arr in iter(stream.read, None):
        for t in tokenizer.step(frame_arr):
            tok_id = vocab.id("fft", t.band)
            feat = {"mag": t.mag, "dphi": t.dphi, "band": t.band}
            if rh_mode and prime_freqs and t.centroid is not None:
                idx = min(
                    range(len(prime_freqs)),
                    key=lambda i: abs(prime_freqs[i] - t.centroid),
                )
                feat["prime_channel"] = primes[idx]
            if t.peak_mag is not None:
                feat["peak_mag"] = t.peak_mag
            if t.centroid is not None:
                feat["centroid"] = t.centroid
            if t.bandwidth is not None:
                feat["bandwidth"] = t.bandwidth
            if t.coherence is not None:
                feat["coherence"] = t.coherence
            if t.bands is not None:
                feat["bands"] = list(t.bands)
            feat.update(tokenizer.extra_features(t))
            if t.mods:
                feat.update(t.mods)

            fft_tokens.append(
                SymbolToken(t=t.t_idx, id=tok_id, mod="fft", feat=feat, w=int(t.mag))
            )
    if vocab_path:
        vocab.save(vocab_path)
    return fft_tokens


async def expand_adjacency(
    tokens: Iterable[SymbolToken],
    adjacency_percentile: float = 0.5,
    llm: LLMClient | None = None,
    *,
    training_db: TrainingDB | None = None,
    update_db: bool = False,
    max_concurrency: int | None = None,
    neighbor_count: int | None = None,
    banned_words: Sequence[str] | None = None,
) -> Dict[int, List[int]]:
    """Expand high-magnitude ``tokens`` using :mod:`adjacency_expander`.

    Parameters
    ----------
    tokens:
        Candidate tokens to expand.
    q:
        Percentile threshold selecting tokens by magnitude.
    llm:
        Client used to fetch semantic neighbours.
    training_db, update_db:
        Passed through to :func:`adjacency_expander.expand`.
    max_concurrency:
        Optional limit for concurrently in-flight neighbour requests.
    neighbor_count:
        Optional override for the number of neighbours requested from the LLM.
    banned_words:
        Words to exclude from adjacency expansion.  Defaults to
        ``ADJ_BANNED_WORDS`` environment variable when not provided.
    """

    tokens = list(tokens)
    mags = [t.feat.get("mag", 0.0) for t in tokens]
    if not mags:
        return {}
    mags_sorted = sorted(mags)
    idx = int(len(mags_sorted) * adjacency_percentile)
    idx = min(max(idx, 0), len(mags_sorted) - 1)
    threshold = mags_sorted[idx]

    targets = [t for t in tokens if t.feat.get("mag", 0.0) >= threshold]
    if not targets:
        return {}

    if llm is None:
        return {t.id: [] for t in targets}

    sem = asyncio.Semaphore(max_concurrency) if max_concurrency else None

    async def _run(tok: SymbolToken) -> Tuple[int, List[int]]:
        if sem is None:
            neighbors_json = await expand_neighbors(
                tok,
                llm,
                training_db=training_db,
                update=update_db,
                neighbor_count=neighbor_count,
                banned_words=banned_words,
            )
        else:
            async with sem:
                neighbors_json = await expand_neighbors(
                    tok,
                    llm,
                    training_db=training_db,
                    update=update_db,
                    neighbor_count=neighbor_count,
                    banned_words=banned_words,
                )
        return tok.id, [json.loads(s)["id"] for s in neighbors_json]

    results = await asyncio.gather(*(_run(t) for t in targets))
    return {tid: ids for tid, ids in results}



def expand_adjacency_sync(
    tokens: Iterable[SymbolToken],
    q: float = 0.5,
    llm: LLMClient | None = None,
    *,
    training_db: TrainingDB | None = None,
    update_db: bool = False,
    max_concurrency: int | None = None,
    neighbor_count: int | None = None,
    banned_words: Sequence[str] | None = None,
    loop: asyncio.AbstractEventLoop | None = None,
) -> Dict[int, List[int]] | asyncio.Task[Dict[int, List[int]]]:
    """Synchronous helper for :func:`expand_adjacency`.

    When no event loop is running the coroutine is executed via
    :func:`asyncio.run`.  If a loop is already running the coroutine is
    scheduled on it and the created task returned.
    """

    try:
        running_loop = loop or asyncio.get_running_loop()
    except RuntimeError:
        return asyncio.run(
            expand_adjacency(
                tokens,
                adjacency_percentile=q,
                llm=llm,
                training_db=training_db,
                update_db=update_db,
                max_concurrency=max_concurrency,
                neighbor_count=neighbor_count,
                banned_words=banned_words,
            )
        )
    else:
        return running_loop.create_task(
            expand_adjacency(
                tokens,
                adjacency_percentile=q,
                llm=llm,
                training_db=training_db,
                update_db=update_db,
                max_concurrency=max_concurrency,
                neighbor_count=neighbor_count,
                banned_words=banned_words,
            )
        )


def _apply_rh_gate(
    tokens: List[SymbolToken], strategy: str | None
) -> List[SymbolToken]:
    """Filter ``tokens`` using a registered gater strategy."""
    if not strategy:
        return tokens
    try:
        from . import plugins

        gater_cls = plugins.get_gater(strategy)
        gater = gater_cls()
    except Exception:
        return tokens

    gated: List[SymbolToken] = []
    for t in tokens:
        try:
            keep = gater.decide(t)
        except Exception:
            keep = True
        if keep:
            gated.append(t)
    return gated

def prune_tokens(
    tokens: Iterable[SymbolToken],
    threshold: float = 1e-3,
    mapping_strategy: str | None = None,
) -> Tuple[List[int], TensorMapper]:
    """Prune weak bands from ``tokens`` and return removed ids and mapper."""
    from . import plugins

    mapper_callable = None
    if mapping_strategy:
        try:
            mapper_cls = plugins.get_mapper(mapping_strategy)
            mapper_callable = mapper_cls().map
        except Exception:
            mapper_callable = mapping_strategy
    mapper = TensorMapper(mapper=mapper_callable)
    mapper.update(tokens)
    pruned = pruning.apply(mapper.graph, threshold)
    return pruned, mapper


class TextFFTPipeline:
    """Convenience wrapper bundling the text→FFT→HLSF pipeline.

    The class records intermediate snapshots in ``token_history`` for
    inspection and testing.
    """

    def __init__(self, vocab_path: str | None = None, *, rh_mode: bool = False) -> None:
        self.vocab_path = vocab_path
        self.rh_mode = rh_mode
        self.token_history: List[Dict[str, object]] = []

    def run(
        self,
        text: str,
        *,
        prune_threshold: float = 1e-3,
        adjacency_percentile: float = 0.5,
    ) -> Tuple[List[SymbolToken], Dict[int, List[int]], Dict[int, Dict[str, float]], HLSFState]:
        tokens = tokenize_text_fft(text, vocab_path=self.vocab_path, rh_mode=self.rh_mode)
        self.token_history.append({"name": "raw", "tokens": tokens})
        adj = expand_adjacency_sync(tokens, q=adjacency_percentile)
        self.token_history.append({"name": "adjacency", "adj": adj})
        pruned, mapper = prune_tokens(tokens, threshold=prune_threshold)
        self.token_history.append({"name": "pruned", "pruned": pruned})
        state = mapper.to_hlsf()
        self.token_history.append({"name": "final", "state": state})
        return tokens, adj, mapper.graph, state


async def text_fft_pipeline(

    text: str,
    llm: LLMClient | None = None,
    prune_threshold: float = 1e-3,
    adjacency_percentile: float = 0.5,
    vocab_path: str | None = None,
    collapse: bool = False,
    angle_deg: float = 45.0,
    training_db: TrainingDB | None = None,
    update_db: bool = False,
    *,
    rh_mode: bool = False,
    rh_config: Dict[str, Any] | None = None,
    gate_strategy: str | None = None,
    mapping_strategy: str | None = None,
) -> Tuple[
    List[SymbolToken],
    Dict[int, List[int]],
    Dict[int, Dict[str, float]],
    HLSFState,
]:
    """Run the full text→FFT→HLSF pipeline."""
    edges = None
    if rh_mode and rh_config:
        edges = rh_config.get("edges")
    tokens = tokenize_text_fft(text, vocab_path=vocab_path, edges=edges)
    if rh_mode:
        for t in tokens:
            t.feat["rh"] = True
        tokens = _apply_rh_gate(tokens, gate_strategy)
        k_value = sum(t.w if t.w else float(t.feat.get("mag", 0.0)) for t in tokens)
    else:
        k_value = None
    adj = await expand_adjacency(
        tokens,
        adjacency_percentile=adjacency_percentile,
        llm=llm,
        training_db=training_db,
        update_db=update_db,
    )
    pruned, mapper = prune_tokens(
        tokens, threshold=prune_threshold, mapping_strategy=mapping_strategy
    )
    state = mapper.to_hlsf()
    if collapse:
        state = rotate_state(state, angle_deg)
    state.metrics = {"token_count": len(tokens), "pruned": len(pruned)}
    if k_value is not None:
        state.metrics["K"] = k_value
    state.resonance_metrics = {
        "symbolic_resonance": mapper.symbolic_resonance_index()
    }
    return tokens, adj, mapper.graph, state


class TextFFTPipeline:
    """Convenience wrapper bundling the text→FFT→HLSF pipeline.

    The class records intermediate snapshots in ``token_history`` for
    inspection and testing.
    """

    def __init__(
        self,
        *,
        vocab_path: str | None = None,
        prune_threshold: float = 1e-3,
        adjacency_percentile: float = 0.5,
        llm: LLMClient | None = None,
        collapse: bool = False,
        angle_deg: float = 45.0,
        training_db: TrainingDB | None = None,
        update_db: bool = False,
    ) -> None:
        self.vocab_path = vocab_path
        self.prune_threshold = prune_threshold
        self.adjacency_percentile = adjacency_percentile
        self.llm = llm
        self.collapse = collapse
        self.angle_deg = angle_deg
        self.training_db = training_db
        self.update_db = update_db
        self.token_history: List[Dict[str, object]] = []

    def run(self, text: str):
        tokens = tokenize_text_fft(
            text,
            vocab_path=self.kwargs.get("vocab_path"),
            rh_mode=self.kwargs.get("rh_mode", False),
        )
        self.token_history.append({"name": "raw", "tokens": list(tokens)})
        adj = expand_adjacency_sync(
            tokens,
            adjacency_percentile=self.adjacency_percentile,
            llm=self.llm,
            training_db=self.training_db,
            update_db=self.update_db,
        )
        self.token_history.append({"name": "adjacency", "adj": adj})
        pruned, mapper = prune_tokens(
            tokens, threshold=self.kwargs.get("prune_threshold", 1e-3)
        )
        self.token_history.append({"name": "pruned", "pruned": pruned})
        state = mapper.to_hlsf()
        if self.collapse:
            state = rotate_state(state, self.angle_deg)
        state.metrics = {"token_count": len(tokens), "pruned": len(pruned)}
        state.resonance_metrics = {
            "symbolic_resonance": mapper.symbolic_resonance_index()
        }
        self.token_history.append({"name": "state", "state": state})
        return tokens, adj, mapper.graph, state


def run_audio_pipeline(
    path: str | None = None,
    *,
    duration: float = 1.0,
    sr: int = 48000,
    frame: int = 2048,
    hop: int = 512,
    pre_emphasis: float = 0.0,
    norm_mode: str = "peak",
    window: str = "hann",
    n_fft: int | None = None,
    banding: str = "log",
    pre_mode: str = "first_order",
    edges: Sequence[float] | None = None,
    collapse: bool = False,
    angle_deg: float = 45.0,
    rh_mode: bool = False,
    rh_config: Dict[str, Any] | None = None,
    gate_strategy: str | None = None,
    mapping_strategy: str | None = None,
) -> Tuple[List[SymbolToken], Dict[int, List[int]], HLSFState]:
    """Tokenise audio from ``path`` or the microphone and map to ``HLSFState``.

    Parameters mirror :func:`~hlsf_module.signal_io.SignalStream.from_microphone`.
    When ``path`` is ``None`` the default microphone is used for ``duration``
    seconds.  If a path is supplied the file is interpreted as a mono WAV file.
    The function returns the list of produced :class:`~symbols.schema.SymbolToken`
    objects, an adjacency mapping (currently empty) and the resulting
    :class:`~tensor_mapper.HLSFState` instance.
    """

    if n_fft is None:
        n_fft = frame

    if path is not None:
        try:  # pragma: no cover - file I/O
            import wave, struct

            with wave.open(path, "rb") as wf:
                if wf.getnchannels() != 1:
                    raise ValueError("only mono WAV files supported")
                sr = wf.getframerate()
                frames = wf.readframes(wf.getnframes())
                fmt = (
                    "<" + {1: "b", 2: "h", 4: "i"}[wf.getsampwidth()] * wf.getnframes()
                )
                data = [
                    x / float(2 ** (8 * wf.getsampwidth() - 1))
                    for x in struct.unpack(fmt, frames)
                ]
        except Exception as exc:  # pragma: no cover - best effort
            raise RuntimeError(f"unable to read audio file: {path}") from exc
        stream, _ = SignalStream.from_array(
            data,
            sr=sr,
            frame=frame,
            hop=hop,
            pre_emphasis=pre_emphasis,
            pre_mode=pre_mode,
            norm_mode=norm_mode,
            window=window,
        )
    else:
        stream = SignalStream.from_microphone(
            duration,
            sr=sr,
            frame=frame,
            hop=hop,
            pre_emphasis=pre_emphasis,
            pre_mode=pre_mode,
            norm_mode=norm_mode,
            window=window,
        )

    if rh_mode and rh_config and rh_config.get("edges") is not None:
        edges = rh_config.get("edges")
    tokenizer = FFTTokenizer(sr=sr, n_fft=n_fft, hop=hop, banding=banding, edges=edges)
    from . import plugins

    mapper_obj = None
    if mapping_strategy:
        try:
            mapper_cls = plugins.get_mapper(mapping_strategy)
            mapper_obj = mapper_cls()
        except Exception:
            mapper_obj = None
    mapper = TensorMapper(mapper=mapper_obj.map if mapper_obj else None)
    tokens: List[SymbolToken] = []
    while True:
        frame_arr = stream.read()
        if frame_arr is None:
            break
        for t in tokenizer.step(frame_arr):
            feat = {"mag": t.mag, "dphi": t.dphi, "band": t.band}
            if t.peak_mag is not None:
                feat["peak_mag"] = t.peak_mag
            if t.centroid is not None:
                feat["centroid"] = t.centroid
            if t.bandwidth is not None:
                feat["bandwidth"] = t.bandwidth
            if t.coherence is not None:
                feat["coherence"] = t.coherence
            if t.bands is not None:
                feat["bands"] = list(t.bands)
            if t.mods:
                feat.update(t.mods)
            tokens.append(
                SymbolToken(t=t.t_idx, id=t.band, mod="audio", feat=feat, w=int(t.mag))
            )

    if rh_mode:
        for t in tokens:
            t.feat["rh"] = True
        tokens = _apply_rh_gate(tokens, gate_strategy)
        k_value = sum(t.w if t.w else float(t.feat.get("mag", 0.0)) for t in tokens)
    else:
        k_value = None

    mapper.update(tokens)
    state = mapper.to_hlsf()
    if collapse:
        state = rotate_state(state, angle_deg)
    adj: Dict[int, List[int]] = {}
    if k_value is not None:
        state.metrics = getattr(state, "metrics", {})
        state.metrics["K"] = k_value
    return tokens, adj, state

class TextFFTPipeline:
    """Convenience wrapper recording token processing history."""

    def __init__(self) -> None:
        self.token_history: List[Dict[str, object]] = []

    def run(
        self, text: str
    ) -> Tuple[
        List[SymbolToken], Dict[int, List[int]], Dict[int, Dict[str, float]], HLSFState
    ]:
        tokens = tokenize_text_fft(text)
        self.token_history.append({"name": "raw", "tokens": tokens})
        adj = expand_adjacency_sync(tokens)
        self.token_history.append({"name": "adj", "adj": adj})
        pruned, mapper = prune_tokens(tokens)
        self.token_history.append({"name": "pruned", "removed": pruned})
        state = mapper.to_hlsf()
        self.token_history.append({"name": "state", "state": state})
        return tokens, adj, mapper.graph, state
