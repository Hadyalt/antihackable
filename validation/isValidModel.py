import re

from valid_in_out_put import check_control_characters, check_null_bytes

def is_valid_model(name):
    allowed_pattern = r"[A-Za-zÀ-ÖØ-öø-ÿ0-9 ./'()\-]{1,70}"  # whitelist setting
    letter_pattern = r"[A-Za-zÀ-ÖØ-öø-ÿ]"  # ensure there's at least one letter


    # Check 1: must be a string
    if isinstance(name, str):
        if check_null_bytes(name):
            if check_control_characters(name):
                if re.fullmatch(allowed_pattern, name):
                    if re.search(letter_pattern, name):
                        return True
    return False
