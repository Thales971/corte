from __future__ import annotations

from corte.settings import Settings


def test_clamp_rejects_garbage() -> None:
    s = Settings(delay_seconds=99, fps=120, image_format="JPG", jpeg_quality=5)
    s.clamp()
    assert s.delay_seconds == 15
    assert s.fps == 30
    assert s.image_format == "jpeg"
    assert s.jpeg_quality == 40


def test_defaults_are_sane() -> None:
    s = Settings().clamp()
    assert s.image_format == "png"
    assert s.copy_image is True
    assert 0 <= s.delay_seconds <= 15
