from DbContext.DbContext import DbContext

class Verification:
    def verify_UserName(self, username):
        if (username.Length < 8 or username.Length > 10):
            return False
        if (DbContext.get_User(username) is None):
            return False


    def resend_code(self):
        # Logic to resend verification code
        pass