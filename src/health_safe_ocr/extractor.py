from PIL import Image
import pytesseract

from .models import OcrResult
from .pii import mask_pii


class HealthSafeOCR:
    def __init__(self, review_threshold: float = 0.75):
        self.review_threshold = review_threshold

    def extract(self, image_path: str, mask_sensitive: bool = True) -> OcrResult:
        image = Image.open(image_path)
        data = pytesseract.image_to_data(
            image,
            output_type=pytesseract.Output.DICT,
        )

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

