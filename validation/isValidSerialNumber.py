import re
import sqlite3

from DbContext.crypto_utils import decrypt
from DbContext.encrypted_logger import EncryptedLogger
from scooter.Scooter_data import Scooter_data
from valid_in_out_put import check_control_characters, check_null_bytes

def is_valid_serial_number(serial_number) -> bool:
    pattern = r"^[A-Za-z0-9]{10,17}$"

    if isinstance(serial_number, str):
        if check_null_bytes(serial_number):
            if check_control_characters(serial_number):
                if re.fullmatch(pattern, serial_number):
                    return True
    return False

def scooter_serial_number_exists(serial_number) -> bool:
    db = Scooter_data()
    try:
        db.connect()
        existing_serial_numbers = db.get_all_serial_numbers()
        for existing_sn in existing_serial_numbers:
            validDatabaseSerial = is_valid_serial_number(decrypt(existing_sn[0]))
            if validDatabaseSerial:
                if decrypt(existing_sn[0]) == serial_number:
                    return True
            else:
                faulty_serial_in_db_log(existing_sn)
        return False
    # Database-specific errors
    except sqlite3.OperationalError as e:
        print("Database operational error:", e)
        EncryptedLogger().log_entry("system", f"OperationalError during Scooter serial number check: {e}", " ", "YES")
        return False
    except sqlite3.IntegrityError as e:
        print("Database constraint violation:", e)
        EncryptedLogger().log_entry("system", f"IntegrityError during Scooter serial number check: {e}", " ", "YES")
        return False
    except sqlite3.ProgrammingError as e:
        print("Database programming error:", e)
        EncryptedLogger().log_entry("system", f"ProgrammingError during Scooter serial number check: {e}", " ", "YES")
        return False
    except IndexError as e:
        print("Invalid row format (IndexError):", e)
        EncryptedLogger().log_entry("system", f"IndexError during Scooter serial number check: {e}", " ", "YES")
        return False
    except TypeError as e:
        print("Type error (TypeError):", e)
        EncryptedLogger().log_entry("system", f"TypeError during Scooter serial number check: {e}", " ", "YES")
        return False
    except Exception as e:
        print("Unexpected error:", e)
        EncryptedLogger().log_entry("system", f"UnexpectedError during Scooter serial number check: {e}", " ", "YES")
        return False

def faulty_serial_in_db_log(serial_number):
    print("Warning: Invalid serial number found in database. Contact administrator.")
    print("Logging out for security reasons.")
    logger = EncryptedLogger()
    logger.log_entry("system", f"Invalid serial number in database: {serial_number[0]}", " ", "YES")
    from um_members import pre_login_menu
    logger.log_entry(f"system", "Logged out, because of faulty data in database", " ", "No")
    pre_login_menu()

def validate_serial_number(serial_number) -> bool:
    if is_valid_serial_number(serial_number):
        if not scooter_serial_number_exists(serial_number):
            return True
    return False 
