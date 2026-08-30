from __future__ import annotations

import os
from datetime import datetime
from pathlib import Path


APP_DIR_NAME = "CORTE"
IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".webp", ".bmp"}
VIDEO_SUFFIXES = {".mp4", ".webm", ".avi", ".mkv"}


def pictures_root() -> Path:
    home = Path.home()
    candidates = [
        Path(os.environ.get("USERPROFILE", "")) / "Pictures" / APP_DIR_NAME,
        home / "Pictures" / APP_DIR_NAME,
        home / "Imagens" / APP_DIR_NAME,
        home / APP_DIR_NAME,
    ]
    for path in candidates:
        if path.parent.exists() or path.parent == home:
            path.mkdir(parents=True, exist_ok=True)
            return path
    fallback = home / APP_DIR_NAME
    fallback.mkdir(parents=True, exist_ok=True)
    return fallback


def stamp(prefix: str, ext: str, folder: Path | None = None) -> Path:
    now = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    root = folder or pictures_root()
    root.mkdir(parents=True, exist_ok=True)
    return root / f"{prefix}_{now}.{ext.lstrip('.')}"


def last_image(folder: Path | None = None) -> Path | None:
    folder = folder or pictures_root()
    files = sorted(
        [p for p in folder.glob("*") if p.suffix.lower() in IMAGE_SUFFIXES],
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    return files[0] if files else None


def last_capture(folder: Path | None = None) -> Path | None:
    folder = folder or pictures_root()
    files = sorted(
        [
            p
            for p in folder.glob("*")
            if p.suffix.lower() in IMAGE_SUFFIXES | VIDEO_SUFFIXES
        ],
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    return files[0] if files else None


def list_captures(folder: Path | None = None, limit: int = 24) -> list[Path]:
    folder = folder or pictures_root()
    files = sorted(
        [
            p
            for p in folder.glob("*")
            if p.suffix.lower() in IMAGE_SUFFIXES | VIDEO_SUFFIXES
        ],
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    return files[:limit]
