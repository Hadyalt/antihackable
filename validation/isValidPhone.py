import re

from valid_in_out_put import check_control_characters, check_null_bytes

def is_valid_phone(phone: str) -> bool:
    # Must be 8 digits only
    if isinstance(phone, str):
        if check_null_bytes(phone):
            if check_control_characters(phone):
                if re.fullmatch(r"^\d{8}$", phone):
                        return True
    return False

def format_phone(phone: str) -> str:
    return f"+31-6-{phone}"

def validate_phone(phone: str) -> tuple[str | None, bool]:
    if is_valid_phone(phone):
        return format_phone(phone), True
    return None, False