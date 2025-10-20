import re
from datetime import datetime

from valid_in_out_put import check_control_characters, check_null_bytes

def is_valid_birthday(birthday_str):
    allowed_pattern = r"\d{4}-\d{2}-\d{2}"  # YYYY-MM-DD strictly
    min_date = datetime(1900, 1, 1)
    today = datetime.today()
    
    if isinstance(birthday_str, str):
        if check_null_bytes(birthday_str):
            if check_control_characters(birthday_str):
                if re.fullmatch(allowed_pattern, birthday_str):
                    try:
                        birthday = datetime.strptime(birthday_str, "%Y-%m-%d")
                        if min_date <= birthday <= today:
                            return True
                    except ValueError:
                        pass
    return False
