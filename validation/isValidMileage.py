import re

from valid_in_out_put import check_control_characters, check_null_bytes

def is_valid_mileage(mileage: str) -> bool:
    # Must be a non-negative number
    if isinstance(mileage, str):
        if check_null_bytes(mileage):
            if check_control_characters(mileage):
                # Allow only digits, max length 10
                if re.fullmatch(r"^\d{1,10}$", mileage):
                    value = int(mileage)
                    if value >= 0:
                        return True
    return False