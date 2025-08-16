import asyncio

from hlsf_module import signal_io
from hlsf_module.stream_pipeline import StreamPipeline
from hlsf_module.tensor_mapper import HLSFState


def test_stream_pipeline_synthetic() -> None:
    stream = signal_io.SignalStream(
        [0.0, 0.1, 0.2, 0.3, 0.4, 0.5],
        sr=1,
        frame=4,
        hop=2,
        pre_emphasis=0.0,
        norm_mode="none",
        window="rect",
    )
    pipe = StreamPipeline(
        stream=stream,
        queue_size=2,
        encoder_args={"sr": 1, "n_fft": 4, "hop": 2, "bands": 2},
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
    assert results
    assert isinstance(results[0][1], HLSFState)
    assert pipe.frame_q.qsize() == 0
