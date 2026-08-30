from __future__ import annotations

import sys
from pathlib import Path

from corte.editor import run_editor


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    if not args:
        sys.stderr.write("uso: python -m corte.editor_main arquivo.png\n")
        return 2
    path = Path(args[0])
    if not path.exists():
        sys.stderr.write(f"arquivo não encontrado: {path}\n")
        return 1
    saved = run_editor(path)
    if saved:
        sys.stdout.write(saved + "\n")
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
