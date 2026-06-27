from health_safe_ocr.nhs import is_valid_nhs_number


def test_valid_nhs_number() -> None:
    assert is_valid_nhs_number("943 476 5919") is True


def test_invalid_nhs_number() -> None:
    assert is_valid_nhs_number("123 456 7890") is False

