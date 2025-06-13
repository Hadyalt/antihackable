from DbContext.DbContext import DbContext
from Login.verification import Verification

class ServiceEngineer:
    def __init__(self):
        self.db_context = DbContext()

    def reset_password(self, username, password):

        connection = self.db_context.connect()
        if connection:
            cursor = connection.cursor()
            hashed_password = Verification.hash_password(password)
            cursor.execute(
                "UPDATE User SET Password = ? WHERE Username = ? AND Role = ?",
                (hashed_password, username, "serviceengineer")
            )
            connection.commit()
        else:
            print("Failed to connect to the database.")
    
    def check_reset_password(self, username):
        connection = self.db_context.connect()
        if connection:
            cursor = connection.cursor()
            cursor.execute(
                "SELECT ResettedPasswordCheck FROM User WHERE LOWER(Username) = LOWER(?) AND Role = ?",
                (username, "serviceengineer")
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
            cursor.execute(
                "UPDATE User SET ResettedPasswordCheck = 0 WHERE LOWER(Username) = LOWER(?) AND Role = ?",
                (username, "serviceengineer")
            )
            connection.commit()
        else:
            print("Failed to connect to the database.")