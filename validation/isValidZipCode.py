import re

from valid_in_out_put import check_control_characters, check_null_bytes

def is_valid_zip_code(zip_code):
    """
    Validate Dutch-style zip code (pure whitelisting):
    - Exactly 4 digits followed by 2 uppercase letters
    """
    pattern = r"^\d{4}[A-Z]{2}$"

    if isinstance(zip_code, str):
        if check_null_bytes(zip_code):
            if check_control_characters(zip_code):
                if re.fullmatch(pattern, zip_code):
                    return True
    return False
