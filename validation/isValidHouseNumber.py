import re

from valid_in_out_put import check_control_characters, check_null_bytes

def is_valid_house_number(house_number: str) -> bool:
    # Must be 1 to 4 digits only
    if isinstance(house_number, str):
        if check_null_bytes(house_number):
            if check_control_characters(house_number):
                if re.fullmatch(r"^\d{1,4}$", house_number):
                    value = int(house_number)
                    if 1 <= value <= 9999: 
                        return True
    return False
