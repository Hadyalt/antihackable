import re

def sanitize_output(text):
    """Remove control characters (e.g., \x1b) from output."""
    return re.sub(r"[\x00-\x1f\x7f-\x9f]", "", str(text))