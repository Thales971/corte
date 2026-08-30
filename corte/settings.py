from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path

from corte.paths import pictures_root


@dataclass
class Settings:
    delay_seconds: int = 0
    monitor_index: int = 0
    fps: int = 24
    image_format: str = "png"
    jpeg_quality: int = 92
    copy_image: bool = True
    copy_path: bool = True
    open_editor_after_shot: bool = True
    frame_padding: int = 48
    frame_radius: int = 18
    frame_shadow: int = 28
    frame_background: str = "#0B0F0C"
    apply_frame_on_save: bool = False
    ocr_lang: str = "por+eng"
    magnifier: bool = True

    def clamp(self) -> Settings:
        self.delay_seconds = max(0, min(int(self.delay_seconds), 15))
        self.monitor_index = max(0, int(self.monitor_index))
        self.fps = max(8, min(int(self.fps), 30))
        fmt = self.image_format.lower().strip()
        self.image_format = fmt if fmt in {"png", "jpeg", "jpg", "webp"} else "png"
        if self.image_format == "jpg":
            self.image_format = "jpeg"
        self.jpeg_quality = max(40, min(int(self.jpeg_quality), 100))
        self.frame_padding = max(0, min(int(self.frame_padding), 160))
        self.frame_radius = max(0, min(int(self.frame_radius), 64))
        self.frame_shadow = max(0, min(int(self.frame_shadow), 80))
        return self


def settings_path() -> Path:
    return pictures_root() / "corte.settings.json"


def load_settings() -> Settings:
    path = settings_path()
    if not path.exists():
        return Settings().clamp()
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
        data = {k: v for k, v in raw.items() if k in Settings.__dataclass_fields__}
        return Settings(**data).clamp()
    except (OSError, json.JSONDecodeError, TypeError, ValueError):
        return Settings().clamp()


def save_settings(settings: Settings) -> Path:
    path = settings_path()
    path.write_text(
        json.dumps(asdict(settings.clamp()), indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return path
