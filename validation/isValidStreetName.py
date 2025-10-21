import re

from valid_in_out_put import check_control_characters, check_length_limits, check_null_bytes

def is_valid_street_name(street: str) -> bool:
    # Define allowed characters
    allowed_chars = r"A-Za-z0-9 .'-"
    # Must start with letter or digit
    start = f"[A-Za-z0-9]"
    # Middle can include allowed characters (including spaces, dots, apostrophes, hyphens)
    middle = f"[{allowed_chars}]*"
    # Must end with letter or digit
    end = f"[A-Za-z0-9]"
    # Must contain at least one letter anywhere
    must_have_letter = r"(?=.*[A-Za-z])"
    # Combine everything into one pattern
    pattern = f"^{must_have_letter}{start}{middle}{end}$"
    # Match the pattern

    if isinstance(street, str):
       if check_null_bytes(street):
            if check_control_characters(street):
                if check_length_limits(street, 2, 100):
                    if re.fullmatch(pattern, street):
                        return True
    return False
