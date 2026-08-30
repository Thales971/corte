from __future__ import annotations

from PIL import Image, ImageDraw, ImageFont

from corte.ocr import OcrResult, _clean_text, _mean_luma, prepare_for_ocr, prepare_variants


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


def test_dark_ui_gets_inverted_variant() -> None:
    dark = Image.new("RGB", (80, 40), (12, 18, 14))
    names = [name for name, _img in prepare_variants(dark)]
    assert "invertido-binario" in names
    assert names[0].startswith("invertido")


def test_clean_text_drops_empty_lines() -> None:
    raw = "  CORTE V2  \n\n  print da tela  \n   \n"
    assert _clean_text(raw) == "CORTE V2\nprint da tela"


def test_ocr_result_preview_trims() -> None:
    from pathlib import Path

    result = OcrResult(
        text="a" * 80,
        confidence=91.2,
        lang="por+eng",
        words=1,
        lines=1,
        source=Path("x.png"),
    )
    assert result.preview(20).endswith("…")
    assert len(result.preview(20)) == 20


def test_mean_luma_dark_vs_light() -> None:
    dark = Image.new("RGB", (10, 10), (8, 8, 8))
    light = Image.new("RGB", (10, 10), (240, 240, 240))
    assert _mean_luma(dark) < 40
    assert _mean_luma(light) > 200
