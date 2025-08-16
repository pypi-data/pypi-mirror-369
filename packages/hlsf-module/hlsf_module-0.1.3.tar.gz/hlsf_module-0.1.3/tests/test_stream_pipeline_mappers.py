import asyncio
import math

from hlsf_module import signal_io
from hlsf_module.stream_pipeline import StreamPipeline


async def _run_pipeline(pipe: StreamPipeline):
    results = []
    async with pipe:
        while True:
            item = await pipe.result_q.get()
            if item is None:
                break
            results.append(item)
    return results


async def _simple_stream(mapper_name: str):
    stream = signal_io.SignalStream([0.0, 0.1, 0.2, 0.3], sr=1, frame=4, hop=2, pre_emphasis=0.0, norm_mode="none", window="rect")
    pipe = StreamPipeline(stream=stream, queue_size=2, encoder_args={"sr": 1, "n_fft": 4, "hop": 2, "bands": 1}, mapper=mapper_name)
    return await _run_pipeline(pipe)


import pytest


@pytest.mark.parametrize("mapper_name,verts,dim", [
    ("square", 4, 2),
    ("pentagon", 5, 2),
    ("bar", 4, 2),
    ("pyramid", 5, 3),
])
def test_stream_pipeline_mappers(mapper_name, verts, dim):
    results = asyncio.run(_simple_stream(mapper_name))
    assert results
    state = results[0][1]
    poly = state.triangles[0]
    assert len(poly) == verts
    assert len(poly[0]) == dim
    # ensure coordinates are floats
    assert all(isinstance(v, float) for pt in poly for v in pt)
