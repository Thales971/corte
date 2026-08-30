from __future__ import annotations

import math
from dataclasses import dataclass

from PIL import Image, ImageDraw, ImageFont

from corte.beautify import apply_frame, blur_region, pixelate
from corte.theme import MINT, WHITE


def font(size: int) -> ImageFont.ImageFont:
    for name in ("segoeui.ttf", "Segoe UI", "arial.ttf", "DejaVuSans.ttf"):
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    return ImageFont.load_default()


def hex_rgb(value: str) -> tuple[int, int, int]:
    raw = value.lstrip("#")
    if len(raw) == 3:
        raw = "".join(ch * 2 for ch in raw)
    if len(raw) != 6:
        return (124, 255, 178)
    return int(raw[0:2], 16), int(raw[2:4], 16), int(raw[4:6], 16)


def draw_arrow(image, start, end, color=MINT, width=4):
    out = image.copy()
    draw = ImageDraw.Draw(out)
    draw.line((start, end), fill=color, width=width)
    angle = math.atan2(end[1] - start[1], end[0] - start[0])
    head = max(12, width * 4)
    p1 = (end[0] - head * math.cos(angle - math.pi / 6), end[1] - head * math.sin(angle - math.pi / 6))
    p2 = (end[0] - head * math.cos(angle + math.pi / 6), end[1] - head * math.sin(angle + math.pi / 6))
    draw.polygon([end, p1, p2], fill=color)
    return out


def draw_shape(image, tool, start, end, color=MINT, width=4):
    out = image.copy()
    draw = ImageDraw.Draw(out)
    box = (*start, *end)
    if tool == "retangulo":
        draw.rectangle(box, outline=color, width=width)
    elif tool == "elipse":
        draw.ellipse(box, outline=color, width=width)
    elif tool == "linha":
        draw.line((start, end), fill=color, width=width)
    else:
        raise ValueError(f"forma desconhecida: {tool}")
    return out


def draw_highlight(image, start, end, color="#C8F54A", alpha=70):
    overlay = Image.new("RGBA", image.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    draw.rectangle((*start, *end), fill=(*hex_rgb(color), max(20, min(alpha, 160))))
    return Image.alpha_composite(image.convert("RGBA"), overlay).convert("RGB")


def draw_text(image, xy, text, color=MINT, size=22):
    out = image.copy()
    ImageDraw.Draw(out).text(xy, text, fill=color, font=font(size))
    return out


def draw_number(image, xy, number, color=MINT, radius=16):
    out = image.copy()
    draw = ImageDraw.Draw(out)
    x, y = xy
    draw.ellipse((x - radius, y - radius, x + radius, y + radius), fill=color, outline=WHITE, width=2)
    draw.text((x - 6, y - 10), str(number), fill="#0B0F0C", font=font(18))
    return out


def draw_pen(image, points, color=MINT, width=4):
    if len(points) < 2:
        return image.copy()
    out = image.copy()
    ImageDraw.Draw(out).line(points, fill=color, width=max(2, width), joint="curve")
    return out


def crop_box(image, start, end):
    x1, x2 = sorted((int(start[0]), int(end[0])))
    y1, y2 = sorted((int(start[1]), int(end[1])))
    return image.crop((x1, y1, max(x1 + 1, x2), max(y1 + 1, y2)))


@dataclass
class Stroke:
    tool: str
    start: tuple[int, int]
    end: tuple[int, int]
    color: str = MINT
    width: int = 4
    text: str = ""
    number: int = 1
    points: tuple[tuple[int, int], ...] = ()


def apply_stroke(image, stroke: Stroke):
    tool = stroke.tool
    if tool == "seta":
        return draw_arrow(image, stroke.start, stroke.end, stroke.color, stroke.width)
    if tool in {"retangulo", "elipse", "linha"}:
        return draw_shape(image, tool, stroke.start, stroke.end, stroke.color, stroke.width)
    if tool == "marca":
        return draw_highlight(image, stroke.start, stroke.end, stroke.color)
    if tool == "texto":
        return draw_text(image, stroke.start, stroke.text or " ", stroke.color, max(18, stroke.width * 6))
    if tool == "blur":
        return blur_region(image, (*stroke.start, *stroke.end), radius=14)
    if tool == "pixel":
        return pixelate(image, (*stroke.start, *stroke.end), block=14)
    if tool == "numero":
        return draw_number(image, stroke.start, stroke.number, stroke.color, max(14, stroke.width * 5))
    if tool == "cortar":
        return crop_box(image, stroke.start, stroke.end)
    if tool == "caneta":
        return draw_pen(image, list(stroke.points or (stroke.start, stroke.end)), stroke.color, stroke.width)
    if tool == "moldura":
        return apply_frame(image)
    raise ValueError(f"ferramenta desconhecida: {tool}")
