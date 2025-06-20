import re

from DbContext.encrypted_logger import EncryptedLogger


def validate_input_user(
    value,
    existing_usernames=None,  # New parameter for uniqueness check
    min_length=8,
    max_length=10,
    value_type=None,
    allowed_values=None,
    context=None,
):
    """
    Username validation according to project rules.
    - Must be unique (case-insensitive)
    - 8-10 chars, starts with letter or _, allowed: a-z, 0-9, _, ', .
    - Case-insensitive
    """
    if value == "super_admin":
        return "super_admin"  # Special case for super_admin

    if value is None or (isinstance(value, str) and value.strip() == ""):
        logger = EncryptedLogger()
        if not hasattr(validate_input_user, "_empty_input_count"):
            validate_input_user._empty_input_count = 0
        validate_input_user._empty_input_count += 1
        suspicious_flag = "Yes" if validate_input_user._empty_input_count > 3 else "No"
        logger.log_entry(
            "system",
            "Input validation failed",
            "Input cannot be empty",
            suspicious=suspicious_flag,
        )
        print("Input cannot be empty.")
        return False

    value = value.lower()
    if min_length and len(value) < min_length:
        logger = EncryptedLogger()
        if not hasattr(validate_input_user, "_too_short_count"):
            validate_input_user._too_short_count = 0
        validate_input_user._too_short_count += 1
        suspicious_flag = "Yes" if validate_input_user._too_short_count > 3 else "No"
        logger.log_entry(
            "system",
            "Input validation failed",
            f"Input too short (min {min_length}).",
            suspicious=suspicious_flag,
        )
        print(f"Input too short (min {min_length}).")
        return False

    if max_length and len(value) > max_length:
        logger = EncryptedLogger()
        if not hasattr(validate_input_user, "_too_long_count"):
            validate_input_user._too_long_count = 0
        validate_input_user._too_long_count += 1
        suspicious_flag = "Yes" if validate_input_user._too_long_count > 3 else "No"
        logger.log_entry(
            "system",
            "Input validation failed",
            f"Input too long (max {max_length}).",
            suspicious=suspicious_flag,
        )
        print(f"Input too long (max {max_length}).")
        return False

    # Username regex: starts with letter or _, then allowed chars
    pattern = r"^[a-z_][a-z0-9_'.]{7,9}$"
    if not re.fullmatch(pattern, value):
        logger = EncryptedLogger()
        if not hasattr(validate_input_user, "_pattern_mismatch_count"):
            validate_input_user._pattern_mismatch_count = 0
        validate_input_user._pattern_mismatch_count += 1
        suspicious_flag = (
            "Yes" if validate_input_user._pattern_mismatch_count > 3 else "No"
        )
        logger.log_entry(
            "system",
            "Input validation failed",
            f"Pattern mismatch: {pattern}",
            suspicious=suspicious_flag,
        )
        print("Username does not match required format.")
        return False

    if existing_usernames and value in [u.lower() for u in existing_usernames]:
        logger = EncryptedLogger()
        if not hasattr(validate_input_user, "_not_unique_count"):
            validate_input_user._not_unique_count = 0
        validate_input_user._not_unique_count += 1
        suspicious_flag = "Yes" if validate_input_user._not_unique_count > 3 else "No"
        logger.log_entry(
            "system",
            "Input validation failed",
            "Username must be unique.",
            suspicious=suspicious_flag,
        )
        print("Username must be unique.")
        return False

    if "\x00" in value:
        logger = EncryptedLogger()
        if not hasattr(validate_input_user, "_null_byte_count"):
            validate_input_user._null_byte_count = 0
        validate_input_user._null_byte_count += 1
        suspicious_flag = "Yes" if validate_input_user._null_byte_count > 3 else "No"
        logger.log_entry(
            "system",
            "Input validation failed",
            "Null byte detected in input.",
            suspicious=suspicious_flag,
        )
        print("Null byte detected in input.")
        return False

    return value


