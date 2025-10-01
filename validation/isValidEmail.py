import re

def is_valid_email(email):
    if isinstance(email, str):
        pattern = (
            r"^(?![.-])"  # No leading dot or hyphen
            r"(?!.*\.\.)"  # No consecutive dots
            r"[A-Za-z0-9._%+-]+"  # Local part
            r"@"
            r"(?!-)"  # No leading hyphen in domain
            r"[A-Za-z0-9.-]+"  # Domain part
            r"\.[A-Za-z]{2,}$"  # TLD
        )
        if re.fullmatch(pattern, email):
                return True
    return False
    