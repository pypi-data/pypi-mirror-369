import pytest

pytest.importorskip("PIL")
from PIL import Image

from hlsf_module.image_encoder import ImageEncoder
from hlsf_module.tensor_mapper import TensorMapper
from hlsf_module.symbols.schema import SymbolToken


def test_image_tokens_no_id_collision(tmp_path):
    img = Image.new("L", (2, 2))
    img.putdata([0, 64, 128, 255])
    path = tmp_path / "img.png"
    img.save(path)

    enc = ImageEncoder()
    img_tokens = enc.step(path)
    assert all(t.mod == "image" for t in img_tokens)

    text_tok = SymbolToken(t=0, id=img_tokens[0].id, mod="text", feat={"mag": 1.0}, w=1)
    mapper = TensorMapper()
    mapper.update(img_tokens + [text_tok])
    state = mapper.to_hlsf()
    assert len(state.triangles) == len(img_tokens) + 1


def test_rgb_channels(tmp_path):
    img = Image.new("RGB", (2, 2))
    img.putdata([(0, 0, 0), (64, 64, 64), (128, 128, 128), (255, 255, 255)])
    enc = ImageEncoder(mode="RGB")
    tokens = enc.step(img)
    chans = {t.feat.get("c") for t in tokens}
    assert {0, 1, 2}.issubset(chans)


def test_volume_slices(tmp_path):
    f1 = Image.new("L", (2, 2), 0)
    f2 = Image.new("L", (2, 2), 255)
    path = tmp_path / "vol.tiff"
    f1.save(path, save_all=True, append_images=[f2])
    enc = ImageEncoder(mode="3D")
    tokens = enc.step(path)
    slices = {t.feat.get("c") for t in tokens}
    assert {0, 1}.issubset(slices)
