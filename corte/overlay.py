from __future__ import annotations

import sys
from dataclasses import dataclass

from PIL import Image, ImageDraw

from corte.capture import shot_from_image


@dataclass
class Region:
    left: int
    top: int
    width: int
    height: int


def select_region() -> Region | None:
    """Fullscreen overlay: drag to crop. Esc cancels. Returns virtual-screen coords."""
    import tkinter as tk

    import mss
    from PIL import ImageTk

    with mss.mss() as sct:
        virtual = sct.monitors[0]
        raw = sct.grab(virtual)
        background = Image.frombytes("RGB", raw.size, raw.bgra, "raw", "BGRX")

    dimmed = background.point(lambda p: int(p * 0.42))

    root = tk.Tk()
    root.title("CORTE — recorte")
    root.attributes("-topmost", True)
    root.configure(cursor="crosshair", bg="black")
    root.overrideredirect(True)
    root.geometry(f"{virtual['width']}x{virtual['height']}+{virtual['left']}+{virtual['top']}")
    try:
        root.attributes("-fullscreen", True)
    except tk.TclError:
        pass

    canvas = tk.Canvas(
        root,
        width=virtual["width"],
        height=virtual["height"],
        highlightthickness=0,
        bg="black",
        cursor="crosshair",
    )
    canvas.pack(fill="both", expand=True)

    photo = ImageTk.PhotoImage(dimmed)
    canvas.create_image(0, 0, image=photo, anchor="nw")
    canvas.image = photo

    hint = canvas.create_text(
        virtual["width"] // 2,
        36,
        text="Arraste para recortar   ·   ENTER confirma   ·   ESC cancela",
        fill="#7CFFB2",
        font=("Segoe UI", 16, "bold"),
    )

    state: dict = {"x0": 0, "y0": 0, "rect": None, "preview": None, "done": None}

    def canvas_to_screen(x: int, y: int) -> tuple[int, int]:
        return virtual["left"] + x, virtual["top"] + y

    def on_press(event: tk.Event) -> None:
        state["x0"], state["y0"] = event.x, event.y
        if state["rect"]:
            canvas.delete(state["rect"])
        state["rect"] = canvas.create_rectangle(
            event.x, event.y, event.x, event.y, outline="#7CFFB2", width=2
        )

    def on_drag(event: tk.Event) -> None:
        if not state["rect"]:
            return
        canvas.coords(state["rect"], state["x0"], state["y0"], event.x, event.y)
        x1, y1 = min(state["x0"], event.x), min(state["y0"], event.y)
        x2, y2 = max(state["x0"], event.x), max(state["y0"], event.y)
        if x2 - x1 < 4 or y2 - y1 < 4:
            return
        crop = background.crop((x1, y1, x2, y2))
        if crop.width > 1 and crop.height > 1:
            framed = crop.copy()
            draw = ImageDraw.Draw(framed)
            draw.rectangle((0, 0, framed.width - 1, framed.height - 1), outline="#7CFFB2")
            preview = ImageTk.PhotoImage(framed)
            if state["preview"]:
                canvas.delete(state["preview"])
            state["tk_preview"] = preview
            state["preview"] = canvas.create_image(x1, y1, image=preview, anchor="nw")
            canvas.tag_raise(state["rect"])
            canvas.tag_raise(hint)

    def finish(ok: bool) -> None:
        if not ok or not state["rect"]:
            state["done"] = None
            root.destroy()
            return
        x1, y1, x2, y2 = canvas.coords(state["rect"])
        left, top = canvas_to_screen(int(min(x1, x2)), int(min(y1, y2)))
        width = abs(int(x2 - x1))
        height = abs(int(y2 - y1))
        state["done"] = Region(left, top, width, height) if width >= 2 and height >= 2 else None
        root.destroy()

    root.bind("<ButtonPress-1>", on_press)
    root.bind("<B1-Motion>", on_drag)
    root.bind("<ButtonRelease-1>", lambda _e: None)
    root.bind("<Return>", lambda _e: finish(True))
    root.bind("<Escape>", lambda _e: finish(False))
    canvas.bind("<ButtonPress-1>", on_press)
    canvas.bind("<B1-Motion>", on_drag)

    root.focus_force()
    root.mainloop()
    return state["done"]


def run_overlay_and_save() -> str:
    region = select_region()
    if region is None:
        return ""
    import mss
    from PIL import Image

    mon = {
        "left": region.left,
        "top": region.top,
        "width": region.width,
        "height": region.height,
    }
    with mss.mss() as sct:
        raw = sct.grab(mon)
        image = Image.frombytes("RGB", raw.size, raw.bgra, "raw", "BGRX")
    result = shot_from_image(image)
    return str(result.path)


def main() -> int:
    path = run_overlay_and_save()
    if path:
        sys.stdout.write(path + "\n")
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
