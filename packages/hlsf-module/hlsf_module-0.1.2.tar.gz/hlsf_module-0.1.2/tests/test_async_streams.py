import asyncio
import pytest

from hlsf_module import signal_io
from hlsf_module.stream_pipeline import StreamPipeline


def test_capture_file(tmp_path):
    path = tmp_path / "samples.txt"
    path.write_text("0.0 0.1 0.2 0.3 0.4 0.5")

    async def run():
        frames = []
        with path.open() as fh:
            async for fr in signal_io.capture_file(fh, sr=1, frame=4, hop=2):
                frames.append(fr)
        assert frames

    asyncio.run(run())


def test_capture_socket():
    async def run():
        reader = asyncio.StreamReader()
        reader.feed_data(b"0.0 0.1 0.2 0.3 0.4 0.5")
        reader.feed_eof()
        frames = []
        async for fr in signal_io.capture_socket(reader, sr=1, frame=4, hop=2):
            frames.append(fr)
        assert frames

    asyncio.run(run())


def test_capture_file_large(tmp_path):
    path = tmp_path / "big.txt"
    # generate a large set of samples to exercise streaming behaviour
    N = 10000
    path.write_text(" ".join(str(float(i)) for i in range(N)))

    async def run():
        count = 0
        with path.open() as fh:
            async for _ in signal_io.capture_file(fh, sr=1, frame=4, hop=4):
                count += 1
        assert count == N // 4

    asyncio.run(run())


def test_capture_socket_streaming():
    async def run():
        reader = asyncio.StreamReader()
        frames: list[list[float]] = []

        async def consumer():
            async for fr in signal_io.capture_socket(
                reader, sr=1, frame=4, hop=4, norm_mode="none"
            ):
                frames.append(fr)

        task = asyncio.create_task(consumer())
        reader.feed_data(b"0 1 2 3 ")
        await asyncio.sleep(0)
        # After the first chunk we should already have a frame
        assert frames

        reader.feed_data(b"4 5 6 7 8 9 10 11 ")
        reader.feed_eof()
        await task
        assert len(frames) == 3

    asyncio.run(run())


def test_stream_pipeline_error_shutdown():
    stream = signal_io.SignalStream(
        [0.0, 0.1, 0.2, 0.3],
        sr=1,
        frame=4,
        hop=2,
        pre_emphasis=0.0,
        norm_mode="none",
        window="rect",
    )
    pipe = StreamPipeline(stream=stream, queue_size=2, encoder_args={"sr": 1, "n_fft": 4, "hop": 2, "bands": 2})

    def faulty_read():
        raise RuntimeError("boom")

    pipe.stream.read = faulty_read  # type: ignore[assignment]

    async def run():
        with pytest.raises(RuntimeError):
            async with pipe:
                await asyncio.sleep(0)
        assert all(t.cancelled() or t.done() for t in pipe._tasks)

    asyncio.run(run())
