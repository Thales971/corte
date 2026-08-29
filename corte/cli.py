from __future__ import annotations

import argparse
import sys
from pathlib import Path

from corte import __app_name__, __version__
from corte.capture import shot_full
from corte.ocr import OcrError, extract_text
from corte.paths import last_image, pictures_root
from corte.record import ScreenRecorder


def _print(msg: str) -> None:
    sys.stdout.write(msg + "\n")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="corte",
        description="Print, recorte, gravação e OCR pelo terminal.",
    )
    parser.add_argument("-v", "--version", action="version", version=f"{__app_name__} {__version__}")
    sub = parser.add_subparsers(dest="cmd")

    sub.add_parser("ui", help="abre o painel visual (padrão)")
    sub.add_parser("shot", help="print da tela inteira")
    sub.add_parser("region", help="recorte com overlay")
    rec = sub.add_parser("record", help="grava a tela até ENTER")
    rec.add_argument("--fps", type=int, default=20)
    rec.add_argument("--seconds", type=float, default=0, help="duração; 0 = até ENTER")
    ocr = sub.add_parser("ocr", help="extrai texto de uma imagem")
    ocr.add_argument("arquivo", nargs="?", help="caminho; se vazio usa a última captura")
    sub.add_parser("pasta", help="mostra a pasta de saídas")

    args = parser.parse_args(argv)
    cmd = args.cmd or "ui"

    if cmd == "ui":
        from corte.app import run

        run()
        return 0

    if cmd == "shot":
        try:
            result = shot_full(0)
        except Exception as exc:
            _print(f"nao foi possivel capturar a tela: {exc}")
            return 1
        _print(str(result.path))
        return 0

    if cmd == "region":
        from corte.overlay import run_overlay_and_save

        path = run_overlay_and_save()
        if not path:
            return 1
        _print(path)
        return 0

    if cmd == "record":
        import time

        recorder = ScreenRecorder(fps=args.fps)
        path = recorder.start()
        _print(f"gravando {path}")
        try:
            if args.seconds > 0:
                time.sleep(args.seconds)
            else:
                input("ENTER para parar… ")
        except KeyboardInterrupt:
            pass
        status = recorder.stop()
        _print(f"salvo {status.frames} frames em {status.elapsed:.1f}s → {status.path}")
        return 0

    if cmd == "ocr":
        target = Path(args.arquivo) if args.arquivo else last_image()
        if target is None:
            _print("nenhuma imagem encontrada.")
            return 1
        try:
            _print(extract_text(target))
        except OcrError as exc:
            _print(str(exc))
            return 1
        return 0

    if cmd == "pasta":
        _print(str(pictures_root()))
        return 0

    parser.print_help()
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
