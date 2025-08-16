from hlsf_module.symbols.encoding import decode_symbol, encode_symbol


def test_encoding_roundtrip_and_collisions():
    seen = set()
    for i in range(32):
        seq = encode_symbol(i)
        assert decode_symbol(seq) == i
        tup = tuple(seq)
        assert tup not in seen
        seen.add(tup)
