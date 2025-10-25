import re
from datetime import datetime

from valid_in_out_put import check_control_characters, check_null_bytes

def is_valid_maintenance_date(maintenance_date_str):
    allowed_pattern = r"\d{4}-\d{2}-\d{2}"  # YYYY-MM-DD strictly
    min_date = datetime(1980, 1, 1)
    today = datetime.today()

    if isinstance(maintenance_date_str, str):
        if check_null_bytes(maintenance_date_str):
            if check_control_characters(maintenance_date_str):
                if re.fullmatch(allowed_pattern, maintenance_date_str):
                    try:
                        maintenance_date = datetime.strptime(maintenance_date_str, "%Y-%m-%d")
                        if min_date <= maintenance_date <= today:
                            return True
                    except ValueError:
                        pass
    return False

def is_newer_maintenance_date(new_date_str, old_date_str):
    try:
        new_date = datetime.strptime(new_date_str, "%Y-%m-%d")
        old_date = datetime.strptime(old_date_str, "%Y-%m-%d")
        return new_date >= old_date
    except ValueError:
        return False
