import re

def is_valid_name(name):
    """Verify that a name contains only allowed characters (whitelisting)."""
    # Must be a string and match the whitelist regex entirely
    pattern = r"^[A-Za-zÀ-ÖØ-öø-ÿ](?:[A-Za-zÀ-ÖØ-öø-ÿ'\- ]{0,48}[A-Za-zÀ-ÖØ-öø-ÿ])?$"

    if isinstance(name, str):
        if re.fullmatch(pattern, name):
            return True
    return False
