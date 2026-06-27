# health-safe-ocr

Safe OCR pipeline for healthcare images with PII masking, NHS number validation, confidence scoring, and human review flags.

`health-safe-ocr` helps developers extract text from healthcare images before sending content to an LLM, RAG pipeline, vector database, logs, audit system, or internal API.

## Installation

```bash
pip install health-safe-ocr
```

For a Python-only OCR backend that does not require installing the Tesseract
desktop app:

```bash
pip install "health-safe-ocr[easyocr]"
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

## OCR Engines

By default, `health-safe-ocr` uses `engine="auto"`:

1. Use Tesseract when the `tesseract` system command is installed.
2. Fall back to EasyOCR when installed with `health-safe-ocr[easyocr]`.
3. Show clear setup instructions when no OCR engine is available.

Check your local setup:

```bash
health-safe-ocr doctor
```

If Tesseract is installed but not on `PATH`, set `TESSERACT_CMD` to the full executable path. On Windows, the package also tries the common install location automatically:

```powershell
$env:TESSERACT_CMD = "C:\Program Files\Tesseract-OCR\tesseract.exe"
```

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

Or install the optional EasyOCR backend instead:

```bash
pip install "health-safe-ocr[easyocr]"
```

EasyOCR avoids the Tesseract desktop install, but it installs heavier Python
dependencies and may download OCR model files on first use.

## Python Usage

```python
from health_safe_ocr import HealthSafeOCR

ocr = HealthSafeOCR(engine="auto")
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

Force a backend:

```bash
health-safe-ocr patient_letter.jpg --engine tesseract --mask-pii --json
health-safe-ocr patient_letter.jpg --engine easyocr --mask-pii --json
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

Version 0.2.0 supports regex-based masking for:

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

Check OCR dependencies:

```bash
health-safe-ocr doctor
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

- Automatic OCR engine selection
- Optional EasyOCR backend
- Clearer OCR dependency diagnostics

### 0.3.0

- PDF support
- Scanned PDF page extraction
- Better image preprocessing

### 0.4.0

- PaddleOCR engine option
- Better OCR accuracy
- Multilingual support

### 0.5.0

- Microsoft Presidio integration
- Advanced entity detection
- Name and address masking

### 0.6.0

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
