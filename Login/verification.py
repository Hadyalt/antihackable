from DbContext.DbContext import DbContext
import re

class Verification:
    def verify_UserName(username):
        username = username.lower()

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
        if DbContext.get_User(username) is not None:
            print("Username already exists in the database.")
            return False
        return True

    def verify_Password(password):
        # Check length constraints
        if len(password) < 12 or len(password) > 30:
            return False

        # Define allowed characters
        allowed_chars = r"^[a-zA-Z0-9~!@#$%&_+=`|\(){}\[\]:;'<>,\.?/]*$"
        if not re.match(allowed_chars, password):
            return False

        # Check for at least one lowercase, one uppercase, one digit, and one special character
        if not re.search(r'[a-z]', password):
            return False
        if not re.search(r'[A-Z]', password):
            return False
        if not re.search(r'[0-9]', password):
            return False
        if not re.search(r'[~!@#$%&_+=`|\(){}\[\]:;\'<>,\.?/]', password):
            return False

        return True