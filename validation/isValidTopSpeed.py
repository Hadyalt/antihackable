import re

from valid_in_out_put import check_control_characters, check_null_bytes

def is_valid_top_speed(top_speed: str) -> bool:
    # Must be 1 to 3 digits only
    if isinstance(top_speed, str):
        if check_null_bytes(top_speed):
            if check_control_characters(top_speed):
                if re.fullmatch(r"^\d{1,3}$", top_speed):
                    value = int(top_speed)
                    if 0 <= value <= 100: 
                        return True
    return False
