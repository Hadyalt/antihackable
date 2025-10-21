import re

from valid_in_out_put import check_control_characters, check_null_bytes

def is_valid_state_of_charge(state_of_charge: str) -> bool:
    # Must be 1 to 3 digits only
    if isinstance(state_of_charge, str):
        if check_null_bytes(state_of_charge):
            if check_control_characters(state_of_charge):
                if re.fullmatch(r"^\d{1,3}$", state_of_charge):
                    value = int(state_of_charge)
                    if 0 <= value <= 100: 
                        return True
    return False