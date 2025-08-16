from hlsf_module.cli import run_fft_mode, ModelState


def test_run_fft_mode_basic() -> None:
    model = run_fft_mode()
    assert isinstance(model, ModelState)
    assert isinstance(model.token_graph, dict)
