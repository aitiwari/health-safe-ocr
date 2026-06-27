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

