from DbContext.DbContext import DbContext
from DbContext.crypto_utils import decrypt
from DbContext.encrypted_logger import EncryptedLogger
import sqlite3

# --- Module-level state for logging counters (keeps single responsibility) ---
_validation_counters = {}

# --- Explicit character sets (whitelists) ---
USERNAME_ALLOWED_CHARS = set("abcdefghijklmnopqrstuvwxyz0123456789_.'")
PASSWORD_LOWER = set("abcdefghijklmnopqrstuvwxyz")
PASSWORD_UPPER = set("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
PASSWORD_DIGITS = set("0123456789")
PASSWORD_SPECIALS = set('~!@#$%&_+=`|\\(){}[]:;"<>,.?/-')
PASSWORD_ALLOWED_CHARS = PASSWORD_LOWER | PASSWORD_UPPER | PASSWORD_DIGITS | PASSWORD_SPECIALS

# --- Special-case checks (explicit whitelist entries) ---
def check_special_case_username(value):
    return value == "super_admin"

def check_special_case_password(value):
    return value == "Admin_123?"

# --- Basic input checks (whitelist semantics: True == valid) ---
def check_non_empty_string(value):
    return isinstance(value, str) and len(value) > 0

def check_length_limits(value, min_length=None, max_length=None):
    if isinstance(value, str): 
        length = len(value)
        if min_length is not None and length >= min_length:
            if max_length is not None and length <= max_length:
                return True
    return False

# --- Character whitelist validators ---
def is_whitelisted_username_char(char):
    return char in USERNAME_ALLOWED_CHARS

def is_whitelisted_password_char(char):
    return char in PASSWORD_ALLOWED_CHARS

def validate_input_against_whitelist(value, char_validator):
    if isinstance(value, str) or len(value) == 0:
        return all(char_validator(ch) for ch in value)
    return False

# --- Whitelist-based checks for whitespace / control / nulls (keep functions but as whitelists) ---
def check_whitespace_presence(value):
    if isinstance(value, str):
        return all(not ch.isspace() for ch in value)
    return False

def check_control_characters(value):
    if isinstance(value, str):
        return all(ch.isprintable() for ch in value)
    return False

def check_null_bytes(value):
    if isinstance(value, str):
        return "\x00" not in value
    return False

# --- Higher-level pattern checks using whitelists ---
def check_username_pattern(value):
    if isinstance(value, str) and len(value) > 0:
        if validate_input_against_whitelist(value, is_whitelisted_username_char):
            return value[0] in "abcdefghijklmnopqrstuvwxyz_"
    return False

def check_password_pattern(value):
    return validate_input_against_whitelist(value, is_whitelisted_password_char)

# --- Uniqueness & requirements (explicit whitelist checks for required character classes) ---
def check_username_uniqueness(value, existing_usernames):
    if not existing_usernames:
        return True
    return False

def check_username_exists_simple(username):
    try:
        db = DbContext()
        connection = db.connect()
        cursor = connection.cursor()
        cursor.execute("SELECT Username, Role FROM User WHERE IsActive = 1")
        all_users = cursor.fetchall()

        matching_users = [user for user in all_users if decrypt(user[0]).lower() == username]
        if not matching_users:
            return None
        else:
            return matching_users[0]

    except ConnectionError as e:
        print(f"Failed because of an error")
        logger = EncryptedLogger()
        logger.log_entry("system", "Database connection error", str(e), "Yes")
        return "connection_error"

    except sqlite3.OperationalError as e:
        print(f"Failed because of an error")
        logger = EncryptedLogger()
        logger.log_entry("system", "Database operational error", str(e), "Yes")
        return "operational_error"

    except sqlite3.ProgrammingError as e:
        print(f"Failed because of an error")
        logger = EncryptedLogger()
        logger.log_entry("system", "Database programming error", str(e), "Yes")
        return "programming_error"

    except ValueError as e:
        print(f"Failed because of an error")
        logger = EncryptedLogger()
        logger.log_entry("system", "Decryption or data processing error", str(e), "Yes")
        return "decrypt_error"

    except Exception as e:
        print(f"Failed because of an error")
        logger = EncryptedLogger()
        logger.log_entry("system", "Unexpected error", str(e), "Yes")
        return "unknown_error"

    finally:
        try:
            if connection:
                connection.close()
        except Exception:
            pass


def check_password_requirements(value):
    if isinstance(value, str) and len(value) > 0:

        has_lower = any(ch in PASSWORD_LOWER for ch in value)
        has_upper = any(ch in PASSWORD_UPPER for ch in value)
        has_digit = any(ch in PASSWORD_DIGITS for ch in value)
        has_special = any(ch in PASSWORD_SPECIALS for ch in value)

        if has_lower:
            if  has_upper:
                if  has_digit:
                    if has_special:
                        return True, None

    return False, None

# --- Logging helpers (kept simple) ---
def log_validation_failure(validation_type, error_message, function_name, error_type):
    logger = EncryptedLogger()

    key = f"{function_name}:{error_type}"
    count = _validation_counters.get(key, 0) + 1
    _validation_counters[key] = count
    suspicious_flag = "Yes" if count > 3 else "No"

    logger.log_entry(
        "system",
        f"{validation_type} validation failed ({function_name})",
        error_message or error_type,
        suspicious=suspicious_flag,
    )

def log_username_validation_failure(error_type, error_message=""):
    log_validation_failure("Input", error_message, "username", error_type)

def log_password_validation_failure(error_type, error_message=""):
    log_validation_failure("Password", error_message, "password", error_type)

# --- Master validators (treat helper True == valid) ---
def validate_username(value, min_length=8, max_length=10, mode="create"):
    # Special-case whitelist entry
    if check_special_case_username(value):
        return True, "super_admin"

    # Non-empty string (whitelist)
    if check_non_empty_string(value):

        # No whitespace (whitelist)
        if check_whitespace_presence(value):

            # No control characters (whitelist)
            if check_control_characters(value):
                
                # No null bytes (whitelist)
                if check_null_bytes(value):

                    # Must be a string (already ensured by check_non_empty_string, but double-check)
                    if isinstance(value, str):

                        # Length (whitelist) - check on original value first
                        if check_length_limits(value, min_length, max_length):

                            # Pattern (explicit char whitelist + first char rule) - check on original value
                            if check_username_pattern(value):

                                return True, value

    return False, value

def validate_password(value, min_length=12, max_length=30, mode="create"):
    # Special-case whitelist entry
    if check_special_case_password(value):
        return True, "Admin_123?"

    # Non-empty string (whitelist)
    if check_non_empty_string(value):

        # No whitespace (whitelist)
        if check_whitespace_presence(value):

            # No control characters (whitelist)
            if check_control_characters(value):

                # No null bytes (whitelist)
                if check_null_bytes(value):

                    # Length checks
                    if check_length_limits(value, min_length, max_length):
                        
                        # Character whitelist for entire password
                        if check_password_pattern(value):

                            # Requirements: explicit whitelist-based checks for required subsets
                            if check_password_requirements(value):
                                return True, value
    return False, value


# --- Backwards-compatible wrappers ---
def validate_input_username(value, min_length=8, max_length=10, mode="create"):
    # First validate the username format (100% validation)
    is_valid, value = validate_username(value, min_length, max_length, mode)
    
    if not is_valid:
        return False, value
    
    # After validation passes, check database for uniqueness (only in create mode)
    if mode == "create":
        normalized_username = value.lower()
        existing_user = check_username_exists_simple(normalized_username)
        
        # If database error, return error
        if isinstance(existing_user, str):
            return True, value
        
        # If user exists, fail validation
        if existing_user is not None:
            return True, value
    
    # All checks passed
    return False, value

def validate_input_pass(value, min_length=12, max_length=30, mode="create"):
    return validate_password(value, min_length, max_length, mode)

# --- Output sanitization (whitelist-based: keep only printable characters) ---
def sanitize_output(text):
    s = str(text)
    return "".join(ch for ch in s if ch.isprintable() and ch != "\x00")

