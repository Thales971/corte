from __future__ import annotations

import argparse
import sys
from pathlib import Path

from corte import __app_name__, __version__
from corte.capture import shot_full
from corte.ocr import OcrError, extract_text
from corte.paths import last_image, list_captures, pictures_root
from corte.record import ScreenRecorder
from corte.settings import load_settings


def _print(msg: str) -> None:
    sys.stdout.write(msg + "\n")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="corte",
        description="CORTE V2 — print, recorte, editor, gravação e OCR.",
    )
    parser.add_argument("-v", "--version", action="version", version=f"{__app_name__} {__version__}")
    sub = parser.add_subparsers(dest="cmd")

    sub.add_parser("ui", help="abre o painel visual (padrão)")
    shot = sub.add_parser("shot", help="print da tela inteira")
    shot.add_argument("--delay", type=int, default=None)
    shot.add_argument("--monitor", type=int, default=None)
    sub.add_parser("region", help="recorte com overlay V2")
    rec = sub.add_parser("record", help="grava a tela até ENTER")
    rec.add_argument("--fps", type=int, default=None)
    rec.add_argument("--seconds", type=float, default=0, help="duração; 0 = até ENTER")
    ocr = sub.add_parser("ocr", help="extrai texto de uma imagem")
    ocr.add_argument("arquivo", nargs="?", help="caminho; se vazio usa a última captura")
    edit = sub.add_parser("edit", help="abre o editor de anotações")
    edit.add_argument("arquivo", nargs="?", help="caminho; se vazio usa a última captura")
    sub.add_parser("pasta", help="mostra a pasta de saídas")
    sub.add_parser("historico", help="lista as últimas capturas")
    sub.add_parser("tutorial", help="imprime o guia rápido")

    args = parser.parse_args(argv)
    cmd = args.cmd or "ui"
    settings = load_settings()

    if cmd == "ui":
        from corte.app import run

        run()
        return 0

    if cmd == "shot":
        import time

        delay = settings.delay_seconds if args.delay is None else max(0, args.delay)
        monitor = settings.monitor_index if args.monitor is None else args.monitor
        if delay:
            _print(f"print em {delay}s…")
            time.sleep(delay)
        try:
            result = shot_full(monitor, settings)
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

        fps = settings.fps if args.fps is None else args.fps
        recorder = ScreenRecorder(monitor_index=settings.monitor_index, fps=fps)
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
            _print(extract_text(target, lang=settings.ocr_lang))
        except OcrError as exc:
            _print(str(exc))
            return 1
        return 0

    if cmd == "edit":
        from corte.editor import run_editor

        target = Path(args.arquivo) if args.arquivo else last_image()
        if target is None:
            _print("nenhuma imagem encontrada.")
            return 1
        saved = run_editor(target)
        if not saved:
            return 1
        _print(saved)
        return 0

    if cmd == "pasta":
        _print(str(pictures_root()))
        return 0

    if cmd == "historico":
        files = list_captures(limit=20)
        if not files:
            _print("histórico vazio.")
            return 0
        for item in files:
            _print(str(item))
        return 0

    if cmd == "tutorial":
        from corte.tutorial import TUTORIAL

        _print(TUTORIAL.strip())
        return 0

    parser.print_help()
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
