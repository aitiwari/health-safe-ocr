from collections.abc import Sequence
import importlib
from typing import Any, Literal

from PIL import Image
import pytesseract

from .engines import EASYOCR_INSTALL_HELP
from .models import OcrResult
from .pii import mask_pii
from .tesseract import TesseractUnavailableError, configure_pytesseract

OcrEngine = Literal["auto", "tesseract", "easyocr"]


NO_OCR_ENGINE_HELP = """No OCR engine is available.

Option 1, lightweight Tesseract backend:
  Windows: winget install UB-Mannheim.TesseractOCR
  macOS: brew install tesseract
  Ubuntu/Debian: sudo apt install tesseract-ocr

Option 2, Python EasyOCR backend:
  pip install "health-safe-ocr[easyocr]"

Then retry with:
  health-safe-ocr image.jpg --mask-pii --json

Or force a backend with:
  health-safe-ocr image.jpg --engine tesseract
  health-safe-ocr image.jpg --engine easyocr
"""


class OcrEngineUnavailableError(RuntimeError):
    """Raised when the requested OCR engine is not installed or unusable."""


class HealthSafeOCR:
    def __init__(
        self,
        review_threshold: float = 0.75,
        engine: OcrEngine = "auto",
        languages: Sequence[str] | None = None,
        easyocr_gpu: bool = False,
    ):
        self.review_threshold = review_threshold
        self.engine = engine
        self.languages = list(languages or ["en"])
        self.easyocr_gpu = easyocr_gpu

    def extract(self, image_path: str, mask_sensitive: bool = True) -> OcrResult:
        if self.engine == "tesseract":
            return self._extract_with_tesseract(image_path, mask_sensitive)

        if self.engine == "easyocr":
            return self._extract_with_easyocr(image_path, mask_sensitive)

        try:
            return self._extract_with_tesseract(image_path, mask_sensitive)
        except TesseractUnavailableError as tesseract_error:
            try:
                return self._extract_with_easyocr(image_path, mask_sensitive)
            except OcrEngineUnavailableError as easyocr_error:
                raise OcrEngineUnavailableError(
                    f"{NO_OCR_ENGINE_HELP}\n"
                    f"Tesseract error: {tesseract_error}\n"
                    f"EasyOCR error: {easyocr_error}"
                ) from easyocr_error

    def _extract_with_tesseract(
        self,
        image_path: str,
        mask_sensitive: bool,
    ) -> OcrResult:
        pytesseract.pytesseract.tesseract_cmd = configure_pytesseract()
        image = Image.open(image_path)
        try:
            data = pytesseract.image_to_data(
                image,
                output_type=pytesseract.Output.DICT,
            )
        except pytesseract.pytesseract.TesseractNotFoundError as exc:
            raise TesseractUnavailableError(str(exc)) from exc

        words: list[str] = []
        confidences: list[float] = []

        for text, conf in zip(data["text"], data["conf"], strict=False):
            if text.strip():
                words.append(text)
                try:
                    score = float(conf)
                except ValueError:
                    continue

                if score >= 0:
                    confidences.append(score)

        full_text = " ".join(words)
        confidence = (
            round(sum(confidences) / len(confidences) / 100, 2)
            if confidences
            else 0.0
        )

        masked_text = None
        entities: list[str] = []
        if mask_sensitive:
            masked_text, entities = mask_pii(full_text)

        return OcrResult(
            text=full_text,
            masked_text=masked_text,
            confidence=confidence,
            requires_human_review=confidence < self.review_threshold,
            entities=entities,
            engine="tesseract",
        )

    def _extract_with_easyocr(
        self,
        image_path: str,
        mask_sensitive: bool,
    ) -> OcrResult:
        try:
            easyocr = importlib.import_module("easyocr")
        except ImportError as exc:
            raise OcrEngineUnavailableError(EASYOCR_INSTALL_HELP) from exc

        reader_class = getattr(easyocr, "Reader")
        reader = reader_class(self.languages, gpu=self.easyocr_gpu)
        raw_results = reader.readtext(image_path)

        words: list[str] = []
        confidences: list[float] = []
        for item in raw_results:
            text, confidence = _parse_easyocr_result(item)
            if text:
                words.append(text)
                confidences.append(confidence)

        full_text = " ".join(words)
        confidence_score = (
            round(sum(confidences) / len(confidences), 2) if confidences else 0.0
        )

        masked_text = None
        entities: list[str] = []
        if mask_sensitive:
            masked_text, entities = mask_pii(full_text)

        return OcrResult(
            text=full_text,
            masked_text=masked_text,
            confidence=confidence_score,
            requires_human_review=confidence_score < self.review_threshold,
            entities=entities,
            engine="easyocr",
        )


def _parse_easyocr_result(item: Any) -> tuple[str, float]:
    try:
        text = str(item[1]).strip()
        confidence = float(item[2])
    except (IndexError, TypeError, ValueError):
        return "", 0.0

    return text, confidence
