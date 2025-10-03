import re

from DbContext.encrypted_logger import EncryptedLogger


# Helper functions for validation checks (Single Responsibility)

def check_special_case_username(value):
    """Check if username is a special case (super_admin)."""
    return value == "super_admin"

def check_special_case_password(value):
    """Check if password is a special case (Admin_123?)."""
    return value == "Admin_123?"

def check_empty_input(value):
    """Check if input is empty or None using strict whitelisting."""
    return value is None or (isinstance(value, str) and len(value) == 0)

def check_length_limits(value, min_length=None, max_length=None):
    """Check if value meets length requirements."""
    if min_length and len(value) < min_length:
        return False, f"too_short_{min_length}"
    if max_length and len(value) > max_length:
        return False, f"too_long_{max_length}"
    return True, None

def check_username_pattern(value):
    """Check if username matches required pattern using strict whitelisting."""
    # First check if all characters are whitelisted
    if not validate_input_against_whitelist(value, is_whitelisted_username_char):
        return False
    
    # Check length (8-10 characters total)
    if len(value) < 8 or len(value) > 10:
        return False
    
    # Check first character (must be letter or underscore)
    if not value[0] in 'abcdefghijklmnopqrstuvwxyz_':
        return False
    
    return True

def check_password_pattern(value):
    """Check if password contains only whitelisted characters."""
    # Strictly validate against whitelist
    return validate_input_against_whitelist(value, is_whitelisted_password_char)

def check_username_uniqueness(value, existing_usernames):
    """Check if username is unique (case-insensitive)."""
    if not existing_usernames:
        return True
    return value.lower() not in [u.lower() for u in existing_usernames]

def check_password_requirements(value):
    """Check if password meets character requirements using whitelisting."""
    lowercase_chars = 'abcdefghijklmnopqrstuvwxyz'
    uppercase_chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    digit_chars = '0123456789'
    special_chars = '~!@#$%&_+=`|\\(){}[]:;"<>,.?/'
    
    has_lowercase = any(char in lowercase_chars for char in value)
    has_uppercase = any(char in uppercase_chars for char in value)
    has_digit = any(char in digit_chars for char in value)
    has_special = any(char in special_chars for char in value)
    
    if not has_lowercase:
        return False, "no_lowercase"
    if not has_uppercase:
        return False, "no_uppercase"
    if not has_digit:
        return False, "no_digit"
    if not has_special:
        return False, "no_special"
    return True, None

def check_null_bytes(value):
    """Check for null bytes in input."""
    return "\x00" in value


# Strict whitelisting functions (Single Responsibility)

def is_whitelisted_username_char(char):
    """Check if character is whitelisted for username."""
    # Only allow: a-z, 0-9, _, ', .
    return char in 'abcdefghijklmnopqrstuvwxyz0123456789_\'.'

def is_whitelisted_password_char(char):
    """Check if character is whitelisted for password."""
    # Only allow: a-z, A-Z, 0-9, ~!@#$%&_+=`|\(){}[]:;'<>,.?/
    allowed_chars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789~!@#$%&_+=`|\\(){}[]:;\"<>,.?/'
    return char in allowed_chars

def validate_input_against_whitelist(value, char_validator):
    """Validate that all characters in input are whitelisted."""
    if not isinstance(value, str):
        return False
    
    for char in value:
        if not char_validator(char):
            return False
    return True

def check_whitespace_presence(value):
    """Check if input contains any whitespace characters (strictly forbidden)."""
    if not isinstance(value, str):
        return False
    
    # Check for any whitespace characters (space, tab, newline, etc.)
    whitespace_chars = ' \t\n\r\f\v'
    for char in value:
        if char in whitespace_chars:
            return True
    return False

def check_control_characters(value):
    """Check for control characters that should be forbidden."""
    if not isinstance(value, str):
        return False
    
    for char in value:
        # Check for control characters (ASCII 0-31 and 127-159)
        if ord(char) < 32 or (127 <= ord(char) <= 159):
            return True
    return False


