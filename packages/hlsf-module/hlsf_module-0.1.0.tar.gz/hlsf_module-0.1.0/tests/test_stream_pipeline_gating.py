import asyncio
import pathlib
import sys

sys.path.append(str(pathlib.Path(__file__).resolve().parents[1]))

from hlsf_module import signal_io
from hlsf_module.stream_pipeline import StreamPipeline


def test_stream_pipeline_filters_low_energy() -> None:
    stream = signal_io.SignalStream(
        [0.0] * 8,
        sr=1,
        frame=4,
        hop=4,
        pre_emphasis=0.0,
        norm_mode="none",
        window="rect",
    )
    pipe = StreamPipeline(
        stream=stream,
        queue_size=1,
        encoder_args={"sr": 1, "n_fft": 4, "hop": 4, "bands": 2},
    )
    scores = []

    async def run() -> None:
        async with pipe:
            while True:
                item = await pipe.result_q.get()
                if item is None:
                    break
                sc, _ = item
                scores.append(sc)

    asyncio.run(run())
    assert all(not s for s in scores)
