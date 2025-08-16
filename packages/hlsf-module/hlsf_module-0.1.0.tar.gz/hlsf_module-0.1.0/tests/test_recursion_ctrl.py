from hlsf_module import recursion_ctrl


def test_update_and_reset_behaviour() -> None:
    ctrl = recursion_ctrl.RecursionController(window=3, threshold=0.5)

    assert ctrl.update(10.0)
    assert ctrl.update(10.0)
    # No improvement in resonance index should trigger a stop
    assert not ctrl.update(10.0)

    ctrl.reset()
    assert ctrl.update(10.0)


def test_gain_metrics() -> None:
    mean_ctrl = recursion_ctrl.RecursionController(
        window=3, threshold=0.1, gain_metric="mean"
    )
    mean_ctrl.update(1.0)
    mean_ctrl.update(1.0)
    assert not mean_ctrl.update(1.05)
    median_ctrl = recursion_ctrl.RecursionController(
        window=3, threshold=0.5, gain_metric="median"
    )
    median_ctrl.update(1.0)
    median_ctrl.update(1.0)
    assert median_ctrl.update(2.0)
