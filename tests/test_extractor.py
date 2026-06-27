from pathlib import Path
from typing import Any

from PIL import Image

from health_safe_ocr import HealthSafeOCR


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
        "health_safe_ocr.extractor.pytesseract.image_to_data",
        fake_image_to_data,
    )

    result = HealthSafeOCR(review_threshold=0.75).extract(str(image_path))

    assert result.text == "Patient DOB 12/05/1990 NHS No 943 476 5919"
    assert result.masked_text == "Patient [DOB] NHS No [NHS_NUMBER]"
    assert result.confidence == 0.87
    assert result.requires_human_review is False
    assert result.entities == ["DOB", "NHS_NUMBER"]

