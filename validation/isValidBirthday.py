import re
from datetime import datetime

def is_valid_birthday(birthday_str):
    if isinstance(birthday_str, str):
        allowed_pattern = r"\d{4}-\d{2}-\d{2}"  # YYYY-MM-DD strictly
        min_date = datetime(1900, 1, 1)
        today = datetime.today()

        if re.fullmatch(allowed_pattern, birthday_str):
            try:
                birthday = datetime.strptime(birthday_str, "%Y-%m-%d")
                if min_date <= birthday <= today:
                    return True
            except ValueError:
                pass
    return False
