from DbContext.DbContext import DbContext
from DbContext.crypto_utils import encrypt, decrypt, hash_password, verify_password
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
        hashed = hash_password(password)
        system_data = {
            "Username": encrypt(user_name),
            "Password": hashed,
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
        matching_users = [user for user in sysAdmins if decrypt(user[0]).lower() == username_to_update.lower()]
        if not matching_users:
            print(f"No system admin found with username '{username_to_update}'.")
            return
        print ("What do you want to update?")
        print(f"1. Username: ({username_to_update})")
        print(f"2. Password")
        choice = input("Enter your choice (1 or 2): ").strip()
        if choice == "1":
            new_username = input("Enter the new username: ").strip()
            if Verification.verify_username(new_username):
                self.set_new_username(username_to_update, new_username)
                print(f"System admin {username_to_update} updated to {new_username}.")
            else:
                print("Invalid username format. Please try again.")
        elif choice == "2":
            new_password = input("Enter the new password: ").strip()
            if Verification.verify_Password(new_password):
                hashed = hash_password(new_password)
                self.reset_password_function(username_to_update, hashed, "systemadmin")
                print(f"Password for system admin {username_to_update} has been updated.")
            else:
                print("Invalid password format. Please try again.")
        else:
            print("Invalid choice. Please try again.")
        
    def delete_system_admin(self):
        sysAdmins = self.view_all_system_admins()
        if not sysAdmins:
            print("No system admins available to delete.")
            return
        username_to_delete = input("Enter the username of the system admin you want to delete: ").strip()
        matching_users = [user for user in sysAdmins if decrypt(user[0]).lower() == username_to_delete.lower()]
        if not matching_users:
            print(f"No system admin found with username '{username_to_delete}'.")
            return
        connection = self.db_context.connect()
        if connection:
            cursor = connection.cursor()
            enc_username = encrypt(username_to_delete)
            cursor.execute("UPDATE User SET IsActive = 0 WHERE Username = ? AND Role = ?", (enc_username, "systemadmin"))
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
                    print(f"- {decrypt(user[0])}")
                return users
            else:
                print("No system admin accounts found.")
                return []
        else:
            print("No database connection.")
            return "Error"
    def view_all_service_engineers(self):
        connection = self.db_context.connect()
        if connection:
            cursor = connection.cursor()
            cursor.execute("SELECT Username FROM User WHERE Role = ? AND IsActive = 1", ("serviceengineer",))
            users = cursor.fetchall()
            
            if users:
                print(f"Retrieved {len(users)} service engineer(s):")
                for user in users:
                    print(f"- {user[0]}")
                return users
            else:
                print("No service engineer accounts found.")
                return []
        else:
            print("No database connection.")
            return "Error"
    def set_new_username(self, old_username, new_username):
        connection = self.db_context.connect()
        if connection:
            cursor = connection.cursor()
            enc_old = encrypt(old_username)
            enc_new = encrypt(new_username)
            cursor.execute("UPDATE User SET Username = ? WHERE Username = ? AND Role = ?", (enc_new, enc_old, "systemadmin"))
            connection.commit()
        else:
            print("Failed to connect to the database.")
    
    def reset_password_function(self, username, new_password, role):
        connection = self.db_context.connect()
        if connection:
            cursor = connection.cursor()
            enc_username = encrypt(username)
            cursor.execute(
                "UPDATE User SET Password = ?, ResettedPasswordCheck = 1 WHERE Username = ? AND Role = ?",
                (new_password, enc_username, role)
            )
            connection.commit()
        else:
            print("Failed to connect to the database.")

    def reset_password_sysadmin(self):
        sysAdmins = self.view_all_system_admins()
        if not sysAdmins:
            print("No system admins available to reset password.")
            return
        username_to_reset = input("Enter the username of the system admin whose password you want to reset: ").strip()

        # Check if the username exists in the sysAdmins list
        matching_users = [user for user in sysAdmins if user[0].lower() == username_to_reset.lower()]
        if not matching_users:
            print(f"No system admin found with username '{username_to_reset}'.")
            return

        new_password = input("Enter the new temporary password: ").strip()
        if Verification.verify_Password(new_password):
            hashed_password = Verification.hash_password(new_password)
            self.reset_password_function(username_to_reset, hashed_password, "systemadmin")
            print(f"Password for system admin {username_to_reset} has been reset.")
        else:
            print("Invalid password format. Please try again.")
    
    def reset_password_service_engineer(self):
        service_engineers = self.view_all_service_engineers()
        if not service_engineers:
            print("No service engineers available to reset password.")
            return
        username_to_reset = input("Enter the username of the service engineer whose password you want to reset: ").strip()

        # Check if the username exists in the service_engineers list
        matching_users = [user for user in service_engineers if user[0].lower() == username_to_reset.lower()]
        if not matching_users:
            print(f"No service engineer found with username '{username_to_reset}'.")
            return

        new_password = input("Enter the new temporary password: ").strip()
        if Verification.verify_Password(new_password):
            hashed_password = Verification.hash_password(new_password)
            self.reset_password_function(username_to_reset, hashed_password, "serviceengineer")
            print(f"Password for service engineer {username_to_reset} has been reset.")
        else:
            print("Invalid password format. Please try again.")