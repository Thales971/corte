from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from textual import on, work
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.widgets import Button, Footer, Header, RichLog, Static

from corte import __version__
from corte.capture import shot_full
from corte.ocr import OcrError, extract_text
from corte.paths import last_image, pictures_root
from corte.record import ScreenRecorder

try:
    import pyperclip
except ImportError:
    pyperclip = None


BANNER = r"""
 ██████╗ ██████╗ ██████╗ ████████╗███████╗
██╔════╝██╔═══██╗██╔══██╗╚══██╔══╝██╔════╝
██║     ██║   ██║██████╔╝   ██║   █████╗
██║     ██║   ██║██╔══██╗   ██║   ██╔══╝
╚██████╗╚██████╔╝██║  ██║   ██║   ███████╗
 ╚═════╝ ╚═════╝ ╚═╝  ╚═╝   ╚═╝   ╚══════╝
"""


class StatusPanel(Static):
    def show_idle(self, folder: Path) -> None:
        self.update(
            f"[bold #7CFFB2]CORTE[/]  [dim]v{__version__}[/]\n"
            f"[dim]pasta[/]  {folder}\n"
            f"[dim]status[/] pronto · F tela  R região  G gravar  O ocr  P pasta"
        )

    def show_shot(self, path: Path, width: int, height: int) -> None:
        size_kb = path.stat().st_size / 1024
        self.update(
            f"[bold #7CFFB2]captura ok[/]\n"
            f"[dim]arquivo[/]  {path.name}\n"
            f"[dim]tamanho[/]  {width}×{height}  ·  {size_kb:.0f} KB\n"
            f"[dim]caminho[/]  {path}"
        )

    def show_record(self, frames: int, elapsed: float, path: Path | None) -> None:
        name = path.name if path else "—"
        self.update(
            f"[bold #FF6B6B]● GRAVANDO[/]  {elapsed:05.1f}s  ·  {frames} frames\n"
            f"[dim]arquivo[/]  {name}\n"
            f"[dim]atalho[/]   G ou ESC para parar"
        )

    def show_ocr(self, preview: str) -> None:
        snippet = preview.replace("\n", " ")[:180]
        self.update(f"[bold #7CFFB2]OCR[/]\n{snippet}")


