from DbContext.DbContext import DbContext
from DbContext.crypto_utils import encrypt, decrypt, hash_password, verify_password
from Login.verification import Verification
from systemAdmin.system_admin import systemAdmin

class ServiceEngineer:
    def __init__(self):
        self.db_context = DbContext()
        self.sysAd = systemAdmin()

    def reset_password(self, username, password):
        user = self.sysAd.get_username(username)
        connection = self.db_context.connect()
        if connection:
            cursor = connection.cursor()
            hashed = hash_password(password)
            enc_username = user
            cursor.execute(
                "UPDATE User SET Password = ? WHERE Username = ? AND Role = ?",
                (hashed, enc_username, "serviceengineer")
            )
            connection.commit()
        else:
            print("Failed to connect to the database.")
    
    def check_reset_password(self, username):
        connection = self.db_context.connect()
        if connection:
            cursor = connection.cursor()
            enc_username = encrypt(username)
            cursor.execute(
                "SELECT ResettedPasswordCheck FROM User WHERE Username = ? AND Role = ?",
                (enc_username, "serviceengineer")
            )
            result = cursor.fetchone()
            if result:
                return result[0] == 1
            else:
                print("No user found with the given username.")
                return False
        else:
            print("Failed to connect to the database.")
            return False
    
    def reset_resetted_password_check(self, username):
        connection = self.db_context.connect()
        if connection:
            cursor = connection.cursor()
            enc_username = encrypt(username)
            cursor.execute(
                "UPDATE User SET ResettedPasswordCheck = 0 WHERE Username = ? AND Role = ?",
                (enc_username, "serviceengineer")
            )
            connection.commit()
        else:
            print("Failed to connect to the database.")