import re

def is_valid_model(name):
    allowed_pattern = r"[A-Za-zÀ-ÖØ-öø-ÿ0-9 ./'()\-]{1,150}"  # whitelist setting

    # Check 1: must be a string
    if isinstance(name, str):
        # Check 2: must match allowed characters and length
        if re.fullmatch(allowed_pattern, name):
            return True
    return False
