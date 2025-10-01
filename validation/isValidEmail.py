import re

def is_valid_email(email):
    if isinstance(email, str):
        pattern = (
            r"[A-Za-z0-9_%+]+"               # Local part start (cannot be . or -)
            r"(?:\.[A-Za-z0-9_%+-]+)*"       # Additional parts after dots (no consecutive dots)
            r"@"
            r"[A-Za-z0-9]+"                  # Domain start (cannot be -)
            r"(?:[-A-Za-z0-9]*[A-Za-z0-9])?"  # Domain middle and end
            r"(?:\.[A-Za-z]{2,})+$"          # TLDs
        )
        if re.fullmatch(pattern, email):
            return True
    return False
