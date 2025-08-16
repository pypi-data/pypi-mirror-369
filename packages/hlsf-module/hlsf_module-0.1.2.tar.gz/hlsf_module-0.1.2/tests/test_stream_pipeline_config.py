import asyncio

from hlsf_module import signal_io
from hlsf_module.stream_pipeline import StreamPipeline


def test_stream_pipeline_configuration() -> None:
    pipe = StreamPipeline(
        queue_size=5,
        latency_window=5,
        latency_threshold=0.1,
        high_wm_perc=0.7,
        low_wm_perc=0.3,
        max_queue_size=10,
    )
    assert pipe._latency_window == 5
    assert pipe._latency_threshold == 0.1
    assert pipe.high_wm == int(pipe.queue_size * 0.7)
    assert pipe.low_wm == int(pipe.queue_size * 0.3)
    assert pipe.max_queue_size == 10


def test_stream_pipeline_error_callback(monkeypatch) -> None:
    stream = signal_io.SignalStream(
        [0.0, 0.1, 0.2, 0.3],
        sr=1,
        frame=4,
        hop=2,
        pre_emphasis=0.0,
        norm_mode="none",
        window="rect",
    )
    errors = []
    pipe = StreamPipeline(stream=stream, encoder_args={"sr": 1, "n_fft": 4, "hop": 2, "bands": 2}, error_callback=lambda e: errors.append(e))

    def boom(self, frame):
        raise RuntimeError("boom")

    monkeypatch.setattr("hlsf_module.enc_audio.AudioEncoder.step", boom)

    async def run() -> None:
        async with pipe:
            await pipe.feed_frame([0.0, 0.0, 0.0, 0.0])
            await asyncio.sleep(0)

    asyncio.run(run())
    assert errors and isinstance(errors[0], RuntimeError)
    assert all(t.cancelled() or t.done() for t in pipe._tasks)