class CorteApp(App[None]):
    TITLE = "CORTE"
    SUB_TITLE = "print · recorte · gravação · ocr"
    CSS = """
    Screen {
        background: #0B0F0C;
    }
    Header {
        background: #102216;
        color: #7CFFB2;
        text-style: bold;
    }
    Footer {
        background: #102216;
        color: #9BE7C4;
    }
    #layout {
        height: 1fr;
        padding: 1 2;
    }
    #banner {
        color: #7CFFB2;
        height: auto;
        text-style: bold;
        padding-bottom: 1;
    }
    #status {
        height: 6;
        border: heavy #1F6A43;
        padding: 1 2;
        background: #0E1712;
        color: #D7FFE8;
    }
    #actions {
        height: auto;
        padding: 1 0;
    }
    Button {
        margin-right: 1;
        min-width: 16;
    }
    Button.-primary {
        background: #1F6A43;
        color: #E8FFF2;
    }
    Button.record-on {
        background: #7A1F1F;
        color: #FFE8E8;
    }
    #log {
        height: 1fr;
        border: heavy #1F6A43;
        background: #070A08;
        color: #C9F5DC;
        padding: 0 1;
    }
    """

    BINDINGS = [
        Binding("f", "full", "Tela cheia"),
        Binding("r", "region", "Região"),
        Binding("g", "toggle_record", "Gravar"),
        Binding("o", "ocr", "OCR"),
        Binding("p", "open_folder", "Pasta"),
        Binding("c", "copy_last", "Copiar path"),
        Binding("q", "quit", "Sair"),
        Binding("escape", "escape", "Parar/Sair", show=False),
    ]

    def __init__(self) -> None:
        super().__init__()
        self.folder = pictures_root()
        self.last_path: Path | None = last_image(self.folder)
        self.recorder = ScreenRecorder(monitor_index=0, fps=20)

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Vertical(id="layout"):
            yield Static(BANNER, id="banner")
            yield StatusPanel(id="status")
            with Horizontal(id="actions"):
                yield Button("Tela cheia  F", id="btn-full", variant="primary")
                yield Button("Região  R", id="btn-region", variant="primary")
                yield Button("Gravar  G", id="btn-record")
                yield Button("OCR  O", id="btn-ocr")
                yield Button("Pasta  P", id="btn-folder")
            yield RichLog(id="log", highlight=True, markup=True)
        yield Footer()

    def on_mount(self) -> None:
        self.query_one("#status", StatusPanel).show_idle(self.folder)
        log = self.query_one("#log", RichLog)
        log.write("[#7CFFB2]CORTE no ar.[/] Prints vão para a pasta Pictures/CORTE.")
        if self.last_path:
            log.write(f"[dim]última imagem:[/] {self.last_path.name}")
        self.set_interval(0.4, self._tick_recorder)

    def log_ok(self, message: str) -> None:
        self.query_one("#log", RichLog).write(f"[#7CFFB2]✓[/] {message}")

    def log_err(self, message: str) -> None:
        self.query_one("#log", RichLog).write(f"[#FF6B6B]✗[/] {message}")

    def log_info(self, message: str) -> None:
        self.query_one("#log", RichLog).write(f"[dim]·[/] {message}")

    @on(Button.Pressed, "#btn-full")
    def _click_full(self) -> None:
        self.action_full()

    @on(Button.Pressed, "#btn-region")
    def _click_region(self) -> None:
        self.action_region()

    @on(Button.Pressed, "#btn-record")
    def _click_record(self) -> None:
        self.action_toggle_record()

    @on(Button.Pressed, "#btn-ocr")
    def _click_ocr(self) -> None:
        self.action_ocr()

    @on(Button.Pressed, "#btn-folder")
    def _click_folder(self) -> None:
        self.action_open_folder()

    def action_full(self) -> None:
        if self.recorder.snapshot().running:
            self.log_err("Pare a gravação antes de tirar print.")
            return
        try:
            result = shot_full(0)
        except Exception as exc:
            self.log_err(f"falha no print: {exc}")
            return
        self.last_path = result.path
        self.query_one("#status", StatusPanel).show_shot(result.path, result.width, result.height)
        self.log_ok(f"tela cheia → {result.path}")
        self._copy(str(result.path))

    @work(thread=True)
    def action_region(self) -> None:
        if self.recorder.snapshot().running:
            self.call_from_thread(self.log_err, "Pare a gravação antes de recortar.")
            return
        self.call_from_thread(self.log_info, "abrindo overlay de recorte…")
        cmd = [sys.executable, "-m", "corte.overlay"]
        try:
            completed = subprocess.run(cmd, check=False, capture_output=True, text=True)
        except Exception as exc:
            self.call_from_thread(self.log_err, f"overlay falhou: {exc}")
            return
        path_text = (completed.stdout or "").strip()
        if completed.returncode != 0 or not path_text:
            self.call_from_thread(self.log_info, "recorte cancelado.")
            return
        path = Path(path_text)
        self.last_path = path
        try:
            from PIL import Image

            with Image.open(path) as img:
                width, height = img.size
        except Exception:
            width, height = 0, 0
        self.call_from_thread(self._after_region, path, width, height)

    def _after_region(self, path: Path, width: int, height: int) -> None:
        self.query_one("#status", StatusPanel).show_shot(path, width, height)
        self.log_ok(f"recorte → {path}")
        self._copy(str(path))

    def action_toggle_record(self) -> None:
        if self.recorder.snapshot().running:
            status = self.recorder.stop()
            self.query_one("#btn-record", Button).label = "Gravar  G"
            self.query_one("#btn-record", Button).remove_class("record-on")
            if status.path:
                self.last_path = status.path
                self.log_ok(
                    f"vídeo salvo ({status.elapsed:.1f}s, {status.frames} frames) → {status.path}"
                )
            self.query_one("#status", StatusPanel).show_idle(self.folder)
            return
        try:
            path = self.recorder.start()
        except Exception as exc:
            self.log_err(str(exc))
            return
        self.query_one("#btn-record", Button).label = "Parar  G"
        self.query_one("#btn-record", Button).add_class("record-on")
        self.log_info(f"gravando → {path}")

    def _tick_recorder(self) -> None:
        status = self.recorder.snapshot()
        if status.running and status.path:
            self.query_one("#status", StatusPanel).show_record(
                status.frames, status.elapsed, status.path
            )

    def action_ocr(self) -> None:
        target = self.last_path or last_image(self.folder)
        if target is None or not target.exists():
            self.log_err("nenhuma imagem para ler. Tire um print primeiro.")
            return
        if target.suffix.lower() not in {".png", ".jpg", ".jpeg", ".webp", ".bmp"}:
            self.log_err("OCR só funciona em imagem, não em vídeo.")
            return
        try:
            text = extract_text(target)
        except OcrError as exc:
            self.log_err(str(exc))
            return
        self.query_one("#status", StatusPanel).show_ocr(text)
        self.query_one("#log", RichLog).write(f"[#7CFFB2]OCR {target.name}[/]\n{text}")
        self._copy(text)

    def action_open_folder(self) -> None:
        folder = self.folder
        folder.mkdir(parents=True, exist_ok=True)
        try:
            if sys.platform.startswith("win"):
                subprocess.Popen(["explorer", str(folder)])
            elif sys.platform == "darwin":
                subprocess.Popen(["open", str(folder)])
            else:
                subprocess.Popen(["xdg-open", str(folder)])
            self.log_ok(f"pasta aberta: {folder}")
        except Exception as exc:
            self.log_err(f"não abriu a pasta: {exc}")

    def action_copy_last(self) -> None:
        if not self.last_path:
            self.log_err("nada para copiar ainda.")
            return
        self._copy(str(self.last_path))

    def action_escape(self) -> None:
        if self.recorder.snapshot().running:
            self.action_toggle_record()
            return
        self.exit()

    def action_quit(self) -> None:
        if self.recorder.snapshot().running:
            self.recorder.stop()
        self.exit()

    def _copy(self, text: str) -> None:
        if not pyperclip:
            return
        try:
            pyperclip.copy(text)
            self.log_info("copiado para a área de transferência")
        except Exception:
            pass


def run() -> None:
    CorteApp().run()
