from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from PIL import Image

from corte.paths import stamp
from corte.settings import Settings, load_settings


@dataclass
class ShotResult:
    path: Path
    width: int
    height: int
    monitor: int


def _grab(monitor: dict) -> Image.Image:
    import mss

    with mss.mss() as sct:
        raw = sct.grab(monitor)
        return Image.frombytes("RGB", raw.size, raw.bgra, "raw", "BGRX")


def list_monitors() -> list[dict]:
    import mss

    with mss.mss() as sct:
        return list(sct.monitors)


def _save(
    image: Image.Image,
    prefix: str,
    settings: Settings | None = None,
    folder: Path | None = None,
) -> Path:
    cfg = settings or load_settings()
    ext = "jpg" if cfg.image_format == "jpeg" else cfg.image_format
    path = stamp(prefix, ext, folder=folder)
    if cfg.image_format == "jpeg":
        image.convert("RGB").save(path, "JPEG", quality=cfg.jpeg_quality, optimize=True)
    elif cfg.image_format == "webp":
        image.save(path, "WEBP", quality=cfg.jpeg_quality, method=6)
    else:
        image.save(path, "PNG", optimize=True)
    return path


def shot_full(monitor_index: int | None = None, settings: Settings | None = None) -> ShotResult:
    cfg = settings or load_settings()
    monitors = list_monitors()
    index = cfg.monitor_index if monitor_index is None else monitor_index
    if index < 0 or index >= len(monitors):
        index = 0
    image = _grab(monitors[index])
    path = _save(image, "tela", cfg)
    return ShotResult(path, image.width, image.height, index)


def shot_region(left: int, top: int, width: int, height: int, settings: Settings | None = None) -> ShotResult:
    if width < 2 or height < 2:
        raise ValueError("Região pequena demais.")
    cfg = settings or load_settings()
    region = {"left": left, "top": top, "width": width, "height": height}
    image = _grab(region)
    path = _save(image, "recorte", cfg)
    return ShotResult(path, image.width, image.height, -1)


def shot_from_image(
    image: Image.Image,
    prefix: str = "recorte",
    settings: Settings | None = None,
    folder: Path | None = None,
) -> ShotResult:
    cfg = settings or load_settings()
    path = _save(image.convert("RGB"), prefix, cfg, folder=folder)
    return ShotResult(path, image.width, image.height, -1)
