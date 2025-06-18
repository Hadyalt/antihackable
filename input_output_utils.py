import re
import logging

# Set up a basic logger for suspicious input attempts
logging.basicConfig(filename='logs.txt', level=logging.WARNING, format='%(asctime)s %(levelname)s: %(message)s')

def validate_input(value, pattern=None, min_length=None, max_length=None, value_type=None, allowed_values=None, context=None):
    """
    Central input validation function.
    - pattern: regex pattern to match
    - min_length, max_length: length constraints
    - value_type: type to cast (int, float, etc.)
    - allowed_values: whitelist of allowed values
    - context: string describing the input context for logging
    Returns the validated value or raises ValueError.
    """
    if value is None or (isinstance(value, str) and value.strip() == ""):
        log_suspicious_input(value, context or "Empty input")
        raise ValueError("Input cannot be empty.")
    if min_length and len(value) < min_length:
        log_suspicious_input(value, context or "Too short")
        raise ValueError(f"Input too short (min {min_length}).")
    if max_length and len(value) > max_length:
        log_suspicious_input(value, context or "Too long")
        raise ValueError(f"Input too long (max {max_length}).")
    if pattern and not re.fullmatch(pattern, value):
        log_suspicious_input(value, context or f"Pattern mismatch: {pattern}")
        raise ValueError("Input does not match required format.")
    if allowed_values and value not in allowed_values:
        log_suspicious_input(value, context or "Not in allowed values")
        raise ValueError("Input not allowed.")
    if value_type:
        try:
            value = value_type(value)
        except Exception:
            log_suspicious_input(value, context or f"Type cast failed: {value_type}")
            raise ValueError(f"Input must be of type {value_type}.")
    if '\x00' in value:
        log_suspicious_input(value, context or "Null byte detected")
        raise ValueError("Null byte detected in input.")
    return value

def is_valid_email(email):
    pattern = r"^[\w\.-]+@[\w\.-]+\.\w{2,}$"
    return re.fullmatch(pattern, email) is not None

def is_valid_license_number(license):
    pattern = r"^[A-Z0-9-]{5,20}$"
    return re.fullmatch(pattern, license) is not None

def sanitize_output(text):
    """Remove control characters (e.g., \x1b) from output."""
    return re.sub(r"[\x00-\x1f\x7f-\x9f]", "", str(text))

def log_suspicious_input(value, context):
    logging.warning(f"Suspicious input: {repr(value)} | Context: {context}")
