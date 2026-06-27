from __future__ import annotations

import importlib.util
from dataclasses import dataclass


EASYOCR_INSTALL_HELP = """EasyOCR is optional and can run without the Tesseract desktop app.

Install it with:
  pip install "health-safe-ocr[easyocr]"

The first EasyOCR run may download OCR model files.
"""


@dataclass(frozen=True)
class EasyOCRStatus:
    available: bool
    message: str


def get_easyocr_status() -> EasyOCRStatus:
    if importlib.util.find_spec("easyocr") is None:
        return EasyOCRStatus(
            available=False,
            message=EASYOCR_INSTALL_HELP,
        )

    return EasyOCRStatus(
        available=True,
        message="EasyOCR Python package is available.",
    )
