import re

def is_valid_driving_license(license):
    """
    Validate driving license number (pure whitelisting):
    - Either 2 uppercase letters followed by 7 digits (XXDDDDDDD)
    - Or 1 uppercase letter followed by 8 digits (XDDDDDDDD)
    """
    pattern = r"^(?:[A-Z]{2}\d{7}|[A-Z]{1}\d{8})$"

    if isinstance(license, str):
        if re.fullmatch(pattern, license):
            return True
    return False
