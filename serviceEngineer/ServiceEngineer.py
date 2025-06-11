from DbContext.DbContext import DbContext

class ServiceEngineer:
    def __init__(self):
        self.db_context = DbContext()

    def reset_password(self, username, new_password):

        connection = self.db_context.connect()
        if connection:
            cursor = connection.cursor()
            cursor.execute(
                "UPDATE User SET Password = ? WHERE Username = ? AND Role = ?",
                (new_password, username, "serviceengineer")
            )
            connection.commit()
        else:
            print("Failed to connect to the database.")