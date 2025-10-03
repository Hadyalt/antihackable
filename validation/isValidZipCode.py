import re

def is_valid_zip_code(zip_code):
    """
    Validate Dutch-style zip code (pure whitelisting):
    - Exactly 4 digits followed by 2 uppercase letters
    """
    pattern = r"^\d{4}[A-Z]{2}$"

    if isinstance(zip_code, str):
        if re.fullmatch(pattern, zip_code):
            return True
    return False
