# CLI Usage

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

Use EasyOCR instead of Tesseract:

```bash
pip install "health-safe-ocr[easyocr]"
health-safe-ocr patient_letter.jpg --engine easyocr --mask-pii --json
```

Check local OCR setup:

```bash
health-safe-ocr doctor
```
