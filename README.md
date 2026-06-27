# health-safe-ocr

Safe OCR pipeline for healthcare images with PII masking, NHS number validation, confidence scoring, and human review flags.

`health-safe-ocr` helps developers extract text from healthcare images before sending content to an LLM, RAG pipeline, vector database, logs, audit system, or internal API.

## Installation

```bash
pip install health-safe-ocr
```

For local development:

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -e ".[dev]"
```

On macOS or Linux:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

## Tesseract OCR Requirement

This package uses `pytesseract`, which requires the Tesseract OCR system binary to be installed separately.

Windows:

```bash
winget install UB-Mannheim.TesseractOCR
```

macOS:

```bash
brew install tesseract
```

Linux:

```bash
sudo apt install tesseract-ocr
```

## Python Usage

```python
from health_safe_ocr import HealthSafeOCR

ocr = HealthSafeOCR()
result = ocr.extract(
    "patient_letter.jpg",
    mask_sensitive=True,
)

print(result.text)
print(result.masked_text)
print(result.confidence)
print(result.requires_human_review)
print(result.entities)
```

Example result:

```python
OcrResult(
    text="Patient Sachin Tiwari NHS No 485 777 3456",
    masked_text="Patient Sachin Tiwari NHS No [NHS_NUMBER]",
    confidence=0.88,
    requires_human_review=False,
    entities=["NHS_NUMBER"],
    engine="tesseract",
)
```

## CLI Usage

Extract plain text:

```bash
health-safe-ocr patient_letter.jpg
```

Extract and mask PII:

```bash
health-safe-ocr patient_letter.jpg --mask-pii
```

Return JSON:

```bash
health-safe-ocr patient_letter.jpg --mask-pii --json
```

Example JSON output:

```json
{
  "text": "Patient Sachin Tiwari DOB 12/05/1990 NHS No 943 476 5919",
  "masked_text": "Patient Sachin Tiwari [DOB] NHS No [NHS_NUMBER]",
  "confidence": 0.88,
  "requires_human_review": false,
  "entities": ["DOB", "NHS_NUMBER"],
  "engine": "tesseract"
}
```

## Supported PII Masking

Version 0.1.0 supports regex-based masking for:

- Email addresses
- UK phone numbers
- Valid NHS numbers
- Dates of birth
- UK postcodes
- National Insurance numbers
- Patient IDs

## Safety Note

This package does not provide diagnosis, clinical advice or treatment recommendations. It only extracts text from images and masks sensitive information.

Always review OCR output before using it in clinical, operational, audit, or production AI systems. OCR confidence scores and regex masking can miss sensitive data.

## Local Checks

Run tests:

```bash
pytest
```

Run the CLI locally:

```bash
health-safe-ocr examples/sample.jpg --mask-pii --json
```

Build package distributions:

```bash
python -m build
```

Upload to TestPyPI:

```bash
python -m twine upload --repository testpypi dist/*
```

Upload to PyPI:

```bash
python -m twine upload dist/*
```

## Roadmap

### 0.1.0

- Image OCR
- PII masking
- NHS number validation
- CLI
- JSON output
- PyPI release

### 0.2.0

- PDF support
- Scanned PDF page extraction
- Better image preprocessing

### 0.3.0

- PaddleOCR engine option
- Better OCR accuracy
- Multilingual support

### 0.4.0

- Microsoft Presidio integration
- Advanced entity detection
- Name and address masking

### 0.5.0

- Azure Document Intelligence provider
- Cloud OCR fallback

### 1.0.0

- Stable API
- Full docs
- Production examples
- FastAPI integration
- RAG-safe pipeline
- Audit report output

## License

MIT

