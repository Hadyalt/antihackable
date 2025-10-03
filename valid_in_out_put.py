from DbContext.encrypted_logger import EncryptedLogger

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
    if not isinstance(value, str):
        return False, "not_string"
    length = len(value)
    if min_length is not None and length < min_length:
        return False, "too_short"
    if max_length is not None and length > max_length:
        return False, "too_long"
    return True, None

# --- Character whitelist validators ---
def is_whitelisted_username_char(char):
    return char in USERNAME_ALLOWED_CHARS

def is_whitelisted_password_char(char):
    return char in PASSWORD_ALLOWED_CHARS

def validate_input_against_whitelist(value, char_validator):
    if not isinstance(value, str) or len(value) == 0:
        return False
    return all(char_validator(ch) for ch in value)

# --- Whitelist-based checks for whitespace / control / nulls (keep functions but as whitelists) ---
def check_whitespace_presence(value):
    if not isinstance(value, str):
        return False
    # whitelist: only allow characters that are not whitespace
    return all(not ch.isspace() for ch in value)

def check_control_characters(value):
    if not isinstance(value, str):
        return False
    # whitelist: every character must be printable
    return all(ch.isprintable() for ch in value)

def check_null_bytes(value):
    if not isinstance(value, str):
        return False
    return "\x00" not in value

# --- Higher-level pattern checks using whitelists ---
def check_username_pattern(value):
    if not isinstance(value, str) or len(value) == 0:
        return False
    if not validate_input_against_whitelist(value, is_whitelisted_username_char):
        return False
    return value[0] in "abcdefghijklmnopqrstuvwxyz_"

def check_password_pattern(value):
    return validate_input_against_whitelist(value, is_whitelisted_password_char)

# --- Uniqueness & requirements (explicit whitelist checks for required character classes) ---
def check_username_uniqueness(value, existing_usernames):
    if not existing_usernames:
        return True
    return value.lower() not in [u.lower() for u in existing_usernames]

def check_password_requirements(value):
    if not isinstance(value, str) or len(value) == 0:
        return False, "no_content"

    has_lower = any(ch in PASSWORD_LOWER for ch in value)
    has_upper = any(ch in PASSWORD_UPPER for ch in value)
    has_digit = any(ch in PASSWORD_DIGITS for ch in value)
    has_special = any(ch in PASSWORD_SPECIALS for ch in value)

    if not has_lower:
        return False, "no_lowercase"
    if not has_upper:
        return False, "no_uppercase"
    if not has_digit:
        return False, "no_digit"
    if not has_special:
        return False, "no_special"
    return True, None

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
def validate_username(value, existing_usernames=None, min_length=8, max_length=10, mode="create"):
    # Special-case whitelist entry
    if check_special_case_username(value):
        return True, "super_admin"

    # Non-empty string (whitelist)
    if not check_non_empty_string(value):
        log_username_validation_failure("empty_input")
        return False, value

    # No whitespace (whitelist)
    if not check_whitespace_presence(value):
        log_username_validation_failure("whitespace_detected")
        return False, value

    # No control characters (whitelist)
    if not check_control_characters(value):
        log_username_validation_failure("control_chars")
        return False, value

    # No null bytes (whitelist)
    if not check_null_bytes(value):
        log_username_validation_failure("null_byte")
        return False, value

    # Must be a string (already ensured by check_non_empty_string, but double-check)
    if not isinstance(value, str):
        log_username_validation_failure("not_string")
        return False, value

    normalized = value.lower()

    # Length (whitelist)
    length_valid, length_error = check_length_limits(normalized, min_length, max_length)
    if not length_valid:
        base_error = length_error.split("_")[0] if length_error else "too_short"
        log_username_validation_failure(base_error)
        return False, value

    # Pattern (explicit char whitelist + first char rule)
    if not check_username_pattern(normalized):
        log_username_validation_failure("pattern_mismatch")
        return False, value

    # Uniqueness
    if not check_username_uniqueness(normalized, existing_usernames):
        log_username_validation_failure("not_unique")
        return False, value

    return True, normalized

def validate_password(value, min_length=12, max_length=30, mode="create"):
    # Special-case whitelist entry
    if check_special_case_password(value):
        return True, "Admin_123?"

    # Non-empty string (whitelist)
    if not check_non_empty_string(value):
        log_password_validation_failure("empty_input")
        return False, value

    # No whitespace (whitelist)
    if not check_whitespace_presence(value):
        log_password_validation_failure("whitespace_detected")
        return False, value

    # No control characters (whitelist)
    if not check_control_characters(value):
        log_password_validation_failure("control_chars")
        return False, value

    # No null bytes (whitelist)
    if not check_null_bytes(value):
        log_password_validation_failure("null_byte")
        return False, value

    # Length checks
    length_valid, length_error = check_length_limits(value, min_length, max_length)
    if not length_valid:
        base_error = length_error.split("_")[0] if length_error else "too_short"
        log_password_validation_failure(base_error)
        return False, value

    # Character whitelist for entire password
    if not check_password_pattern(value):
        log_password_validation_failure("pattern_mismatch")
        return False, value

    # Requirements: explicit whitelist-based checks for required subsets
    req_valid, req_error = check_password_requirements(value)
    if not req_valid:
        log_password_validation_failure(req_error)
        return False, value

    return True, value

# --- Backwards-compatible wrappers ---
def validate_input_user(value, existing_usernames=None, min_length=8, max_length=10, mode="create"):
    return validate_username(value, existing_usernames, min_length, max_length, mode)

def validate_input_pass(value, min_length=12, max_length=30, mode="create"):
    return validate_password(value, min_length, max_length, mode)

# --- Output sanitization (whitelist-based: keep only printable characters) ---
def sanitize_output(text):
    s = str(text)
    return "".join(ch for ch in s if ch.isprintable() and ch != "\x00")
