from __future__ import annotations

import sys
from pathlib import Path

from PIL import Image

try:
    import pyperclip
except ImportError:
    pyperclip = None


def copy_text(text: str) -> bool:
    if not pyperclip:
        return False
    try:
        pyperclip.copy(text)
        return True
    except Exception:
        return False


def copy_image(image: Image.Image) -> bool:
    if sys.platform.startswith("win"):
        return _copy_image_windows(image)
    if sys.platform == "darwin":
        return _copy_image_macos(image)
    return _copy_image_linux(image)


def copy_image_path(path: Path) -> bool:
    try:
        with Image.open(path) as img:
            return copy_image(img.convert("RGB"))
    except Exception:
        return False


def _copy_image_windows(image: Image.Image) -> bool:
    import ctypes
    import io

    CF_DIB = 8
    GMEM_MOVEABLE = 0x0002

    output = io.BytesIO()
    image.convert("RGB").save(output, "BMP")
    data = output.getvalue()[14:]

    kernel32 = ctypes.windll.kernel32
    user32 = ctypes.windll.user32

    if not user32.OpenClipboard(None):
        return False
    try:
        user32.EmptyClipboard()
        handle = kernel32.GlobalAlloc(GMEM_MOVEABLE, len(data))
        if not handle:
            return False
        locked = kernel32.GlobalLock(handle)
        ctypes.memmove(locked, data, len(data))
        kernel32.GlobalUnlock(handle)
        user32.SetClipboardData(CF_DIB, handle)
        return True
    except Exception:
        return False
    finally:
        user32.CloseClipboard()


def _copy_image_macos(image: Image.Image) -> bool:
    import subprocess
    import tempfile

    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
        path = Path(tmp.name)
    try:
        image.save(path, "PNG")
        script = (
            'set the clipboard to (read (POSIX file "'
            + str(path)
            + '") as «class PNGf»)'
        )
        completed = subprocess.run(
            ["osascript", "-e", script],
            check=False,
            capture_output=True,
            text=True,
        )
        return completed.returncode == 0
    except Exception:
        return False
    finally:
        path.unlink(missing_ok=True)


def _copy_image_linux(image: Image.Image) -> bool:
    import subprocess
    import tempfile

    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
        path = Path(tmp.name)
    try:
        image.save(path, "PNG")
        for cmd in (
            ["wl-copy", "--type", "image/png"],
            ["xclip", "-selection", "clipboard", "-t", "image/png"],
        ):
            try:
                with path.open("rb") as fh:
                    completed = subprocess.run(cmd, check=False, stdin=fh, capture_output=True)
                if completed.returncode == 0:
                    return True
            except FileNotFoundError:
                continue
        return False
    except Exception:
        return False
    finally:
        path.unlink(missing_ok=True)
