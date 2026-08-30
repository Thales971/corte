from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageFilter, ImageOps


class OcrError(RuntimeError):
    pass


def prepare_for_ocr(image: Image.Image) -> Image.Image:
    """Sobe contraste e limpa ruído antes do Tesseract — muda o jogo em print de aula."""
    work = image.convert("L")
    work = ImageOps.autocontrast(work, cutoff=2)
    if min(work.size) >= 80 and max(work.size) < 1800:
        work = work.resize((work.width * 2, work.height * 2), Image.Resampling.LANCZOS)
    work = work.filter(ImageFilter.MedianFilter(size=3))
    work = work.point(lambda p: 255 if p > 168 else 0)
    return work.convert("RGB")


def extract_text(image_path: Path, lang: str = "por+eng", preprocess: bool = True) -> str:
    try:
        import pytesseract
    except ImportError as exc:
        raise OcrError("pytesseract não está instalado.") from exc

    path = Path(image_path)
    if not path.exists():
        raise OcrError(f"Arquivo não encontrado: {path}")

    image = Image.open(path)
    prepared = prepare_for_ocr(image) if preprocess else image.convert("RGB")
    config = "--oem 3 --psm 6"
    try:
        text = pytesseract.image_to_string(prepared, lang=lang, config=config)
    except pytesseract.TesseractNotFoundError as exc:
        raise OcrError(
            "Tesseract OCR não está no PATH. Instale o motor em "
            "https://github.com/UB-Mannheim/tesseract/wiki e marque "
            "Portuguese + English na instalação."
        ) from exc
    except pytesseract.TesseractError:
        try:
            text = pytesseract.image_to_string(prepared, lang="eng", config=config)
        except Exception as exc:
            raise OcrError(f"Tesseract falhou: {exc}") from exc

    cleaned = "\n".join(line.rstrip() for line in text.splitlines()).strip()
    return cleaned or "(nenhum texto reconhecido)"
