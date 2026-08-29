from __future__ import annotations

from pathlib import Path

from PIL import Image


class OcrError(RuntimeError):
    pass


def extract_text(image_path: Path, lang: str = "por+eng") -> str:
    try:
        import pytesseract
    except ImportError as exc:
        raise OcrError("pytesseract não está instalado.") from exc

    path = Path(image_path)
    if not path.exists():
        raise OcrError(f"Arquivo não encontrado: {path}")

    image = Image.open(path)
    try:
        text = pytesseract.image_to_string(image, lang=lang)
    except pytesseract.TesseractNotFoundError as exc:
        raise OcrError(
            "Tesseract OCR não está no PATH. Instale o motor em "
            "https://github.com/UB-Mannheim/tesseract/wiki e marque "
            "Portuguese + English na instalação."
        ) from exc
    except pytesseract.TesseractError:
        text = pytesseract.image_to_string(image, lang="eng")

    cleaned = "\n".join(line.rstrip() for line in text.splitlines()).strip()
    return cleaned or "(nenhum texto reconhecido)"
