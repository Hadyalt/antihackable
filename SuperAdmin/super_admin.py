
from DbContext.DbContext import DbContext
from Login.verification import Verification


class SuperAdmin:
    def __init__(self):
        self.db_context = DbContext()

    def create_system_admin(self):
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
            "Role": "systemadmin",
            "IsActive": 1
        }
        self.db_context.insert_User(system_data)
        return user_name
    
    def update_system_admin(self):
        sysAdmins = self.view_all_system_admins()
        if not sysAdmins:
            print("No system admins available to update.")
            return
        username_to_update = input("Enter the username of the system admin you want to update: ").strip()

        # Check if the username exists in the sysAdmins list
        matching_users = [user for user in sysAdmins if user[0] == username_to_update]
        if not matching_users:
            print(f"No system admin found with username '{username_to_update}'.")
            return
        print ("What do you want to update?")
        print(f"1. Username: ({username_to_update})")
        print(f"2. Password")
        choice = input("Enter your choice (1 or 2): ").strip()
        
    def delete_system_admin(self):
        sysAdmins = self.view_all_system_admins()
        if not sysAdmins:
            print("No system admins available to delete.")
            return
        username_to_delete = input("Enter the username of the system admin you want to delete: ").strip()

        # Check if the username exists in the sysAdmins list
        matching_users = [user for user in sysAdmins if user[0] == username_to_delete]  # assumes username is in column 0

        if not matching_users:
            print(f"No system admin found with username '{username_to_delete}'.")
            return

        connection = self.db_context.connect()
        if connection:
            cursor = connection.cursor()
            cursor.execute("UPDATE User SET IsActive = 0 WHERE Username = ? AND Role = ?", (username_to_delete, "systemadmin"))
            connection.commit()
            print(f"System admin '{username_to_delete}' has been deleted.")
        else:
            print("Failed to connect to the database.")
        

    def view_all_system_admins(self):
        connection = self.db_context.connect()
        if connection:
            cursor = connection.cursor()
            cursor.execute("SELECT Username FROM User WHERE Role = ? AND IsActive = 1", ("systemadmin",))
            users = cursor.fetchall()
            
            if users:
                print(f"Retrieved {len(users)} system admin(s):")
                for user in users:
                    print(user)
                return users
            else:
                print("No system admin accounts found.")
                return []
        else:
            print("No database connection.")
            return "Error"

        