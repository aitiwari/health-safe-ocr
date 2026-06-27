from health_safe_ocr import HealthSafeOCR


ocr = HealthSafeOCR()
result = ocr.extract("patient_letter.jpg", mask_sensitive=True)

print(result.text)
print(result.masked_text)
print(result.confidence)
print(result.requires_human_review)
print(result.entities)

