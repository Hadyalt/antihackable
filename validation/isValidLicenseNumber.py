import re

# unused in the project
def is_valid_license_number(license):
    if isinstance(license, str):
        pattern = r"^[A-Z0-9-]{5,20}$"
        if re.fullmatch(pattern, license):
            return True
    return False