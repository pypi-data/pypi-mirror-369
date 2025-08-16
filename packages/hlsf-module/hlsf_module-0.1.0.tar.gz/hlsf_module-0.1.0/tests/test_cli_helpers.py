from hlsf_module.cli import (
    ModelState,
    parse_args,
    run_fft_mode,
    run_microphone_mode,
    run_text_mode,
    run_visualizer,
)


def test_run_fft_mode() -> None:
    model = run_fft_mode()
    assert isinstance(model, ModelState)
    assert isinstance(model.token_graph, dict)


def test_run_fft_mode_live(monkeypatch) -> None:
    called = {}

    class DummyVis:
        def __init__(self):
            called["init"] = True

        def update(self, scores, state):
            called["update"] = (scores, state)

        def close(self):
            called["close"] = True

    model = run_fft_mode(live=True, visualizer_cls=DummyVis)
    assert called.get("init")
    assert called.get("update")


def test_run_text_mode(capsys) -> None:
    run_text_mode("hi")
    captured = capsys.readouterr()
    assert "Triangles" in captured.out


def test_run_microphone_mode(monkeypatch) -> None:
    import sys
    import types
    import asyncio
    import hlsf_module.cli as cli
    import hlsf_module.stream_pipeline as sp


    async def fake_capture(*a, **k):  # pragma: no cover - generator stub
        if False:
            yield []

    dummy_signal = types.SimpleNamespace(capture_microphone=fake_capture)
    monkeypatch.setitem(sys.modules, "hlsf_module.signal_io", dummy_signal)

    class DummyPipeline:
        def __init__(self, *a, **k):
            self.result_q = asyncio.Queue()

        async def start(self):
            pass

        def feed_nowait(self, frame):
            pass

        async def stop(self):
            await self.result_q.put(None)

        async def join(self):
            pass

    monkeypatch.setattr(sp, "StreamPipeline", DummyPipeline)

    class DummyVis:
        def __init__(self):
            pass

        def update(self, scores, state):  # pragma: no cover - stub
            pass

        def close(self):
            pass

    cli.run_microphone_mode(0.01, visualizer_cls=DummyVis)


def test_run_microphone_mode_streaming(monkeypatch) -> None:
    import sys
    import types
    import asyncio
    import hlsf_module.cli as cli
    import hlsf_module.stream_pipeline as sp

    frames = [[0.0], [0.1]]

    async def fake_capture(*a, **k):
        for fr in frames:
            yield fr

    dummy_signal = types.SimpleNamespace(capture_microphone=fake_capture)
    monkeypatch.setitem(sys.modules, "hlsf_module.signal_io", dummy_signal)

    seen: list = []

    class DummyPipeline:
        def __init__(self, *a, **k):
            self.result_q = asyncio.Queue()

        async def start(self):
            pass

        def feed_nowait(self, frame):
            seen.append(frame)

        async def stop(self):
            await self.result_q.put(None)

        async def join(self):
            pass

    monkeypatch.setattr(sp, "StreamPipeline", DummyPipeline)

    class DummyVis:
        def __init__(self):
            pass

        def update(self, scores, state):  # pragma: no cover - stub
            pass

        def close(self):
            pass

    cli.run_microphone_mode(0.01, frame=1, hop=1, visualizer_cls=DummyVis)
    assert seen == frames



def test_run_visualizer(monkeypatch) -> None:
    from hlsf_module import visualization

    called = {}

    class DummyGUI:
        def __init__(self, *a, **k):
            called["init"] = True

        def run(self):
            called["run"] = True

    monkeypatch.setattr(visualization, "PolygonGUI", DummyGUI)
    run_visualizer()
    assert called.get("run")


def test_parse_args(tmp_path) -> None:
    edge = tmp_path / "edges.txt"
    edge.write_text("0 1 2")
    args = parse_args([
        "run",
        "--enable-fft",
        "--banding",
        "mel",
        "--edge-file",
        str(edge),
        "--window",
        "blackman",
        "--pre-mode",
        "dc_block",
    ])
    assert args.banding == "mel"
    assert args.edge_file == str(edge)

    assert args.window == "blackman"
    assert args.pre_mode == "dc_block"


def test_parse_args_invalid_preemphasis() -> None:
    """``parse_args`` rejects out-of-range pre-emphasis values."""
    import pytest

    with pytest.raises(SystemExit):
        parse_args(["run", "--preemphasis", "1.2"])


def test_parse_args_invalid_fft_size() -> None:
    """Non power-of-two FFT sizes should trigger a parser error."""
    import pytest

    with pytest.raises(SystemExit):
        parse_args(["run", "--fft-size", "300"])


def test_validate_args_rejects_bad_fft_size() -> None:
    """Internal validator guards against non power-of-two sizes."""
    import argparse
    import pytest
    from hlsf_module.cli import _validate_args

    ns = argparse.Namespace(
        preemphasis=0.5, fft_size=300, res_threshold=0.5, gate_duration=1
    )
    with pytest.raises(ValueError):
        _validate_args(ns)
