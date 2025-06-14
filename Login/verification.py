import hashlib
from DbContext.DbContext import DbContext
import re
from DbContext.crypto_utils import encrypt

class Verification:
    def hash_password(password):
        return hashlib.sha256(password.encode()).hexdigest()
    
    def check_username_exists(username):
        db = DbContext()
        connection = db.connect()
        """Retrieve a User record by username hash."""
        username_hash = hashlib.sha256(username.encode()).hexdigest()
        if connection:
            cursor = connection.cursor()
            cursor.execute("SELECT Username FROM User WHERE UsernameHash = ?", (username_hash,))
            user = cursor.fetchone()
            if user is not None:
                return user
            else:
                return None
        else:
            print("No database connection.")
            return "Error"
        
    def verify_username(username):
        db = DbContext()

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
        if Verification.check_username_exists(username) is not None:
            print("Username already exists in the database.")
            return False
        return True

    def verify_Password(password):
        # Check length constraints
        if len(password) < 12 or len(password) > 30:
            print("Password must be between 12 and 30 characters.")
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
        # Allow only letters, hyphens, apostrophes, and spaces
        if not re.fullmatch(r"[A-Za-zÀ-ÖØ-öø-ÿ'\- ]{1,50}", name):
            print("Invalid characters in name. Please use letters, hyphens (-), or apostrophes (').")
            return False
        return True
