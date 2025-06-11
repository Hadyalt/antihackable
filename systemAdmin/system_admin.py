from DbContext.DbContext import DbContext
from Login.verification import Verification


class systemAdmin:
    def __init__(self):
        self.db_context = DbContext()
    
    def create_service_engineer(self):
        verified_username = False
        while not verified_username:
            user_name = input("Enter username: ")
            verified_username = Verification.verify_username(user_name)
        verified_password = False
        while not verified_password:
            password = input("Enter password: ")
            verified_password = Verification.verify_Password(password)
        hashed_password = Verification.hash_password(password)
        system_data = {
            "Username": user_name,
            "Password": hashed_password,
            "Role": "serviceengineer",
            "IsActive": 1
        }
        self.db_context.insert_User(system_data)
        return user_name
    
    def view_all_users(self):
        connection = self.db_context.connect()
        if connection:
            cursor = connection.cursor()
            cursor.execute("SELECT Username, Role FROM User WHERE IsActive = 1")
            users = cursor.fetchall()
            if users:
                print("\nAll User Accounts:")
                for user in users:
                    print(f"Username: {user[0]}, Role: {user[1]}")
            else:
                print("No user accounts found.")
            connection.close()
        else:
            print("No database connection.")
        return