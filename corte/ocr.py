from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from PIL import Image, ImageFilter, ImageOps


class OcrError(RuntimeError):
    pass


@dataclass(frozen=True)
class OcrResult:
    text: str
    confidence: float
    lang: str
    words: int
    lines: int
    source: Path
    saved_txt: Path | None = None

    def preview(self, limit: int = 240) -> str:
        compact = " ".join(self.text.split())
        if len(compact) <= limit:
            return compact
        return compact[: limit - 1] + "…"


def _mean_luma(image: Image.Image) -> float:
    gray = image.convert("L")
    hist = gray.histogram()
    total = sum(hist) or 1
    return sum(i * count for i, count in enumerate(hist)) / total


def prepare_variants(image: Image.Image) -> list[tuple[str, Image.Image]]:
    base = image.convert("RGB")
    gray = ImageOps.autocontrast(base.convert("L"), cutoff=1)
    if min(gray.size) >= 60 and max(gray.size) < 2200:
        gray = gray.resize((gray.width * 2, gray.height * 2), Image.Resampling.LANCZOS)
    gray = gray.filter(ImageFilter.MedianFilter(size=3))
    gray = gray.filter(ImageFilter.SHARPEN)
    binary = gray.point(lambda p: 255 if p > 160 else 0)
    soft = ImageOps.autocontrast(gray, cutoff=0)
    inverted = ImageOps.invert(gray)
    inverted_bin = inverted.point(lambda p: 255 if p > 160 else 0)
    variants = [("binario", binary.convert("RGB")), ("suave", soft.convert("RGB"))]
    if _mean_luma(base) < 118:
        variants.insert(0, ("invertido-binario", inverted_bin.convert("RGB")))
        variants.insert(1, ("invertido", inverted.convert("RGB")))
    else:
        variants.append(("invertido-binario", inverted_bin.convert("RGB")))
    return variants


def prepare_for_ocr(image: Image.Image) -> Image.Image:
    variants = prepare_variants(image)
    for name, variant in variants:
        if name in {"binario", "invertido-binario"}:
            return variant
    return variants[0][1]


def _clean_text(raw: str) -> str:
    lines = []
    for line in raw.splitlines():
        stripped = " ".join(line.split())
        if stripped:
            lines.append(stripped)
    return "\n".join(lines).strip()


def _score_data(data: dict) -> tuple[float, int]:
    confs = []
    words = 0
    n = len(data.get("text", []))
    for i in range(n):
        piece = (data["text"][i] or "").strip()
        try:
            conf = float(data["conf"][i])
        except (TypeError, ValueError, KeyError):
            continue
        if piece and conf >= 0:
            confs.append(conf)
            words += 1
    if not confs:
        return 0.0, 0
    return sum(confs) / len(confs), words


def _try_read(pytesseract, image: Image.Image, lang: str, psm: int) -> tuple[str, float, int]:
    config = f"--oem 3 --psm {psm}"
    text = pytesseract.image_to_string(image, lang=lang, config=config)
    try:
        data = pytesseract.image_to_data(
            image, lang=lang, config=config, output_type=pytesseract.Output.DICT
        )
        confidence, words = _score_data(data)
    except Exception:
        cleaned = _clean_text(text)
        return cleaned, (40.0 if cleaned else 0.0), len(cleaned.split())
    return _clean_text(text), confidence, words


def read_image(
    image_path: Path,
    lang: str = "por+eng",
    preprocess: bool = True,
    save_txt: bool = False,
) -> OcrResult:
    try:
        import pytesseract
    except ImportError as exc:
        raise OcrError("pytesseract não está instalado. Rode: pip install pytesseract") from exc

    path = Path(image_path)
    if not path.exists():
        raise OcrError(f"Arquivo não encontrado: {path}")
    try:
        source = Image.open(path)
        source.load()
    except Exception as exc:
        raise OcrError(f"Não abri a imagem: {exc}") from exc

    variants = prepare_variants(source) if preprocess else [("original", source.convert("RGB"))]
    attempts = [(lang, variants[0][1], 6)]
    if len(variants) > 1:
        attempts.append((lang, variants[1][1], 6))
    attempts.append((lang, variants[0][1], 4))
    attempts.append((lang, variants[0][1], 3))
    if lang != "eng":
        attempts.append(("eng", variants[0][1], 6))

    best_text = ""
    best_conf = -1.0
    best_words = 0
    best_lang = lang
    last_error = None

    for used_lang, variant, psm in attempts:
        try:
            text, conf, words = _try_read(pytesseract, variant, used_lang, psm)
        except pytesseract.TesseractNotFoundError as exc:
            raise OcrError(
                "Tesseract OCR não está no PATH. Instale o motor em "
                "https://github.com/UB-Mannheim/tesseract/wiki "
                "e marque Portuguese + English."
            ) from exc
        except Exception as exc:
            last_error = exc
            continue
        score = conf + min(len(text), 400) / 80 + min(words, 40) / 8
        if text and score > best_conf:
            best_text, best_conf, best_words, best_lang = text, conf, words, used_lang
        if best_conf >= 80 and best_words >= 3:
            break

    if not best_text:
        if last_error:
            raise OcrError(f"Tesseract falhou: {last_error}") from last_error
        best_text = "(nenhum texto reconhecido)"
        best_conf = 0.0

    lines = 0 if best_text.startswith("(") else best_text.count("\n") + 1
    saved = None
    if save_txt and not best_text.startswith("("):
        saved = path.with_suffix(".txt")
        saved.write_text(best_text + "\n", encoding="utf-8")

    return OcrResult(
        text=best_text,
        confidence=round(max(0.0, best_conf), 1),
        lang=best_lang,
        words=best_words,
        lines=lines,
        source=path,
        saved_txt=saved,
    )


def extract_text(image_path: Path, lang: str = "por+eng", preprocess: bool = True) -> str:
    return read_image(image_path, lang=lang, preprocess=preprocess).text
