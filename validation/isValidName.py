import re

def is_valid_name(name):
    """
    Verify that a name contains only allowed characters (whitelisting):
    - Letters (A-Z, a-z, Latin letters with accents)
    - Single apostrophes or hyphens between letters
    - Single spaces between words
    - Must start and end with a letter
    """
    pattern = (
        r"^[A-Za-zÀ-ÖØ-öø-ÿ]"                  # Start with 1 letter
        r"(?:[A-Za-zÀ-ÖØ-öø-ÿ]|"               # Middle letters
        r"[ '\-](?=[A-Za-zÀ-ÖØ-öø-ÿ])){0,49}$" # Spaces/apostrophes/hyphens only if followed by a letter, total max 50 chars
    )

    if isinstance(name, str):
        if re.fullmatch(pattern, name):
            return True
    return False