# Helper functions for logging (Single Responsibility)

def log_validation_failure(validation_type, error_message, function_name, error_type):
    """Log validation failure with error counting and suspicious activity tracking."""
    logger = EncryptedLogger()
    
    # Track error counts for suspicious activity
    count_attr = f"_{error_type}_count"
    if not hasattr(log_validation_failure, function_name):
        setattr(log_validation_failure, function_name, {})
    
    func_counters = getattr(log_validation_failure, function_name)
    if count_attr not in func_counters:
        func_counters[count_attr] = 0
    
    func_counters[count_attr] += 1
    suspicious_flag = "Yes" if func_counters[count_attr] > 3 else "No"
    
    logger.log_entry(
        "system",
        f"{validation_type} validation failed",
        error_message,
        suspicious=suspicious_flag,
    )

def log_username_validation_failure(error_type, error_message):
    """Log username validation failure."""
    log_validation_failure("Input", error_message, "username", error_type)

def log_password_validation_failure(error_type, error_message):
    """Log password validation failure."""
    log_validation_failure("Password", error_message, "password", error_type)


# Helper functions for user feedback (Single Responsibility)

def print_validation_error(message, mode):
    """Print validation error message if not in login mode."""
    if mode != "login":
        print(message)

def get_error_message(error_type, min_length=None, max_length=None):
    """Get appropriate error message for validation failure."""
    error_messages = {
        "empty": "Input cannot be empty.",
        "too_short": f"Input too short (min {min_length}).",
        "too_long": f"Input too long (max {max_length}).",
        "username_pattern": "Username does not match required format.",
        "password_pattern": "Password contains invalid characters.",
        "not_unique": "Username must be unique.",
        "no_lowercase": "Password must contain at least one lowercase letter.",
        "no_uppercase": "Password must contain at least one uppercase letter.",
        "no_digit": "Password must contain at least one digit.",
        "no_special": "Password must contain at least one special character.",
        "null_byte": "Null byte detected in input."
    }
    return error_messages.get(error_type, "Validation failed.")


# Master validation functions (Single Responsibility - orchestration)

def validate_username(value, existing_usernames=None, min_length=8, max_length=10, mode="create"):
    """
    Master function for username validation using strict whitelisting.
    Orchestrates all username validation steps.
    """
    # Check special cases first
    if check_special_case_username(value):
        return (True, "super_admin")
    
    # Check empty input
    if check_empty_input(value):
        log_username_validation_failure("empty_input", "Input cannot be empty")
        print_validation_error(get_error_message("empty"), mode)
        return (False, value)
    
    # Check for whitespace characters (strictly forbidden)
    if check_whitespace_presence(value):
        log_username_validation_failure("whitespace_detected", "Whitespace characters are not allowed")
        print_validation_error("Whitespace characters are not allowed.", mode)
        return (False, value)
    
    # Check for control characters (strictly forbidden)
    if check_control_characters(value):
        log_username_validation_failure("control_chars", "Control characters are not allowed")
        print_validation_error("Control characters are not allowed.", mode)
        return (False, value)
    
    # Convert to lowercase for case-insensitive validation
    value = value.lower()
    
    # Check length limits
    length_valid, length_error = check_length_limits(value, min_length, max_length)
    if not length_valid:
        error_type = length_error.split('_')[0] + "_" + length_error.split('_')[1]
        length_value = int(length_error.split('_')[2])
        log_username_validation_failure(error_type, f"Input {error_type.replace('_', ' ')} ({error_type.split('_')[0]} {length_value}).")
        print_validation_error(get_error_message(error_type, min_length, max_length), mode)
        return (False, value)
    
    # Check pattern using strict whitelisting
    if not check_username_pattern(value):
        log_username_validation_failure("pattern_mismatch", "Username contains non-whitelisted characters or invalid format")
        print_validation_error(get_error_message("username_pattern"), mode)
        return (False, value)
    
    # Check uniqueness
    if not check_username_uniqueness(value, existing_usernames):
        log_username_validation_failure("not_unique", "Username must be unique.")
        print_validation_error(get_error_message("not_unique"), mode)
        return (False, value)
    
    # Check null bytes
    if check_null_bytes(value):
        log_username_validation_failure("null_byte", "Null byte detected in input.")
        print_validation_error(get_error_message("null_byte"), mode)
        return (False, value)
    
    return (True, value)


