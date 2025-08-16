import asyncio

from hlsf_module.text_stream_pipeline import TextStreamPipeline
from hlsf_module.llm_client import StubLLMClient
from hlsf_module.tensor_mapper import HLSFState


def test_text_stream_pipeline_basic() -> None:
    stub = StubLLMClient(["foo"])
    pipe = TextStreamPipeline(llm=stub, queue_size=2, prune_threshold=0.0)
    results: list[tuple[dict, HLSFState]] = []

    async def run() -> None:
        async with pipe:
            await pipe.feed_text("hi")
            await pipe.token_q.put(None)
            while True:
                item = await pipe.result_q.get()
                if item is None:
                    break
                results.append(item)

    asyncio.run(run())
    assert results
    scores, state = results[0]
    assert state.triangles
    assert stub.calls >= 2
    assert scores
