from __future__ import annotations

from PIL import Image, ImageDraw, ImageFilter


def _hex_to_rgb(value: str, fallback: tuple[int, int, int] = (11, 15, 12)) -> tuple[int, int, int]:
    raw = value.strip().lstrip("#")
    if len(raw) == 3:
        raw = "".join(ch * 2 for ch in raw)
    if len(raw) != 6:
        return fallback
    try:
        return int(raw[0:2], 16), int(raw[2:4], 16), int(raw[4:6], 16)
    except ValueError:
        return fallback


def _round_mask(size: tuple[int, int], radius: int) -> Image.Image:
    mask = Image.new("L", size, 0)
    draw = ImageDraw.Draw(mask)
    draw.rounded_rectangle((0, 0, size[0] - 1, size[1] - 1), radius=max(0, radius), fill=255)
    return mask


def apply_frame(
    image: Image.Image,
    padding: int = 48,
    radius: int = 18,
    shadow: int = 28,
    background: str = "#0B0F0C",
) -> Image.Image:
    """Moldura estilo CleanShot: fundo, cantos, sombra suave."""
    src = image.convert("RGBA")
    pad = max(0, int(padding))
    rad = max(0, min(int(radius), min(src.size) // 2))
    sh = max(0, int(shadow))

    if pad == 0 and rad == 0 and sh == 0:
        return src.convert("RGB")

    if rad:
        rounded = Image.new("RGBA", src.size, (0, 0, 0, 0))
        rounded.paste(src, (0, 0))
        rounded.putalpha(_round_mask(src.size, rad))
        src = rounded

    shadow_blur = max(1, sh // 2) if sh else 0
    extra = sh + shadow_blur
    canvas_w = src.width + pad * 2 + extra * 2
    canvas_h = src.height + pad * 2 + extra * 2
    bg = (*_hex_to_rgb(background), 255)
    canvas = Image.new("RGBA", (canvas_w, canvas_h), bg)

    if sh:
        shadow_layer = Image.new("RGBA", (canvas_w, canvas_h), (0, 0, 0, 0))
        blob = Image.new("RGBA", src.size, (0, 0, 0, 0))
        blob.paste((0, 0, 0, 140), (0, 0), src.split()[-1] if src.mode == "RGBA" else None)
        ox = pad + extra + max(2, sh // 8)
        oy = pad + extra + max(4, sh // 5)
        shadow_layer.paste(blob, (ox, oy), blob)
        shadow_layer = shadow_layer.filter(ImageFilter.GaussianBlur(radius=max(4, sh // 2)))
        canvas = Image.alpha_composite(canvas, shadow_layer)

    canvas.paste(src, (pad + extra, pad + extra), src)
    return canvas.convert("RGB")


def pixelate(image: Image.Image, box: tuple[int, int, int, int], block: int = 12) -> Image.Image:
    x1, y1, x2, y2 = _norm_box(box, image.size)
    region = image.crop((x1, y1, x2, y2))
    if region.width < 2 or region.height < 2:
        return image
    small_w = max(1, region.width // max(2, block))
    small_h = max(1, region.height // max(2, block))
    tiny = region.resize((small_w, small_h), Image.Resampling.NEAREST)
    big = tiny.resize(region.size, Image.Resampling.NEAREST)
    out = image.copy()
    out.paste(big, (x1, y1))
    return out


def blur_region(image: Image.Image, box: tuple[int, int, int, int], radius: int = 12) -> Image.Image:
    x1, y1, x2, y2 = _norm_box(box, image.size)
    region = image.crop((x1, y1, x2, y2))
    if region.width < 2 or region.height < 2:
        return image
    out = image.copy()
    out.paste(region.filter(ImageFilter.GaussianBlur(radius=max(2, radius))), (x1, y1))
    return out


def _norm_box(
    box: tuple[int, int, int, int], size: tuple[int, int]
) -> tuple[int, int, int, int]:
    x1, y1, x2, y2 = box
    x1, x2 = sorted((int(x1), int(x2)))
    y1, y2 = sorted((int(y1), int(y2)))
    x1 = max(0, min(x1, size[0] - 1))
    x2 = max(x1 + 1, min(x2, size[0]))
    y1 = max(0, min(y1, size[1] - 1))
    y2 = max(y1 + 1, min(y2, size[1]))
    return x1, y1, x2, y2
