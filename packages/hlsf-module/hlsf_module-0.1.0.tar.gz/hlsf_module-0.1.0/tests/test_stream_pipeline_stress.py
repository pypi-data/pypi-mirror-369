import asyncio

from hlsf_module.stream_pipeline import StreamPipeline


def test_stress_backpressure_and_shutdown() -> None:
    pipe = StreamPipeline(
        queue_size=2,
        encoder_args={"sr": 1, "n_fft": 4, "hop": 4, "bands": 2},
    )
    max_q = 0

    async def run() -> None:
        nonlocal max_q
        async with pipe:
            async def producer() -> None:
                nonlocal max_q
                for _ in range(50):
                    await pipe.feed_frame([0.0, 0.0, 0.0, 0.0])
                    max_q = max(max_q, pipe.frame_q.qsize())
            async def consumer() -> None:
                while True:
                    item = await pipe.result_q.get()
                    if item is None:
                        break
                    await asyncio.sleep(0.01)

            prod_task = asyncio.create_task(producer())
            cons_task = asyncio.create_task(consumer())
            await prod_task
            await pipe.stop()
            await pipe.result_q.put(None)
            await cons_task

    asyncio.run(run())
    assert max_q <= pipe.frame_q.maxsize
    assert pipe.frame_q.qsize() == 0
    assert pipe._tasks == []

