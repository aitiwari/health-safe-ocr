import re


def is_valid_nhs_number(value: str) -> bool:
    digits = re.sub(r"\D", "", value)
    if len(digits) != 10:
        return False

    total = sum(int(digits[i]) * (10 - i) for i in range(9))
    check_digit = 11 - (total % 11)
    if check_digit == 11:
        check_digit = 0
    if check_digit == 10:
        return False

    return check_digit == int(digits[9])

