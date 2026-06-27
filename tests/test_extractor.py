from pathlib import Path
from typing import Any

from PIL import Image

from health_safe_ocr import HealthSafeOCR
from health_safe_ocr.extractor import OcrEngineUnavailableError
from health_safe_ocr.tesseract import TesseractUnavailableError


def test_extract_masks_pii_and_calculates_confidence(
    tmp_path: Path,
    monkeypatch: Any,
) -> None:
    image_path = tmp_path / "sample.png"
    Image.new("RGB", (20, 20), "white").save(image_path)

    def fake_image_to_data(image: Image.Image, output_type: object) -> dict[str, list[str]]:
        return {
            "text": ["Patient", "DOB", "12/05/1990", "NHS", "No", "943", "476", "5919"],
            "conf": ["90", "80", "70", "95", "88", "90", "90", "90"],
        }

    monkeypatch.setattr(
        "health_safe_ocr.extractor.configure_pytesseract",
        lambda: "tesseract",
    )
    monkeypatch.setattr(
        "health_safe_ocr.extractor.pytesseract.image_to_data",
        fake_image_to_data,
    )

    result = HealthSafeOCR(review_threshold=0.75, engine="tesseract").extract(
        str(image_path)
    )

    assert result.text == "Patient DOB 12/05/1990 NHS No 943 476 5919"
    assert result.masked_text == "Patient [DOB] NHS No [NHS_NUMBER]"
    assert result.confidence == 0.87
    assert result.requires_human_review is False
    assert result.entities == ["DOB", "NHS_NUMBER"]


def test_extract_raises_clear_error_when_tesseract_missing(
    tmp_path: Path,
    monkeypatch: Any,
) -> None:
    image_path = tmp_path / "sample.png"
    Image.new("RGB", (20, 20), "white").save(image_path)

    def missing_tesseract() -> str:
        raise TesseractUnavailableError("Install Tesseract")

    monkeypatch.setattr(
        "health_safe_ocr.extractor.configure_pytesseract",
        missing_tesseract,
    )

    try:
        HealthSafeOCR(engine="tesseract").extract(str(image_path))
    except TesseractUnavailableError as exc:
        assert "Install Tesseract" in str(exc)
    else:
        raise AssertionError("Expected TesseractUnavailableError")


def test_auto_falls_back_to_easyocr_when_tesseract_missing(
    tmp_path: Path,
    monkeypatch: Any,
) -> None:
    image_path = tmp_path / "sample.png"
    Image.new("RGB", (20, 20), "white").save(image_path)

    class FakeReader:
        def __init__(self, languages: list[str], gpu: bool = False) -> None:
            self.languages = languages
            self.gpu = gpu

        def readtext(self, image_path: str) -> list[tuple[object, str, float]]:
            return [
                (object(), "Email", 0.95),
                (object(), "sachin@example.com", 0.85),
            ]

    class FakeEasyOCR:
        Reader = FakeReader

    def missing_tesseract() -> str:
        raise TesseractUnavailableError("Install Tesseract")

    def fake_import_module(name: str) -> object:
        if name == "easyocr":
            return FakeEasyOCR
        raise ImportError(name)

    monkeypatch.setattr(
        "health_safe_ocr.extractor.configure_pytesseract",
        missing_tesseract,
    )
    monkeypatch.setattr(
        "health_safe_ocr.extractor.importlib.import_module",
        fake_import_module,
    )

    result = HealthSafeOCR(engine="auto").extract(str(image_path))

    assert result.text == "Email sachin@example.com"
    assert result.masked_text == "Email [EMAIL]"
    assert result.confidence == 0.9
    assert result.requires_human_review is False
    assert result.entities == ["EMAIL"]
    assert result.engine == "easyocr"


def test_auto_raises_clear_error_when_no_engine_available(
    tmp_path: Path,
    monkeypatch: Any,
) -> None:
    image_path = tmp_path / "sample.png"
    Image.new("RGB", (20, 20), "white").save(image_path)

    def missing_tesseract() -> str:
        raise TesseractUnavailableError("Install Tesseract")

    def fake_import_module(name: str) -> object:
        raise ImportError(name)

    monkeypatch.setattr(
        "health_safe_ocr.extractor.configure_pytesseract",
        missing_tesseract,
    )
    monkeypatch.setattr(
        "health_safe_ocr.extractor.importlib.import_module",
        fake_import_module,
    )

    try:
        HealthSafeOCR(engine="auto").extract(str(image_path))
    except OcrEngineUnavailableError as exc:
        message = str(exc)
        assert "No OCR engine is available" in message
        assert 'pip install "health-safe-ocr[easyocr]"' in message
    else:
        raise AssertionError("Expected OcrEngineUnavailableError")
