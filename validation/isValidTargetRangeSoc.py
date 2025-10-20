import re

from valid_in_out_put import check_control_characters, check_null_bytes

def is_valid_target_range_soc(min_soc: str, max_soc: str) -> bool:
    # Must be 1 to 3 digits only
    if isinstance(min_soc, str) and isinstance(max_soc, str):
        if check_null_bytes(min_soc) and check_null_bytes(max_soc):
            if check_control_characters(min_soc) and check_control_characters(max_soc):
                if re.fullmatch(r"^\d{1,3}$", min_soc) and re.fullmatch(r"^\d{1,3}$", max_soc):
                    min_value = int(min_soc)
                    max_value = int(max_soc)
                    if 0 <= min_value <= max_value <= 100: 
                        return True
    return False