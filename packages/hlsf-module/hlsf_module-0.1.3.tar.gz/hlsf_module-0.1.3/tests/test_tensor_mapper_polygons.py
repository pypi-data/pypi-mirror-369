from hlsf_module.tensor_mapper import TensorMapper
from hlsf_module.symbols.schema import SymbolToken


def test_polygon_output_shape_and_color_range():
    mapper = TensorMapper()
    tokens = [
        SymbolToken(
            t=0,
            id=1,
            mod="text",
            feat={"mag": 1.0, "phase": 0.25, "centroid": 0.5},
            w=1.0,
        )
    ]
    mapper.update(tokens)
    state = mapper.to_hlsf()
    assert len(state.triangles) == 1
    tri = state.triangles[0]
    assert len(tri) == 3
    for pt in tri:
        assert len(pt) == 2
        assert all(isinstance(v, float) for v in pt)
    color = state.colors[0]
    assert len(color) == 4
    assert all(0.0 <= c <= 1.0 for c in color)