def validate_password(value, min_length=12, max_length=30, mode="create"):
    """
    Master function for password validation using strict whitelisting.
    Orchestrates all password validation steps.
    """
    # Check special cases first
    if check_special_case_password(value):
        return (True, "Admin_123?")

    # Check empty input
    if check_empty_input(value):
        log_password_validation_failure("empty_input", "Input cannot be empty")
        print_validation_error(get_error_message("empty"), mode)
        return (False, value)
    
    # Check for whitespace characters (strictly forbidden)
    if check_whitespace_presence(value):
        log_password_validation_failure("whitespace_detected", "Whitespace characters are not allowed")
        print_validation_error("Whitespace characters are not allowed.", mode)
        return (False, value)
    
    # Check for control characters (strictly forbidden)
    if check_control_characters(value):
        log_password_validation_failure("control_chars", "Control characters are not allowed")
        print_validation_error("Control characters are not allowed.", mode)
        return (False, value)
    
    # Check length limits
    length_valid, length_error = check_length_limits(value, min_length, max_length)
    if not length_valid:
        error_type = length_error.split('_')[0] + "_" + length_error.split('_')[1]
        length_value = int(length_error.split('_')[2])
        log_password_validation_failure(error_type, f"Input {error_type.replace('_', ' ')} ({error_type.split('_')[0]} {length_value}).")
        print_validation_error(get_error_message(error_type, min_length, max_length), mode)
        return (False, value)
    
    # Check pattern using strict whitelisting
    if not check_password_pattern(value):
        log_password_validation_failure("pattern_mismatch", "Password contains non-whitelisted characters")
        print_validation_error(get_error_message("password_pattern"), mode)
        return (False, value)
    
    # Check character requirements using whitelisting
    requirements_valid, requirement_error = check_password_requirements(value)
    if not requirements_valid:
        error_messages = {
            "no_lowercase": "Password must contain at least one lowercase letter.",
            "no_uppercase": "Password must contain at least one uppercase letter.",
            "no_digit": "Password must contain at least one digit.",
            "no_special": "Password must contain at least one special character."
        }
        log_password_validation_failure(requirement_error, error_messages[requirement_error])
        print_validation_error(get_error_message(requirement_error), mode)
        return (False, value)
    
    # Check null bytes
    if check_null_bytes(value):
        log_password_validation_failure("null_byte", "Null byte detected in input.")
        print_validation_error(get_error_message("null_byte"), mode)
        return (False, value)
    
    return (True, value)


# Backward compatibility wrapper functions

def validate_input_user(
    value,
    existing_usernames=None,
    min_length=8,
    max_length=10,
    value_type=None,
    allowed_values=None,
    context=None,
    mode="create",
):
    """
    Backward compatibility wrapper for username validation.
    Calls the new master function validate_username.
    """
    return validate_username(value, existing_usernames, min_length, max_length, mode)


def validate_input_pass(
    value,
    min_length=12,
    max_length=30,
    value_type=None,
    allowed_values=None,
    context=None,
    mode="create",
):
    """
    Backward compatibility wrapper for password validation.
    Calls the new master function validate_password.
    """
    return validate_password(value, min_length, max_length, mode)


def sanitize_output(text):
    """Remove control characters (e.g., \x1b) from output."""
    return re.sub(r"[\x00-\x1f\x7f-\x9f]", "", str(text))
