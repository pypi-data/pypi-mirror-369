from hlsf_module.symbols.vocab import Vocab



def test_vocab_stable_ids():
    v1 = Vocab()
    ids1 = [v1.id("audio", b) for b in [0, 1, 2]]
    v2 = Vocab()
    ids2 = [v2.id("audio", b) for b in [0, 1, 2]]
    assert ids1 == ids2
    assert v1.id("audio", 0) == ids1[0]
    assert v1.id("audio", 1) == ids1[1]


def test_vocab_save_load_rebuild(tmp_path):
    v = Vocab()
    seq = [v.id("audio", b) for b in [0, 1, 2]]
    path = tmp_path / "vocab.json"
    v.save(path)
    v_loaded = Vocab.load(path)
    # IDs should remain the same after reloading
    assert [v_loaded.id("audio", b) for b in [0, 1, 2]] == seq
    # New tokens should get new IDs after loading
    new_id = v_loaded.id("audio", 3)
    assert new_id == len(seq)
