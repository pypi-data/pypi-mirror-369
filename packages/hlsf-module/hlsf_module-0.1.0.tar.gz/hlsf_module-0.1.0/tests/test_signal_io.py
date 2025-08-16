import math
import sys, pathlib
import random
import math
import sys
import pathlib
import pytest

sys.path.append(str(pathlib.Path(__file__).resolve().parents[1]))

from hlsf_module.signal_io import SignalStream


@pytest.mark.parametrize("window", ["hann", "hamming", "blackman", "rect"])
def test_read_applies_pre_emphasis_and_window(window):
    data = [1.0, 2.0, 4.0, 8.0]
    sr, frame, hop, pre = 8000, 4, 4, 0.5
    stream = SignalStream(
        data,
        sr=sr,
        frame=frame,
        hop=hop,
        pre_emphasis=pre,
        pre_mode="first_order",
        window=window,
    )
    out = stream.read()
    assert out is not None

    max_val = max(data)
    expected = [x / max_val for x in data]
    for i in range(frame - 1, 0, -1):
        expected[i] -= pre * expected[i - 1]
    if window == "hann":
        win = [0.5 - 0.5 * math.cos(2 * math.pi * i / (frame - 1)) for i in range(frame)]
    elif window == "hamming":
        win = [0.54 - 0.46 * math.cos(2 * math.pi * i / (frame - 1)) for i in range(frame)]
    elif window == "blackman":
        win = [
            0.42 - 0.5 * math.cos(2 * math.pi * i / (frame - 1)) + 0.08 * math.cos(4 * math.pi * i / (frame - 1))
            for i in range(frame)
        ]
    else:
        win = [1.0] * frame
    expected = [f * w for f, w in zip(expected, win)]

    assert out == pytest.approx(expected)
      
def test_dc_block_pre_mode():
    data = [1.0, 2.0, 4.0, 8.0]
    sr, frame, hop, pre = 8000, 4, 4, 0.5
    stream = SignalStream(
        data,
        sr=sr,
        frame=frame,
        hop=hop,
        pre_emphasis=pre,
        pre_mode="dc_block",
        window="rect",
    )
    out = stream.read()
    assert out is not None

    max_val = max(data)
    expected = [x / max_val for x in data]
    prev_x = expected[0]
    prev_y = 0.0
    for i in range(frame):
        y = expected[i] - prev_x + pre * prev_y
        prev_x = expected[i]
        prev_y = y
        expected[i] = y
    assert out == pytest.approx(expected)

def test_stream_iteration_yields_all_frames():
    data = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7]
    sr, frame, hop = 8, 4, 4
    stream, _ = SignalStream.from_array(data, sr=sr, frame=frame, hop=hop)
    frames_iter = list(iter(stream.read, None))

    stream2, _ = SignalStream.from_array(data, sr=sr, frame=frame, hop=hop)
    frames_manual = [stream2.read(), stream2.read()]

    assert frames_iter == frames_manual
    assert stream.read() is None
