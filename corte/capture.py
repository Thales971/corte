from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import mss
from PIL import Image

from corte.paths import stamp


@dataclass
class ShotResult:
    path: Path
    width: int
    height: int
    monitor: int


def _grab(monitor: dict) -> Image.Image:
    with mss.mss() as sct:
        raw = sct.grab(monitor)
        return Image.frombytes("RGB", raw.size, raw.bgra, "raw", "BGRX")


def list_monitors() -> list[dict]:
    with mss.mss() as sct:
        return list(sct.monitors)


def shot_full(monitor_index: int = 0) -> ShotResult:
    monitors = list_monitors()
    if monitor_index < 0 or monitor_index >= len(monitors):
        monitor_index = 0
    image = _grab(monitors[monitor_index])
    path = stamp("tela", "png")
    image.save(path, "PNG")
    return ShotResult(path, image.width, image.height, monitor_index)


def shot_region(left: int, top: int, width: int, height: int) -> ShotResult:
    if width < 2 or height < 2:
        raise ValueError("Região pequena demais.")
    region = {"left": left, "top": top, "width": width, "height": height}
    image = _grab(region)
    path = stamp("recorte", "png")
    image.save(path, "PNG")
    return ShotResult(path, image.width, image.height, -1)


def shot_from_image(image: Image.Image) -> ShotResult:
    path = stamp("recorte", "png")
    image.save(path, "PNG")
    return ShotResult(path, image.width, image.height, -1)
