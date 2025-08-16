import asyncio
import pytest

from hlsf_module.fft_tokenizer import FFTTokenizer
from hlsf_module.tensor_mapper import TensorMapper, HLSFState
from hlsf_module.stream_pipeline import StreamPipeline
from hlsf_module.signal_io import SignalStream
from hlsf_module.trainer import Trainer
from hlsf_module.resonator import SymbolResonator
from hlsf_module.symbols.schema import SymbolToken


def _require_cuda():
    torch = pytest.importorskip("torch")
    if not torch.cuda.is_available():
        pytest.skip("CUDA required for GPU tests")
    return torch


def test_fft_tokenizer_gpu():
    _require_cuda()
    tok = FFTTokenizer(sr=8000, n_fft=16, hop=16, n_bands=4, use_gpu=True, device="cuda")
    frame = [0.0] * 16
    tokens = tok.step(frame)
    assert tokens == tok.step(frame)


def test_tensor_mapper_gpu():
    _require_cuda()
    mapper = TensorMapper(use_gpu=True, device="cuda")
    token = SymbolToken(t=0, id=1, mod="audio", feat={"mag": 1.0})
    mapper.update([token])
    state = mapper.to_hlsf()
    assert state.triangles and state.colors


def test_stream_pipeline_gpu():
    _require_cuda()
    stream = SignalStream([0.0] * 32, sr=8, frame=16, hop=16)
    pipe = StreamPipeline(
        stream=stream,
        encoder_args={"sr": 8, "n_fft": 16, "hop": 16, "bands": 4},
        use_gpu=True,
        device="cuda",
    )
    results: list[tuple[dict, HLSFState]] = []

    async def run() -> None:
        async with pipe:
            while True:
                item = await pipe.result_q.get()
                if item is None:
                    break
                results.append(item)

    asyncio.run(run())
    assert results and isinstance(results[0][1].triangles, list)


def test_trainer_gpu():
    _require_cuda()
    trainer = Trainer(resonator=SymbolResonator(use_gpu=True, device="cuda"))
    dataset = [
        {"audio": [SymbolToken(t=0, id=1, mod="audio", feat={"band": 1, "mag": 0.5})]},
        {"audio": [SymbolToken(t=1, id=1, mod="audio", feat={"band": 1, "mag": 0.5})]},
    ]
    trainer.train(dataset)
    assert trainer.training_db.connections
