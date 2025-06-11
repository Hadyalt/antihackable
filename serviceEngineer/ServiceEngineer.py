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