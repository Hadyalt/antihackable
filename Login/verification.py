from DbContext.DbContext import DbContext
import re

class Verification:
    def verify_UserName(self, username):
        username = username.lower()

        # Check length constraints
        if len(username) < 8 or len(username) > 10:
            return False

        # Check if it starts with a letter or underscore
        if not re.match(r'^[a-z_]', username):
            return False

        # Check for allowed characters only
        if not re.match(r'^[a-z0-9_\'\.]+$', username):
            return False

        # Check uniqueness in the database (assumes case-insensitive uniqueness)
        if DbContext.get_User(username) is not None:
            return False
        return True

    def resend_code(self):
        # Logic to resend verification code
        pass