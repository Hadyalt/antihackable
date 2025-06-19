import re

def is_valid_email(email):
    pattern = r"^[\w\.-]+@[\w\.-]+\.\w{2,}$"
    return re.fullmatch(pattern, email) is not None

def is_valid_license_number(license):
    pattern = r"^[A-Z0-9-]{5,20}$"
    return re.fullmatch(pattern, license) is not None

def sanitize_output(text):
    """Remove control characters (e.g., \x1b) from output."""
    return re.sub(r"[\x00-\x1f\x7f-\x9f]", "", str(text))
