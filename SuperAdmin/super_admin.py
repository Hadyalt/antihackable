
from DbContext.DbContext import DbContext
from Login.verification import Verification


class SuperAdmin:
    def __init__(self):
        self.db_context = DbContext()

    def create_system_admin(self, user_name, password):
        system_data = {
            "Username": user_name,
            "Password": password,
            "Role": "systemadmin",
            "IsActive": 1
        }
        self.db_context.insert_User(system_data)
        

    def delete_user(self, user_id):
        print(f"User with ID {user_id} deleted.")

    def view_all_users(self):
        print("Displaying all users.")