from datetime import datetime
import hashlib
from DbContext.DbContext import DbContext
import re
from DbContext.crypto_utils import decrypt, encrypt


class Verification:   
    def check_username_exists_simple(username):
        db = DbContext()
        connection = db.connect()
        if connection:
            cursor = connection.cursor()
            cursor.execute("SELECT Username, Role FROM User WHERE IsActive = 1")
            all_users = cursor.fetchall()
        else:
            print("Failed to connect to the database.")
            return "error"

        matching_users = [user for user in all_users if decrypt(user[0]).lower() == username]
        if not matching_users:
            return None
        else:
            return matching_users[0]
        
    def verify_username(username):
        username = username.lower()

        # Check if username is empty
        if username is None or username.strip() == "":
            print("Username cannot be empty.")
            return False

        # Check length constraints
        if len(username) < 8 or len(username) > 10:
            print("Username must be between 8 and 10 characters.")
            return False

        # Check if it starts with a letter or underscore
        if not re.match(r'^[a-z_]', username):
            print("Username must start with a letter or underscore.")
            return False

        # Check for allowed characters only
        if not re.match(r'^[a-z0-9_\'\.]+$', username):
            print("Username can only contain lowercase letters, digits, underscores, apostrophes, and periods.")
            return False

        # Check uniqueness in the database (assumes case-insensitive uniqueness)
        if Verification.check_username_exists_simple(username) is not None:
            print("Username already exists in the database.")
            return False
        return True

    def verify_Password(password):
        # Check length constraints
        if len(password) < 12 or len(password) > 30:
            print("Password must be between 12 and 30 characters.")
            return False
        
        # Check if password is empty
        if password is None or password.strip() == "":
            print("Password cannot be empty.")
            return False

        # Define allowed characters
        allowed_chars = r"^[a-zA-Z0-9~!@#$%&_+=`|\(){}\[\]:;'<>,\.?/]*$"
        if not re.match(allowed_chars, password):
            print("Password can only contain letters, digits, and special characters.")
            return False

        # Check for at least one lowercase, one uppercase, one digit, and one special character
        if not re.search(r'[a-z]', password):
            print("Password must contain at least one lowercase letter.")
            return False
        if not re.search(r'[A-Z]', password):
            print("Password must contain at least one uppercase letter.")
            return False
        if not re.search(r'[0-9]', password):
            print("Password must contain at least one digit.")
            return False
        if not re.search(r'[~!@#$%&_+=`|\(){}\[\]:;\'<>,\.?/]', password):
            print("Password must contain at least one special character.")
            return False
        return True

    def verify_name(name):
        if not name:
            print("Name cannot be empty.")
            return False
        # Control characters (null byte, tabs, etc.)
        if any(ord(c) < 32 or ord(c) == 127 for c in name):
            return False
        # Allow only letters, hyphens, apostrophes, and spaces
        if not re.fullmatch(r"[A-Za-zÀ-ÖØ-öø-ÿ'\- ]{1,50}", name):
            print("Invalid characters in name. Please use letters, hyphens (-), or apostrophes (').")
            return False
        return True
    
    def is_valid_birthday(birthday_str):
        try:
            birthday = datetime.strptime(birthday_str, "%Y-%m-%d")
            today = datetime.today()

            # Birthday should not be in the future or unrealistically old
            if birthday > today:
                return False
            if birthday.year < 1900:
                return False

            return True
        except ValueError:
            return False

    def is_valid_street_name(street: str) -> bool:
        # Reject empty or whitespace-only
        if not street:
            return False

        # Control characters (null byte, tabs, etc.)
        if any(ord(c) < 32 or ord(c) == 127 for c in street):
            return False

        # ASCII only (no Unicode)
        try:
            street.encode('ascii')
        except UnicodeEncodeError:
            return False

        # Allow only specific characters
        if not re.fullmatch(r"[A-Za-z0-9 .'-]+", street):
            return False

        # Must contain at least one letter
        if not re.search(r"[A-Za-z]", street):
            return False
        return True


