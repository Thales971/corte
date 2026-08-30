from __future__ import annotations

import time
from pathlib import Path

from corte.paths import IMAGE_SUFFIXES, last_image, list_captures, stamp


def test_stamp_creates_expected_name(tmp_path: Path) -> None:
    path = stamp("tela", "png", folder=tmp_path)
    assert path.parent == tmp_path
    assert path.name.startswith("tela_")
    assert path.suffix == ".png"


def test_last_image_picks_newest(tmp_path: Path) -> None:
    older = tmp_path / "tela_old.png"
    newer = tmp_path / "recorte_new.png"
    older.write_bytes(b"x")
    time.sleep(0.05)
    newer.write_bytes(b"y")
    assert last_image(tmp_path) == newer


def test_list_captures_ignores_other_files(tmp_path: Path) -> None:
    (tmp_path / "nota.txt").write_text("nao")
    shot = tmp_path / "tela_1.png"
    shot.write_bytes(b"png")
    found = list_captures(tmp_path)
    assert found == [shot]
    assert ".png" in IMAGE_SUFFIXES
