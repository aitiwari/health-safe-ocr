from health_safe_ocr.pii import mask_pii


def test_email_masking() -> None:
    text = "Email sachin@example.com"
    masked, entities = mask_pii(text)

    assert "[EMAIL]" in masked
    assert "EMAIL" in entities


def test_postcode_masking() -> None:
    text = "Address NE1 1AA"
    masked, entities = mask_pii(text)

    assert "[POSTCODE]" in masked
    assert "POSTCODE" in entities


def test_valid_nhs_number_masking() -> None:
    text = "NHS No 943 476 5919"
    masked, entities = mask_pii(text)

    assert "[NHS_NUMBER]" in masked
    assert "NHS_NUMBER" in entities

