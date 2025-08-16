import asyncio

from hlsf_module import signal_io
from hlsf_module.stream_pipeline import StreamPipeline


def test_stream_pipeline_order_and_resonance():
    data = [0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, -1.0]
    stream = signal_io.SignalStream(
        data,
        sr=1,
        frame=4,
        hop=4,
        pre_emphasis=0.0,
        norm_mode="none",
        window="rect",
    )
    pipe = StreamPipeline(
        stream=stream,
        queue_size=2,
        encoder_args={"sr": 1, "n_fft": 4, "hop": 4, "bands": 2},
        gate_args={"threshold": 0.0, "margin": 0.0},
    )
    results = []

    async def run():
        async with pipe:
            while True:
                item = await pipe.result_q.get()
                if item is None:
                    break
                results.append(item)

    asyncio.run(run())
    assert len(results) == 2
    first_scores, first_state = results[0]
    second_scores, second_state = results[1]
    assert sum(first_scores.values()) == 0
    assert sum(second_scores.values()) > 0
    assert len(first_state.triangles) < len(second_state.triangles)
    assert pipe._mapper.symbolic_resonance_index() > 0
