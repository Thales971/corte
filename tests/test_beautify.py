from __future__ import annotations

from PIL import Image

from corte.beautify import apply_frame, blur_region, pixelate


def _sample() -> Image.Image:
    img = Image.new("RGB", (80, 40), (20, 40, 30))
    for x in range(80):
        img.putpixel((x, 20), (220, 255, 230))
    return img


def test_frame_grows_canvas() -> None:
    src = _sample()
    framed = apply_frame(src, padding=10, radius=4, shadow=8, background="#0B0F0C")
    assert framed.width > src.width
    assert framed.height > src.height
    assert framed.mode == "RGB"


def test_frame_zero_keeps_size() -> None:
    src = _sample()
    framed = apply_frame(src, padding=0, radius=0, shadow=0)
    assert framed.size == src.size


def test_pixelate_changes_region() -> None:
    src = _sample()
    out = pixelate(src, (0, 0, 40, 40), block=8)
    assert out.size == src.size
    assert out.tobytes() != src.tobytes()


def test_blur_changes_region() -> None:
    src = _sample()
    out = blur_region(src, (10, 5, 50, 30), radius=6)
    assert out.size == src.size
    assert out.tobytes() != src.tobytes()
