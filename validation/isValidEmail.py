import re

from valid_in_out_put import check_control_characters, check_length_limits, check_null_bytes

def is_valid_email(email):
    pattern = (
            r"[A-Za-z0-9_%+]+"               # Local part start (cannot be . or -)
            r"(?:\.[A-Za-z0-9_%+-]+)*"       # Additional parts after dots (no consecutive dots)
            r"@"
            r"[A-Za-z0-9]+"                  # Domain start (cannot be -)
            r"(?:[-A-Za-z0-9]*[A-Za-z0-9])?" # Domain middle and end
            r"(?:\.[A-Za-z]{2,})+$"          # TLDs
        )
    
    if isinstance(email, str):
        if check_null_bytes(email):
            if check_control_characters(email):
                if check_length_limits(email, 5, 254):  # General email length limits
                    if re.fullmatch(pattern, email):
                        return True
    return False
