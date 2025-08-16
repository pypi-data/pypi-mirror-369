from math import pi, sin

from math import pi, sin
import pytest

from hlsf_module.signal_io import SignalStream
from hlsf_module.enc_audio import AudioEncoder
from hlsf_module.symbols.vocab import Vocab
from hlsf_module.fft_tokenizer import FFTTokenizer, _rfft


def test_audio_encoder_deterministic():
    sr, frame, hop = 48000, 64, 64
    x = [sin(2 * pi * 440 * n / sr) for n in range(frame)]
    stream, _ = SignalStream.from_array(x, sr=sr, frame=frame, hop=hop)
    enc = AudioEncoder(sr=sr, n_fft=64, hop=hop, bands=8, vocab=Vocab())
    tokens1 = enc.step(stream.read())
    stream, _ = SignalStream.from_array(x, sr=sr, frame=frame, hop=hop)

    enc = AudioEncoder(sr=sr, n_fft=64, hop=hop, bands=8, vocab=Vocab())
    tokens2 = enc.step(stream.read())
    assert tokens1 == tokens2

def test_fft_tokenizer_deterministic():
    sr, n_fft, hop, bands = 48000, 64, 64, 8
    x = [sin(2 * pi * 440 * n / sr) for n in range(n_fft)]
    tok1 = FFTTokenizer(sr=sr, n_fft=n_fft, hop=hop, n_bands=bands)
    tok2 = FFTTokenizer(sr=sr, n_fft=n_fft, hop=hop, n_bands=bands)
    tokens1 = tok1.step(x)
    tokens2 = tok2.step(x)
    feat = lambda t: (
        t.band,
        round(t.mag, 6),
        round(t.dphi, 6),
        round(t.peak_mag or 0.0, 6),
        round(t.centroid or 0.0, 6),
        round(t.bandwidth or 0.0, 6),
        round(t.coherence or 0.0, 6),
    )
    assert [feat(t) for t in tokens1] == [feat(t) for t in tokens2]

def test_rfft_handles_multiple_sizes():
    sr = 24
    freq = 6
    for n_fft in (8, 12):
        frame = [sin(2 * pi * freq * n / sr) for n in range(n_fft)]
        spec = _rfft(frame, n_fft)
        k = int(freq * n_fft / sr)
        assert len(spec) == n_fft // 2 + 1
        assert abs(spec[k]) == pytest.approx(n_fft / 2, rel=1e-4)


def test_fft_tokenizer_linear_banding():
    sr, n_fft, hop, bands = 100, 20, 20, 5
    freq = 30
    frame = [sin(2 * pi * freq * n / sr) for n in range(n_fft)]
    tok_lin = FFTTokenizer(sr=sr, n_fft=n_fft, hop=hop, n_bands=bands, banding="lin")
    bands_lin = [t.band for t in tok_lin.step(frame)]
    assert 2 in bands_lin
    tok_log = FFTTokenizer(sr=sr, n_fft=n_fft, hop=hop, n_bands=bands, banding="log")
    bands_log = [t.band for t in tok_log.step(frame)]
    assert bands_lin != bands_log


def test_fft_tokenizer_without_torch(monkeypatch):
    import importlib
    import builtins
    import sys

    real_import = builtins.__import__

    def fake_import(name, *args, **kwargs):
        if name == "torch":
            raise ImportError("torch not available")
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", fake_import)
    monkeypatch.delitem(sys.modules, "torch", raising=False)
    monkeypatch.delitem(sys.modules, "hlsf_module.fft_backends", raising=False)
    monkeypatch.delitem(sys.modules, "hlsf_module.fft_tokenizer", raising=False)

    ft = importlib.import_module("hlsf_module.fft_tokenizer")
    tok = ft.FFTTokenizer(sr=8, n_fft=8, hop=4, n_bands=2, use_gpu=False)
    assert not tok._use_torch