def validate_input_pass(
    value,
    min_length=12,
    max_length=30,
    value_type=None,
    allowed_values=None,
    context=None,
):
    """
    Password validation according to project rules.
    - 12-30 chars
    - Allowed: a-z, A-Z, 0-9, ~!@#$%&_+=`|\(){}[]:;'<>,.?/
    - Must have at least one lowercase, one uppercase, one digit, one special char
    """
    if value == "Admin_123?":
        return "Admin_123?"  # Special case for Admin password

    if value is None or (isinstance(value, str) and value.strip() == ""):
        logger = EncryptedLogger()
        if not hasattr(validate_input_pass, "_empty_input_count"):
            validate_input_pass._empty_input_count = 0
        validate_input_pass._empty_input_count += 1
        suspicious_flag = "Yes" if validate_input_pass._empty_input_count > 3 else "No"
        logger.log_entry(
            "system",
            "Password validation failed",
            "Input cannot be empty",
            suspicious=suspicious_flag,
        )
        print("Input cannot be empty.")
        return False

    if min_length and len(value) < min_length:
        logger = EncryptedLogger()
        if not hasattr(validate_input_pass, "_too_short_count"):
            validate_input_pass._too_short_count = 0
        validate_input_pass._too_short_count += 1
        suspicious_flag = "Yes" if validate_input_pass._too_short_count > 3 else "No"
        logger.log_entry(
            "system",
            "Password validation failed",
            f"Input too short (min {min_length}).",
            suspicious=suspicious_flag,
        )
        print(f"Input too short (min {min_length}).")
        return False

    if max_length and len(value) > max_length:
        logger = EncryptedLogger()
        if not hasattr(validate_input_pass, "_too_long_count"):
            validate_input_pass._too_long_count = 0
        validate_input_pass._too_long_count += 1
        suspicious_flag = "Yes" if validate_input_pass._too_long_count > 3 else "No"
        logger.log_entry(
            "system",
            "Password validation failed",
            f"Input too long (max {max_length}).",
            suspicious=suspicious_flag,
        )
        print(f"Input too long (max {max_length}).")
        return False

    # Allowed special chars: ~!@#$%&_+=`|\(){}[]:;'<>,.?/
    allowed_special = r"~!@#$%&_+=`|\\(){}\[\]:;'<>,\.\?/"
    pattern = rf"^[a-zA-Z0-9{allowed_special}]+$"
    if not re.fullmatch(pattern, value):
        logger = EncryptedLogger()
        if not hasattr(validate_input_pass, "_pattern_mismatch_count"):
            validate_input_pass._pattern_mismatch_count = 0
        validate_input_pass._pattern_mismatch_count += 1
        suspicious_flag = (
            "Yes" if validate_input_pass._pattern_mismatch_count > 3 else "No"
        )
        logger.log_entry(
            "system",
            "Password validation failed",
            f"Pattern mismatch: {pattern}",
            suspicious=suspicious_flag,
        )
        print("Password contains invalid characters.")
        return False

    # At least one lowercase, one uppercase, one digit, one special char
    if not re.search(r"[a-z]", value):
        logger = EncryptedLogger()
        if not hasattr(validate_input_pass, "_no_lowercase_count"):
            validate_input_pass._no_lowercase_count = 0
        validate_input_pass._no_lowercase_count += 1
        suspicious_flag = "Yes" if validate_input_pass._no_lowercase_count > 3 else "No"
        logger.log_entry(
            "system",
            "Password validation failed",
            "Password must contain at least one lowercase letter.",
            suspicious=suspicious_flag,
        )
        print("Password must contain at least one lowercase letter.")
        return False

    if not re.search(r"[A-Z]", value):
        logger = EncryptedLogger()
        if not hasattr(validate_input_pass, "_no_uppercase_count"):
            validate_input_pass._no_uppercase_count = 0
        validate_input_pass._no_uppercase_count += 1
        suspicious_flag = "Yes" if validate_input_pass._no_uppercase_count > 3 else "No"
        logger.log_entry(
            "system",
            "Password validation failed",
            "Password must contain at least one uppercase letter.",
            suspicious=suspicious_flag,
        )
        print("Password must contain at least one uppercase letter.")
        return False

    if not re.search(r"[0-9]", value):
        logger = EncryptedLogger()
        if not hasattr(validate_input_pass, "_no_digit_count"):
            validate_input_pass._no_digit_count = 0
        validate_input_pass._no_digit_count += 1
        suspicious_flag = "Yes" if validate_input_pass._no_digit_count > 3 else "No"
        logger.log_entry(
            "system",
            "Password validation failed",
            "Password must contain at least one digit.",
            suspicious=suspicious_flag,
        )
        print("Password must contain at least one digit.")
        return False

    if not re.search(rf"[{allowed_special}]", value):
        logger = EncryptedLogger()
        if not hasattr(validate_input_pass, "_no_special_count"):
            validate_input_pass._no_special_count = 0
        validate_input_pass._no_special_count += 1
        suspicious_flag = "Yes" if validate_input_pass._no_special_count > 3 else "No"
        logger.log_entry(
            "system",
            "Password validation failed",
            "Password must contain at least one special character.",
            suspicious=suspicious_flag,
        )
        print("Password must contain at least one special character.")
        return False

    if "\x00" in value:
        logger = EncryptedLogger()
        if not hasattr(validate_input_pass, "_null_byte_count"):
            validate_input_pass._null_byte_count = 0
        validate_input_pass._null_byte_count += 1
        suspicious_flag = "Yes" if validate_input_pass._null_byte_count > 3 else "No"
        logger.log_entry(
            "system",
            "Password validation failed",
            "Null byte detected in input.",
            suspicious=suspicious_flag,
        )
        print("Null byte detected in input.")
        return False

    return value


def is_valid_email(email):
    if not isinstance(email, str):
        return False
    email = email.strip()
    # RFC 5322 Official Standard (simplified for practical use)
    pattern = (
        r"^(?![.-])"  # No leading dot or hyphen
        r"[A-Za-z0-9._%+-]+"  # Local part
        r"@"
        r"(?!-)"  # No leading hyphen in domain
        r"[A-Za-z0-9.-]+"  # Domain part
        r"\.[A-Za-z]{2,}$"  # TLD
    )
    if not re.fullmatch(pattern, email):
        return False
    if ".." in email:
        return False  # No consecutive dots allowed
    return email


def is_valid_license_number(license):
    pattern = r"^[A-Z0-9-]{5,20}$"
    return re.fullmatch(pattern, license) is not None


def sanitize_output(text):
    """Remove control characters (e.g., \x1b) from output."""
    return re.sub(r"[\x00-\x1f\x7f-\x9f]", "", str(text))
