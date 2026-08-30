from __future__ import annotations

from corte.cli import main


def test_tutorial_exits_zero() -> None:
    assert main(["tutorial"]) == 0


def test_version_does_not_crash() -> None:
    try:
        main(["--version"])
    except SystemExit as exc:
        assert exc.code == 0
