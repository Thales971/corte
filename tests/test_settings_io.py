from __future__ import annotations

from pathlib import Path

from corte import settings as settings_mod
from corte.settings import Settings, load_settings, save_settings


def test_roundtrip(monkeypatch, tmp_path: Path) -> None:
    target = tmp_path / "corte.settings.json"
    monkeypatch.setattr(settings_mod, "settings_path", lambda: target)
    original = Settings(delay_seconds=5, fps=20, image_format="webp").clamp()
    path = save_settings(original)
    assert path == target
    assert path.exists()
    loaded = load_settings()
    assert loaded.delay_seconds == 5
    assert loaded.fps == 20
    assert loaded.image_format == "webp"
