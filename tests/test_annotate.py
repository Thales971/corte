from __future__ import annotations

from PIL import Image

from corte.annotate import Stroke, apply_stroke, draw_arrow, hex_rgb


def _blank() -> Image.Image:
    return Image.new("RGB", (120, 80), (18, 24, 20))


def test_arrow_changes_pixels() -> None:
    src = _blank()
    out = draw_arrow(src, (10, 40), (100, 40), color="#7CFFB2", width=4)
    assert out.size == src.size
    assert out.tobytes() != src.tobytes()


def test_number_and_crop_pipeline() -> None:
    src = _blank()
    numbered = apply_stroke(src, Stroke("numero", (30, 30), (30, 30), number=3))
    cropped = apply_stroke(numbered, Stroke("cortar", (10, 10), (70, 60)))
    assert cropped.width == 60
    assert cropped.height == 50


def test_highlight_keeps_size() -> None:
    src = _blank()
    out = apply_stroke(src, Stroke("marca", (5, 5), (80, 40), color="#C8F54A"))
    assert out.size == src.size
    assert out.tobytes() != src.tobytes()


def test_hex_rgb_short_and_invalid() -> None:
    assert hex_rgb("#0f0") == (0, 255, 0)
    assert hex_rgb("nope") == (124, 255, 178)
