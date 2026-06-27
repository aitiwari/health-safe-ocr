import re

from .nhs import is_valid_nhs_number


def mask_pii(text: str) -> tuple[str, list[str]]:
    entities: list[str] = []
    masked = text

    patterns = {
        "EMAIL": r"\b[\w\.-]+@[\w\.-]+\.\w+\b",
        "PHONE": r"\b(?:\+44\s?7\d{3}|07\d{3})\s?\d{3}\s?\d{3}\b",
        "DOB": r"\b(?:DOB|Date of Birth)?\s*:?\s?\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b",
        "POSTCODE": r"\b[A-Z]{1,2}\d[A-Z\d]?\s?\d[A-Z]{2}\b",
        "NI_NUMBER": r"\b[A-CEGHJ-PR-TW-Z]{2}\d{6}[A-D]\b",
        "PATIENT_ID": r"\b(?:PAT\b|Patient ID|Patient No)\s*:?\s?[A-Z0-9-]{4,}\b",
    }

    for entity, pattern in patterns.items():
        if re.search(pattern, masked, flags=re.IGNORECASE):
            masked = re.sub(pattern, f"[{entity}]", masked, flags=re.IGNORECASE)
            entities.append(entity)

    nhs_pattern = r"\b\d{3}\s?\d{3}\s?\d{4}\b"
    for match in re.findall(nhs_pattern, masked):
        if is_valid_nhs_number(match):
            masked = masked.replace(match, "[NHS_NUMBER]")
            entities.append("NHS_NUMBER")

    return masked, sorted(set(entities))
