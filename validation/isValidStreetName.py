import re

def is_valid_street_name(street: str) -> bool:
    if isinstance(street, str):
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
        if re.fullmatch(pattern, street):
            return True
    return False
