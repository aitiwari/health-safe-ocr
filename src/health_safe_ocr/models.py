from dataclasses import dataclass, field


@dataclass
class OcrResult:
    text: str
    masked_text: str | None = None
    confidence: float | None = None
    requires_human_review: bool = False
    entities: list[str] = field(default_factory=list)
    engine: str = "tesseract"

