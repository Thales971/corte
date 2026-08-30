from __future__ import annotations

from pathlib import Path

from PIL import Image

from corte.capture import shot_from_image
from corte.settings import Settings


def test_saves_png_in_given_folder(tmp_path: Path) -> None:
    img = Image.new("RGB", (24, 16), (10, 80, 40))
    result = shot_from_image(img, prefix="teste", settings=Settings(image_format="png"), folder=tmp_path)
    assert result.path.parent == tmp_path
    assert result.path.suffix == ".png"
    assert result.path.exists()
    saved = Image.open(result.path)
    assert saved.size == (24, 16)


def test_saves_jpeg_when_asked(tmp_path: Path) -> None:
    img = Image.new("RGB", (20, 12), (200, 30, 30))
    result = shot_from_image(
        img, prefix="foto", settings=Settings(image_format="jpeg", jpeg_quality=80), folder=tmp_path
    )
    assert result.path.suffix == ".jpg"
    assert result.path.exists()
