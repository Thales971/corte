from __future__ import annotations

from PIL import Image, ImageDraw, ImageFont

from corte.ocr import prepare_for_ocr


def test_prepare_returns_high_contrast_rgb() -> None:
    img = Image.new("RGB", (120, 40), (30, 30, 30))
    draw = ImageDraw.Draw(img)
    draw.text((8, 10), "CORTE V2", fill=(240, 240, 240), font=ImageFont.load_default())
    out = prepare_for_ocr(img)
    assert out.mode == "RGB"
    assert out.width >= img.width
    assert out.height >= img.height
    extremes = {(0, 0, 0), (255, 255, 255)}
    sample = {out.getpixel((x, 10)) for x in range(0, out.width, 8)}
    assert sample <= extremes
