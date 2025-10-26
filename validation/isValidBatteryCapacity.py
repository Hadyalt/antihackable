import re

from valid_in_out_put import check_control_characters, check_null_bytes

def is_valid_battery_capacity(battery_capacity: str) -> bool:
    # Must be 1 to 5 digits only
    if isinstance(battery_capacity, str):
        if check_null_bytes(battery_capacity):
            if check_control_characters(battery_capacity):
                if re.fullmatch(r"^\d{1,5}$", battery_capacity):
                    value = int(battery_capacity)
                    if 0 <= value <= 10000: 
                        return True
    return False
