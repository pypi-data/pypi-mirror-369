from math import pi, sin
import pytest

from hlsf_module.resonator import SymbolResonator
from hlsf_module.symbols.schema import SymbolToken
from hlsf_module.text_signal import text_to_signal_tokens
from hlsf_module.enc_audio import AudioEncoder
from hlsf_module.signal_io import SignalStream
from hlsf_module.symbols.vocab import Vocab


def test_resonator_update_and_score():
    res = SymbolResonator(decay=0.5)
    tok1 = SymbolToken(t=0, id=1, mod="m", feat={"x": 1.0})
    res.update(tok1)
    assert res.prototypes[1] == [1.0]
    tok2 = SymbolToken(t=0, id=1, mod="m", feat={"x": 0.0})
    res.update(tok2)
    assert res.prototypes[1] == [0.5]
    assert res.score(tok1) == pytest.approx(1.0)
    assert res.score(tok2) == 0.0


def test_text_resonance_integration():
    res = SymbolResonator()
    tokens = text_to_signal_tokens(["hi"], n_fft=8, bands=2)
    res.update_batch(tokens)
    tokens2 = text_to_signal_tokens(["hi"], n_fft=8, bands=2, resonator=res)
    assert all("res" in t.feat for t in tokens2)
    assert tokens2[0].feat["res"] == pytest.approx(1.0, rel=1e-2)


def test_audio_resonance_integration():
    sr, frame, hop = 48000, 64, 64
    x = [sin(2 * pi * 440 * n / sr) for n in range(frame)]
    stream, _ = SignalStream.from_array(x, sr=sr, frame=frame, hop=hop)
    res = SymbolResonator()
    enc = AudioEncoder(sr=sr, n_fft=64, hop=hop, bands=8, vocab=Vocab(), resonator=res)
    tokens = enc.step(stream.read())
    res.update_batch(tokens)
    stream, _ = SignalStream.from_array(x, sr=sr, frame=frame, hop=hop)
    tokens2 = enc.step(stream.read())
    assert all("res" in t.feat for t in tokens2)
    assert tokens2[0].feat["res"] == pytest.approx(1.0, rel=1e-2)
