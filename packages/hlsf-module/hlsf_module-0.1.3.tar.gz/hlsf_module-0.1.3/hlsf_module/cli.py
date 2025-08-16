"""Command-line interface wiring geometry and visualization."""

from __future__ import annotations

import argparse
import os
import json
import textwrap
from dataclasses import dataclass, field
from typing import Any, Sequence

from .geometry import HLSFGenerator
from .symbols.vocab import Vocab
from . import plugins as _plugins  # load plugin entry points
from . import gating_strategies


def _load_config(path: str) -> dict:
    """Load configuration data from JSON or YAML file."""

    with open(path, "r", encoding="utf-8") as fh:
        if path.endswith((".yml", ".yaml")):
            try:
                import yaml  # type: ignore
            except Exception as exc:  # pragma: no cover - optional dependency
                raise RuntimeError("PyYAML is required for YAML configuration files") from exc
            return yaml.safe_load(fh) or {}
        return json.load(fh)


@dataclass
class ModelState:
    """Minimal container for FFT pipeline state."""

    token_graph: dict = field(default_factory=dict)
    weights: dict = field(default_factory=dict)
    motifs: list = field(default_factory=list)
    gate_state: bool = False
    recursion_metrics: list = field(default_factory=list)


def parse_args(argv: Any | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser()

    # Plugin management -----------------------------------------------------
    sub = parser.add_subparsers(dest="command")
    plugins_parser = sub.add_parser("plugins", help="plugin utilities")
    plugins_sub = plugins_parser.add_subparsers(dest="plugins_command")
    plugins_sub.required = True  # type: ignore[attr-defined]
    plugins_sub.add_parser("list", help="list available plugins")
    parser.add_argument(
        "--enable-fft",
        action="store_true",
        help="run experimental FFT pipeline (GPU backends supported)",
    )
    parser.add_argument(
        "--live",
        action="store_true",
        help="enable live visualisation of resonance and geometry (use --web for browser viewer)",
    )
    parser.add_argument("--web", action="store_true", help="launch web viewer for geometry inspection")
    parser.add_argument("--use-gpu", action="store_true", help="enable GPU backend when available")
    parser.add_argument("--device", type=str, help="GPU device identifier, e.g. 'cuda:0'")
    parser.add_argument(
        "--rh-mode",
        action="store_true",
        help="enable RH gating/mapping plugins",
    )
    parser.add_argument("--mic", type=float, help="record N seconds from microphone")
    parser.add_argument(
        "--text",
        type=str,
        help="process text input instead of audio; additional modalities can be loaded via plugins",
    )
    parser.add_argument("--vocab", type=str, help="path to vocabulary for text/plugins")
    parser.add_argument("--export-vocab", type=str, help="export current vocabulary to path")
    parser.add_argument("--import-vocab", type=str, help="import vocabulary from path")
    parser.add_argument(
        "--weights-db",
        type=str,
        default=os.getenv("HLSF_WEIGHTS_DB"),
        help="path to persistent TrainingDB weight database",
    )
    parser.add_argument(
        "--text-fft",
        type=str,
        help="run multi-stage text→FFT pipeline on input string",
    )
    parser.add_argument(
        "--train",
        type=str,
        help="path to a mixed-modality dataset for training",
    )
    parser.add_argument(
        "--prototypes",
        type=str,
        help="where to persist SymbolResonator prototypes",
    )
    parser.add_argument(
        "--collapse-geom",
        action="store_true",
        help="rotate geometry and merge overlapping triangles",
    )
    parser.add_argument(
        "--adj-neighbors",
        type=int,
        default=int(os.getenv("ADJ_NEIGHBOR_COUNT", "2")),
        help="number of adjacency neighbours to request",
    )
    parser.add_argument(
        "--adj-model",
        type=str,
        default=os.getenv("ADJ_MODEL", "gpt-3.5-turbo"),
        help="LLM model for adjacency expansion",
    )
    parser.add_argument(
        "--llm-provider",
        type=str,
        default=os.getenv("LLM_PROVIDER", "openai"),
        help="LLM provider for adjacency expansion",
    )
    parser.add_argument(
        "--llm-embedding",
        type=str,
        help="path to embeddings for 'embedding' LLM provider",
    )
    parser.add_argument(
        "--queue-size",
        type=int,
        default=int(os.getenv("STREAM_QUEUE_SIZE", "4")),
        help="max items per streaming pipeline queue",
    )
    parser.add_argument(
        "--save-state",
        type=str,
        help="write final HLSFState to this path",
    )
    parser.add_argument(
        "--load-state",
        type=str,
        help="load HLSFState from this path for visualisation",
    )

    # Pre-processing and normalisation options
    pre = parser.add_argument_group("preprocessing")
    pre.add_argument(
        "--norm-mode",
        choices=["peak", "rms", "none"],
        default=os.getenv("HLSF_NORM_MODE", "peak"),
        help="normalisation mode",
    )
    pre.add_argument(
        "--preemphasis",
        type=float,
        default=float(os.getenv("HLSF_PRE_EMPHASIS", "0.97")),
        help="pre-emphasis alpha",
    )

    pre.add_argument(
        "--pre-mode",
        choices=["first_order", "pre_emphasis", "dc_block"],
        default=os.getenv("HLSF_PRE_MODE", "first_order"),
        help="pre-emphasis filter mode",
    )
    pre.add_argument(

        "--window",
        choices=["hann", "hamming", "blackman", "rect"],
        default=os.getenv("HLSF_WINDOW", "hann"),
        help="analysis window type",
    )

    # FFT configuration
    fft = parser.add_argument_group("FFT")
    fft.add_argument(
        "--fft-size",
        type=int,
        default=int(os.getenv("HLSF_FFT_SIZE", "2048")),
        help="FFT size (power of two)",
    )

    # Banding options
    band = parser.add_argument_group("banding")
    band.add_argument(
        "--banding",
        choices=["log", "linear", "mel"],
        default=os.getenv("HLSF_BANDING", "log"),
        help="banding scheme",
    )

    band.add_argument(
        "--edge-file",
        type=str,
        default=None,
        help="file containing explicit band edges",
    )

    # Resonator / gating parameters
    res = parser.add_argument_group("resonator")
    res.add_argument(

        "--res-threshold",
        type=float,
        default=float(os.getenv("HLSF_RESON_THRESHOLD", str(1 / 3.636))),
        help="resonator threshold",
    )
    res.add_argument(
        "--gate-duration",
        type=int,
        default=int(os.getenv("HLSF_GATE_DURATION", "8")),
        help="gate duration",
    )
    gate = parser.add_argument_group("gating")
    gate.add_argument(
        "--gate-margin",
        type=float,
        default=float(os.getenv("HLSF_GATE_MARGIN", "0.0")),
        help="margin added to gate threshold",
    )
    gate.add_argument(
        "--gate-detectors",
        type=int,
        default=int(os.getenv("HLSF_GATE_DETECTORS", "1")),
        help="number of parallel gate detectors",
    )
    gate.add_argument(
        "--gate-coherence",
        type=float,
        default=os.getenv("HLSF_GATE_COHERENCE"),
        help="coherence ratio required to open gate",
    )
    gate.add_argument(
        "--gate-peak",
        type=float,
        default=os.getenv("HLSF_GATE_PEAK"),
        help="peak ratio required to open gate",
    )
    gate.add_argument(
        "--gate-detector-var",
        type=float,
        default=os.getenv("HLSF_GATE_DETECTOR_VAR"),
        help="expected variance of detectors",
    )
    gate.add_argument(
        "--gate-strategy",
        "--gate-threshold-strategy",
        "--gate-strategy",
        dest="gate_threshold_strategy",
        choices=list(gating_strategies.STRATEGIES),
        default=os.getenv("HLSF_GATE_THRESHOLD_STRATEGY"),
        help="strategy for dynamic thresholds",
    )
    gate.add_argument(
        "--gate-percentile",
        type=float,
        default=float(os.getenv("HLSF_GATE_PERCENTILE", "50.0")),
        help="percentile for percentile strategy",
    )
    gate.add_argument(
        "--gate-var-factor",
        type=float,
        default=float(os.getenv("HLSF_GATE_VAR_FACTOR", "1.0")),
        help="variance scaling factor",
    )
    gate.add_argument(
        "--gate-ema-alpha",
        type=float,
        default=float(os.getenv("HLSF_GATE_EMA_ALPHA", "0.5")),
        help="smoothing factor for EMA strategy",
    )
    gate.add_argument(
        "--gate-cross-weight",
        type=float,
        default=float(os.getenv("HLSF_GATE_CROSS_WEIGHT", "0.5")),
        help="weight for cross-modal scores",
    )
    rec = parser.add_argument_group("recursion")
    rec.add_argument(
        "--gain-metric",
        choices=["first", "mean", "median"],
        default=os.getenv("HLSF_GAIN_METRIC", "first"),
        help="statistic used to evaluate window gain",
    )
    args = parser.parse_args(argv)
    # Propagate adjacency parameters to environment for library defaults
    os.environ["ADJ_NEIGHBOR_COUNT"] = str(args.adj_neighbors)
    os.environ["ADJ_MODEL"] = args.adj_model
    os.environ["LLM_PROVIDER"] = args.llm_provider
    if getattr(args, "llm_embedding", None):
        os.environ["LLM_EMBEDDINGS"] = args.llm_embedding

    if getattr(args, "edge_file", None):
        try:
            _validate_args(args)
        except ValueError as exc:
            run.error(str(exc))
    return args


def export_vocab(path: str, vocab: Vocab | None = None) -> None:
    """Export ``vocab`` to ``path``.  If ``vocab`` is ``None`` an empty vocabulary is written."""

    (vocab or Vocab()).save(path)


def import_vocab(path: str) -> Vocab:
    """Load vocabulary from ``path`` and return it."""

    return Vocab.load(path)


def _validate_args(args: argparse.Namespace) -> None:
    if not 0.0 <= args.preemphasis < 1.0:
        raise ValueError("pre-emphasis alpha must be in [0, 1)")
    if args.fft_size <= 0 or args.fft_size & (args.fft_size - 1) != 0:
        raise ValueError("FFT size must be a power of two")
    if not 0.0 < args.res_threshold < 1.0:
        raise ValueError("resonator threshold must be between 0 and 1")
    if args.gate_duration <= 0:
        raise ValueError("gate duration must be positive")
    if args.gate_margin < 0:
        raise ValueError("gate margin must be non-negative")
    if args.gate_detectors <= 0:
        raise ValueError("gate detectors must be positive")
    if not 0.0 <= args.gate_percentile <= 100.0:
        raise ValueError("gate percentile must be in [0,100]")
    if args.gate_ema_alpha is not None and not 0.0 < args.gate_ema_alpha <= 1.0:
        raise ValueError("gate ema alpha must be in (0,1]")
    if not 0.0 <= args.cross_weight <= 1.0:
        raise ValueError("cross weight must be in [0,1]")
    if not 0.0 <= args.gate_trim_percent <= 50.0:
        raise ValueError("gate trim percent must be in [0,50]")
    if args.gate_slope_window <= 0:
        raise ValueError("gate slope window must be positive")
    if args.gate_entropy_window <= 0:
        raise ValueError("gate entropy window must be positive")
    if args.gate_slope_factor < 0:
        raise ValueError("gate slope factor must be non-negative")
    if args.gate_entropy_weight < 0:
        raise ValueError("gate entropy weight must be non-negative")


def run_text_fft(
    text: str,
    vocab_path: str | None = None,
    collapse: bool = False,
    rh_mode: bool = False,
    rh_config: dict | None = None,
    llm_provider: str | None = None,
    llm_embedding: str | None = None,
    state_path: str | None = None,
    gate_strategy: str | None = None,
    mapping_strategy: str | None = None,
) -> None:
    """Run the multi-stage text→FFT pipeline."""
    import asyncio
    from .text_fft import text_fft_pipeline
    from .llm_client import LLMClient, StubLLMClient, EmbeddingLLMClient

    llm = None
    if llm_provider:
        name = llm_provider.lower()
        if name == "stub":
            llm = LLMClient(provider=StubLLMClient(["foo", "bar"]))
        elif name == "embedding":
            if llm_embedding is None:
                raise ValueError("embedding provider requires --llm-embedding")
            llm = LLMClient(provider=EmbeddingLLMClient(llm_embedding))
        else:
            llm = LLMClient(provider_name=llm_provider)

    tokens, adj, graph, state = text_fft_pipeline(
        text,
        vocab_path=vocab_path,
        collapse=collapse,
        rh_mode=rh_mode,
        rh_config=rh_config,
        gate_strategy=gate_strategy,
        mapping_strategy=mapping_strategy,
    )
    if state_path:
        from .multimodal_out import snapshot_state

        snapshot_state(state_path, state)
    print(f"FFT tokens: {len(tokens)}")
    print(f"Expanded adjacencies: {len(adj)}")
    print(f"Triangles: {len(state.triangles)}")


def _process_tokens(
    tokens: list,
    sr: int,
    is_text: bool,
    res_threshold: float,
    gate_duration: int,
    gate_margin: float,
    gate_detectors: int,
    gate_coherence: float | None,
    gate_peak: float | None,
    gate_detector_var: float | None,
    gate_strategy: str | None,
    gate_percentile: float,
    gate_var_factor: float,
    gate_ema_alpha: float,
    gate_trim_percent: float,
    gate_slope_window: int,
    gate_slope_factor: float,
    gate_entropy_window: int,
    gate_entropy_weight: float,
    cross_weight: float,
    gate_prev_threshold: float | None = None,
    gate_k_target: float = 0.0,
    gate_weight_resonance: float = 1.0,
    gate_weight_k: float = 1.0,
    gate_weight_prime: float = 0.0,
    gate_weight_harmonic: float = 0.0,
    gate_prime_priority: bool = False,
    mapping_strategy: str | None = None,
    import_weights: str | None = None,
    export_weights: str | None = None,
    gain_metric: str = "first",
    weight_db: str | None = None,
    state_path: str | None = None,
    mapper_name: str | None = None,
) -> HLSFState:
    from .tensor_mapper import TensorMapper
    from . import (
        pruning,
        clusterer,
        weights_bp,
        recursion_ctrl,
        rotation_rules,
        agency_gates,
        multimodal_out,
    )
    from .gating_strategies import compute_K
    from .llm_weights import TrainingDB
    from .weight_cache import load_training_db, save_training_db

    if weight_db:
        db = load_training_db(weight_db)
    else:
        db = TrainingDB()
        if import_weights:
            db.load(import_weights)
    db.update(tokens)
    if weight_db:
        save_training_db(db, weight_db)
    elif export_weights:
        db.save(export_weights)

    if is_text:
        tokens = pruning.prune_text_tokens(tokens, min_weight=0.1)

    mapper = TensorMapper(use_gpu=use_gpu, device=device, mapping_strategy=mapping_strategy)
    mapper.update(tokens)
    pruned = pruning.apply(mapper.graph)
    removed = clusterer.collapse(mapper.graph)
    if all(isinstance(v, (int, float)) for v in mapper.graph.values()):
        weights_bp.update(mapper.graph, list(set(pruned) | set(removed)), {})
    ctrl = recursion_ctrl.RecursionController(
        window=gate_duration, threshold=res_threshold, gain_metric=gain_metric
    )
    total = sum(v for v in mapper.graph.values() if isinstance(v, (int, float))) or 1.0
    ctrl.update(total)

    stats = {t.feat.get("band", t.id): t.feat.get("dphi", 0.0) for t in tokens}
    angles = rotation_rules.for_motifs(stats)
    res_sustain = gate_duration
    res_detectors = gate_detectors
    gated = []
    for t in tokens:
        motif = {
            "scores": [t.feat.get("mag", 0.0), 0.0],
            "duration": res_sustain,
            "detectors": res_detectors,
            "cross_scores": t.feat.get("cross_scores", []),
        }
        K_val = compute_K(motif["scores"])
        motif["K_dev"] = abs(K_val - 0.0)
        if agency_gates.decide(
            motif,
            threshold=res_threshold,
            margin=gate_margin,
            sustain=res_sustain,
            detectors=res_detectors,
            coherence=gate_coherence,
            peak=gate_peak,
            detector_var=gate_detector_var,
            strategy=gate_strategy,
            percentile=gate_percentile,
            var_factor=gate_var_factor,
            ema_alpha=gate_ema_alpha,
            prev_threshold=gate_prev_threshold,
            cross_weight=cross_weight,
            k_target=gate_k_target,
            weights={
                "resonance": gate_weight_resonance,
                "k_dev": gate_weight_k,
                "prime": gate_weight_prime,
                "harmonic": gate_weight_harmonic,
            },
            prime_priority=gate_prime_priority,
        ):
            gated.append(t)
    if is_text:
        text_out = "".join(chr(t.feat["char"]) for t in gated if "char" in t.feat)
        audio_out = (
            multimodal_out.resynth_bands(
                [t.feat.get("mag", 1.0) for t in gated], 0.1, sr
            )
            if gated
            else []
        )
        print(f"Gated text: {text_out}")
    else:
        text_out = " ".join(str(t.feat["band"]) for t in gated)
        audio_out = (
            multimodal_out.resynth_bands(
                [t.feat.get("mag", 0.0) for t in gated], 0.5, sr
            )
            if gated
            else []
        )
        print(f"Gated bands: {text_out}")
    print(f"Generated {len(audio_out)} audio samples")
    state = mapper.to_hlsf()
    if state_path:
        from .multimodal_out import snapshot_state

        snapshot_state(state_path, state)
    print(f"Triangles: {len(state.triangles)}")
    print(f"Rotation angles: {angles}")
    if state.metrics:
        print(f"Symbolic Resonance Index: {state.metrics.get('resonance_index', 0.0)}")
    return state


def run_text_mode(
    text: str,
    sr: int = 48000,
    frame: int = 2048,
    hop: int = 512,
    res_threshold: float = 1 / 3.636,
    gate_duration: int = 8,
    gate_margin: float = 0.1,
    gate_detectors: int = 1,
    gate_coherence: float | None = None,
    gate_peak: float | None = None,
    gate_detector_var: float | None = None,
    gate_strategy: str | None = None,
    gate_percentile: float = 50.0,
    gate_var_factor: float = 1.0,
    gate_ema_alpha: float = 0.5,
    gate_trim_percent: float = 0.0,
    gate_slope_window: int = 5,
    gate_slope_factor: float = 1.0,
    gate_entropy_window: int = 5,
    gate_entropy_weight: float = 1.0,
    cross_weight: float = 0.5,
    gate_prev_threshold: float | None = None,
    gate_k_target: float = 0.0,
    gate_weight_resonance: float = 1.0,
    gate_weight_k: float = 1.0,
    gate_weight_prime: float = 0.0,
    gate_weight_harmonic: float = 0.0,
    gate_prime_priority: bool = False,
    mapping_strategy: str | None = None,
    vocab_path: str | None = None,
    import_weights: str | None = None,
    export_weights: str | None = None,
    weight_db: str | None = None,
    state_path: str | None = None,
    mapper_name: str | None = None,

) -> HLSFState:

    """Process text input through the audio pipeline."""
    from .ngram_text_encoder import tokenize_multilevel

    tokens: list = []
    levels = tokenize_multilevel(text, vocab_path=vocab_path)
    for lvl in levels:
        tokens.extend(lvl)
    gain_metric = "first"
    state = _process_tokens(
        tokens,
        sr,
        True,
        res_threshold,
        gate_duration,
        gate_margin,
        gate_detectors,
        gate_coherence,
        gate_peak,
        gate_detector_var,
        gate_strategy,
        gate_percentile,
        gate_var_factor,
        gate_ema_alpha,
        gate_trim_percent,
        gate_slope_window,
        gate_slope_factor,
        gate_entropy_window,
        gate_entropy_weight,
        cross_weight,
        gate_prev_threshold,
        gate_k_target,
        gate_weight_resonance,
        gate_weight_k,
        gate_weight_prime,
        gate_weight_harmonic,
        gate_prime_priority,
        mapping_strategy,
        import_weights,
        export_weights,
        gain_metric="first",
        weight_db=weight_db,
        state_path=state_path,
        mapper_name=mapper_name,
    )
    return state

def run_microphone_mode(
    duration: float,
    sr: int = 48000,
    frame: int = 2048,
    hop: int = 512,
    pre_emphasis: float = 0.97,
    norm_mode: str = "peak",
    window: str = "hann",
    n_fft: int = 2048,
    banding: str = "log",
    pre_mode: str = "first_order",
    edges: Sequence[float] | None = None,

    res_threshold: float = 1 / 3.636,
    gate_duration: int = 8,
    gate_margin: float = 0.1,
    gate_detectors: int = 1,
    gate_coherence: float | None = None,
    gate_peak: float | None = None,
    gate_detector_var: float | None = None,
    gate_strategy: str | None = None,
    gate_percentile: float = 50.0,
    gate_var_factor: float = 1.0,
    gate_ema_alpha: float = 0.5,
    gate_trim_percent: float = 0.0,
    gate_slope_window: int = 5,
    gate_slope_factor: float = 1.0,
    gate_entropy_window: int = 5,
    gate_entropy_weight: float = 1.0,
    cross_weight: float = 0.5,
    gate_prev_threshold: float | None = None,
    gate_k_target: float = 0.0,
    gate_weight_resonance: float = 1.0,
    gate_weight_k: float = 1.0,
    gate_weight_prime: float = 0.0,
    gate_weight_harmonic: float = 0.0,
    gate_prime_priority: bool = False,
    mapping_strategy: str | None = None,

    queue_size: int = 4,
    visualizer_cls: Any | None = None,

    *,
    use_gpu: bool = False,
    device: str | None = None,
    state_path: str | None = None,
) -> None:
    """Record audio from the microphone and process frames incrementally."""

    import asyncio
    from .signal_io import capture_microphone

    from .stream_pipeline import StreamPipeline
    from .live_visualizer import LiveVisualizer


    async def _runner() -> None:
        pipeline = StreamPipeline(
            queue_size=queue_size,
            encoder_args=dict(
                sr=sr,
                n_fft=n_fft,
                hop=hop,
                bands=8,
                banding=banding,
                edges=edges,
                use_gpu=use_gpu,
                device=device,
            ),
            gate_args=dict(
                threshold=res_threshold,
                margin=gate_margin,
                sustain=gate_duration,
                detectors=gate_detectors,
                coherence=gate_coherence,
                peak=gate_peak,
                detector_var=gate_detector_var,
                strategy=gate_strategy,
                percentile=gate_percentile,
                var_factor=gate_var_factor,
                ema_alpha=gate_ema_alpha,
                prev_threshold=gate_prev_threshold,
                cross_weight=cross_weight,
                k_target=gate_k_target,
                weights={
                    "resonance": gate_weight_resonance,
                    "k_dev": gate_weight_k,
                    "prime": gate_weight_prime,
                    "harmonic": gate_weight_harmonic,
                },
                prime_priority=gate_prime_priority,
            ),
            mapping_strategy=mapping_strategy,
            use_gpu=use_gpu,
            device=device,
        )
        await pipeline.start()
        vis_cls = visualizer_cls or LiveVisualizer
        vis = vis_cls()
        last_state: HLSFState | None = None

        async def consume() -> None:
            while True:
                item = await pipeline.result_q.get()
                if item is None:
                    break
                scores, state = item
                last_state = state
                vis.update(scores, state)
            vis.close()

        consumer = asyncio.create_task(consume())

        async for frame_arr in capture_microphone(
            duration,
            sr=sr,
            frame=frame,
            hop=hop,
            pre_emphasis=pre_emphasis,
            pre_mode=pre_mode,
            norm_mode=norm_mode,
            window=window,
        ):
            pipeline.feed_nowait(frame_arr)

        await pipeline.stop()
        await consumer
        if state_path and last_state is not None:
            from .multimodal_out import snapshot_state

            snapshot_state(state_path, last_state)


    asyncio.run(_runner())


def run_image_mode(path: str, vocab_path: str | None = None) -> None:
    """Encode an image file and print basic geometry stats."""
    from .image_encoder import ImageEncoder
    from .tensor_mapper import TensorMapper

    encoder = ImageEncoder(vocab_path=vocab_path)
    tokens = encoder.step(path)
    mapper = TensorMapper()
    mapper.update(tokens)
    state = mapper.to_hlsf()
    print(f"Image tokens: {len(tokens)}")
    print(f"Triangles: {len(state.triangles)}")


def run_fft_mode(
    sr: int = 48000,
    frame: int = 2048,
    hop: int = 512,

    *,
    window: str = "rect",
    n_fft: int = 2048,
    banding: str = "log",
    pre_mode: str = "first_order",
    edges: Sequence[float] | None = None,
    live: bool = False,
    visualizer_cls: Any | None = None,
    use_gpu: bool = False,
    device: str | None = None,
    state_path: str | None = None,
) -> ModelState:
    """Run the experimental FFT pipeline.

    When ``live`` is true the function instantiates ``visualizer_cls`` (defaulting
    to :class:`~hlsf_module.live_visualizer.LiveVisualizer`) and feeds it resonance scores
    and triangle geometry without blocking the pipeline.
    """


    from .signal_io import SignalStream
    from .fft_tokenizer import FFTTokenizer
    from .tensor_mapper import TensorMapper
    from .symbols.schema import SymbolToken
    from . import pruning, clusterer, weights_bp

    model = ModelState()
    stream, _ = SignalStream.from_array(
        [0.0] * frame,
        sr=sr,
        frame=frame,
        hop=hop,
        norm_mode="none",
        window=window,
        pre_mode=pre_mode,
    )

    tokenizer = FFTTokenizer(
        sr=sr,
        n_fft=n_fft,
        hop=hop,
        banding=banding,
        edges=edges,
        use_gpu=use_gpu,
        device=device,
    )

    mapper = TensorMapper(use_gpu=use_gpu, device=device)
    while True:
        frame_arr = stream.read()
        if frame_arr is None:
            break
        raw = tokenizer.step(frame_arr)
        tokens = [
            SymbolToken(
                t=t.t_idx,
                id=t.band,
                mod="audio",
                feat={
                    "mag": t.mag,
                    "dphi": t.dphi,
                    "band": t.band,
                    **({"peak_mag": t.peak_mag} if t.peak_mag is not None else {}),
                    **({"centroid": t.centroid} if t.centroid is not None else {}),
                    **({"bandwidth": t.bandwidth} if t.bandwidth is not None else {}),
                    **({"coherence": t.coherence} if t.coherence is not None else {}),
                    **(t.mods or {}),
                    **({"bands": list(t.bands)} if t.bands else {}),
                },
                w=int(t.mag),
            )
            for t in raw
        ]
        mapper.update(tokens)
        pruned = pruning.apply(mapper.graph)
        removed = clusterer.collapse(mapper.graph)
        weights_bp.update(mapper.graph, pruned + removed, model.weights)
    state = mapper.to_hlsf()
    if state_path:
        from .multimodal_out import snapshot_state

        snapshot_state(state_path, state)
    model.token_graph = mapper.graph

    if live:
        if visualizer_cls is None:
            from .live_visualizer import LiveVisualizer

            visualizer_cls = LiveVisualizer
        vis = visualizer_cls()
        vis.update(model.token_graph, state)
        vis.close()

    print(f"FFT mode produced {len(state.triangles)} triangles")
    return model


def run_training(
    dataset_path: str,
    *,
    weights_db: str | None = None,
    prototypes: str | None = None,
    batch_size: int = 1,
    epochs: int = 1,
) -> None:
    """Train internal models from a dataset."""

    import json
    from .trainer import Trainer
    from .symbols.schema import SymbolToken

    with open(dataset_path, "r", encoding="utf-8") as fh:
        data = json.load(fh)
    dataset = [[SymbolToken(**tok) for tok in sample] for sample in data]
    trainer = Trainer()
    for _ in range(max(1, epochs)):
        trainer.train(dataset, batch_size=batch_size)
    if weights_db:
        trainer.training_db.save(weights_db)
    if prototypes:
        with open(prototypes, "w", encoding="utf-8") as fh:
            json.dump(trainer.resonator.prototypes, fh)


def run_visualizer(path: str | None = None) -> None:
    """Launch the polygon visualizer or display a saved ``HLSFState``."""

    if path:
        import json
        from .tensor_mapper import HLSFState
        from .visualization import HLSFViewer

        with open(path, "r", encoding="utf-8") as fh:
            data = json.load(fh)
        state = HLSFState.from_hlsf(data)
        viewer = HLSFViewer(state)
        viewer.show()
        return

    for lvl in range(1, 6):
        origin = HLSFGenerator.calculate_symmetry_point_adjusted((0, 0), 1, 4, lvl)
        print(f"Level {lvl} origin: {origin}")
    from .visualization import PolygonGUI  # local import; matplotlib optional

    app = PolygonGUI(
        center=(0.0, 0.0),
        radius=1,
        sides=8,
        levels=2,
        is_rotation_animation_running=True,
    )
    app.run()


def run_web_viewer() -> None:
    """Launch the experimental web viewer."""
    print("Starting web viewer server on ws://localhost:8765")
    print("Open docs/client.html in a browser to view geometry updates")


def main(argv: Any | None = None) -> None:
    args = parse_args(argv)
    if getattr(args, "command", None) == "plugins":
        if args.plugins_command == "list":
            for kind, mapping in _plugins.available_plugins().items():
                print(f"{kind}:")
                for name in sorted(mapping):
                    print(f"  {name}")
            return
    if args.export_vocab:
        export_vocab(args.export_vocab)
        return
    if args.import_vocab:
        vocab = import_vocab(args.import_vocab)
        print(f"loaded vocab with {len(vocab)} entries")
        return
    if args.load_state:
        run_visualizer(args.load_state)
        return
    if args.web and not (args.text_fft or args.text or args.mic or args.enable_fft):
        run_web_viewer()
        return
    if getattr(args, "text_fft", None):
        run_text_fft(
            args.text_fft,
            vocab_path=args.vocab,
            collapse=args.collapse_geom,
            rh_mode=args.rh_mode,
            gate_strategy=args.gate_strategy,
            mapping_strategy=args.mapping_strategy,
            llm_provider=args.llm_provider,
            llm_embedding=args.llm_embedding,
            state_path=args.save_state,
        )
    elif args.text:
        run_text_mode(
            args.text,
            res_threshold=args.res_threshold,
            gate_duration=args.gate_duration,
            gate_margin=args.gate_margin,
            gate_detectors=args.gate_detectors,
            gate_coherence=args.gate_coherence,
            gate_peak=args.gate_peak,
            gate_detector_var=args.gate_detector_var,
            gate_strategy=args.gate_strategy,
            gate_percentile=args.gate_percentile,
            gate_var_factor=args.gate_var_factor,
            gate_ema_alpha=args.gate_ema_alpha,
            cross_weight=args.gate_cross_weight,
            gate_prev_threshold=args.gate_prev_threshold,
            gate_k_target=args.gate_k_target,
            gate_weight_resonance=args.gate_weight_resonance,
            gate_weight_k=args.gate_weight_k,
            gate_weight_prime=args.gate_weight_prime,
            gate_weight_harmonic=args.gate_weight_harmonic,
            gate_prime_priority=args.gate_prime_priority,
            mapping_strategy=args.mapping_strategy,
            vocab_path=args.vocab,
            weight_db=args.weights_db,
            state_path=args.save_state,
            mapper_name=args.mapper,
        )
    elif args.mic:
        run_microphone_mode(
            float(args.mic),
            pre_emphasis=args.preemphasis,
            norm_mode=args.norm_mode,
            window=args.window,
            n_fft=args.fft_size,
            banding=args.banding,
            pre_mode=args.pre_mode,
            edges=args.edges,
            res_threshold=args.res_threshold,
            gate_duration=args.gate_duration,
            gate_margin=args.gate_margin,
            gate_detectors=args.gate_detectors,
            gate_coherence=args.gate_coherence,
            gate_peak=args.gate_peak,
            gate_detector_var=args.gate_detector_var,
            gate_strategy=args.gate_strategy,
            gate_percentile=args.gate_percentile,
            gate_var_factor=args.gate_var_factor,
            gate_ema_alpha=args.gate_ema_alpha,
            cross_weight=args.gate_cross_weight,
            gate_prev_threshold=args.gate_prev_threshold,
            gate_k_target=args.gate_k_target,
            gate_weight_resonance=args.gate_weight_resonance,
            gate_weight_k=args.gate_weight_k,
            gate_weight_prime=args.gate_weight_prime,
            gate_weight_harmonic=args.gate_weight_harmonic,
            gate_prime_priority=args.gate_prime_priority,
            mapping_strategy=args.mapping_strategy,
            queue_size=args.queue_size,
            visualizer_cls=None,
            use_gpu=args.use_gpu,
            device=args.device,
            state_path=args.save_state,
        )
    elif args.image:
        run_image_mode(args.image, vocab_path=getattr(args, "vocab", None))
    elif args.enable_fft:
        run_fft_mode(
            live=args.live,
            window=args.window,
            n_fft=args.fft_size,
            banding=args.banding,
            pre_mode=args.pre_mode,
            edges=args.edges,
            use_gpu=args.use_gpu,
            device=args.device,
            state_path=args.save_state,
        )
    elif args.web:
        run_web_viewer()
    else:
        run_visualizer(args.load_state)
        
if __name__ == "__main__":
    main()
