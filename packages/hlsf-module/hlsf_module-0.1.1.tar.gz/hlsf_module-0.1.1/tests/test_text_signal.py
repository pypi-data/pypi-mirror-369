from hlsf_module.text_signal import text_to_signal_tokens


def test_text_signal_deterministic_and_format():
    tokens1 = text_to_signal_tokens(["hi", "there"], n_fft=8, bands=2)
    tokens2 = text_to_signal_tokens(["hi", "there"], n_fft=8, bands=2)
    assert tokens1 == tokens2
    assert all(t.mod == "audio" for t in tokens1)
    assert all({"mag", "dphi", "band"} <= set(t.feat) for t in tokens1)

