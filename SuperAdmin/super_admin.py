import hashlib
from DbContext.DbContext import DbContext
from DbContext.crypto_utils import encrypt, decrypt, hash_password, verify_password
from DbContext.encrypted_logger import EncryptedLogger
from Login.verification import Verification
from valid_in_out_put import validate_input_pass,validate_input_user


class SuperAdmin:
    def __init__(self):
        self.db_context = DbContext()

    def create_system_admin(self):
        verified_username = False
        while not verified_username:
            user_name = validate_input_user(input("Enter username: ").strip())
            verified_username = Verification.verify_username(user_name)
        verified_password = False
        while not verified_password:
            password = validate_input_pass(input("Enter password: "))
            verified_password = Verification.verify_Password(password)
        verified_first_name = False
        while not verified_first_name:
            firstname = input("Enter first name: ")
            verified_first_name = Verification.verify_name(firstname)
        verified_last_name = False
        while not verified_last_name:
            lastname = input("Enter last name: ")
            verified_last_name = Verification.verify_name(lastname)

        hashed = hash_password(password)
        system_data = {
            "Username": user_name,
            "Password": hashed,
            "FirstName": encrypt(firstname),
            "LastName": encrypt(lastname),
            "Role": "systemadmin",
            "IsActive": 1
        }
        self.db_context.insert_User(system_data)
        logger = EncryptedLogger()
        logger.log_entry("super_admin", "Created System Admin Account", f"username: {user_name}", "No")
        return user_name
    
    def update_system_admin(self):
        sysAdmins = self.view_all_system_admins()
        if not sysAdmins:
            print("No system admins available to update.")
            return
        username_to_update = input("Enter the username of the system admin you want to update: ").strip().lower()
        matching_users = [user for user in sysAdmins if decrypt(user[0]).lower() == username_to_update]
        if not matching_users:
            print(f"No system admin found with username '{username_to_update}'.")
            return
        print ("What do you want to do")
        print(f"1. Update Username: ({decrypt(matching_users[0][0])})")
        print("2. Reset Password")
        print("3. Update First Name")
        print("4. Update Last Name")
        print("5. Go Back")
        choice = input("Enter your choice (1, 2, 3, 4 or 5): ").strip()
        if choice == "1":  
            if self.confirm_password():  
                new_username = input("Enter the new username: ").strip()
                if Verification.verify_username(new_username):
                    self.set_new_username(matching_users[0][0], new_username)
                    print(f"System admin {decrypt(matching_users[0][0])} updated to {new_username}.")
                    logger = EncryptedLogger()
                    logger.log_entry("super_admin", "Updated System Admin Username", f"Old: {decrypt(matching_users[0][0])}, New: {new_username}", "No")
                else:
                    print("Invalid username format. Please try again.")
            else:
                print("Incorrect password. Update cancelled.")
                return
        elif choice == "2":
            if self.confirm_password():
                new_password = input("Enter the new password: ").strip()
                if Verification.verify_Password(new_password):
                    hashed = hash_password(new_password)
                    self.reset_password_function(matching_users[0][0], hashed, "systemadmin")
                    print(f"Password for system admin {decrypt(matching_users[0][0])} has been updated.")
                    logger = EncryptedLogger()
                    logger.log_entry("super_admin", "Reset System Admin Password", f"Username: {decrypt(matching_users[0][0])} had their password reset ", "No")
                else:
                    print("Invalid password format. Please try again.")
            else:
                print("Incorrect password. Reset cancelled.")
                return
        elif choice == "3":
            new_first_name = input("Enter the new first name: ").strip()
            if Verification.verify_name(new_first_name):
                self.set_new_first_name(matching_users[0][0], new_first_name)
                print(f"First name for system admin {decrypt(matching_users[0][0])} has been updated to {new_first_name}.")
                logger = EncryptedLogger()
                logger.log_entry("super_admin", "Updated System Admin First Name", f"New First Name: {new_first_name}", "No")
        elif choice == "4":
            new_last_name = input("Enter the new last name: ").strip()
            if Verification.verify_name(new_last_name):
                self.set_new_last_name(matching_users[0][0], new_last_name)
                print(f"Last name for system admin {decrypt(matching_users[0][0])} has been updated to {new_last_name}.")
                logger = EncryptedLogger()
                logger.log_entry("super_admin", "Updated System Admin Last Name", f"New Last Name: {new_last_name}", "No")
        elif choice == "5":
            print("Going back to the previous menu.")
            return
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
            enc_username = matching_users[0][0]
            cursor.execute("UPDATE User SET IsActive = 0 WHERE Username = ? AND Role = ?", (enc_username, "systemadmin"))
            connection.commit()
            print(f"System admin '{decrypt(matching_users[0][0])}' has been deleted.")
            logger = EncryptedLogger()
            logger.log_entry("super_admin", "Deleted System Admin Account", f"Username: {decrypt(matching_users[0][0])} is deleted" , "No")
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
                    print(f"- {decrypt(user[0])}")
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
            enc_new = encrypt(new_username)
            cursor.execute("UPDATE User SET Username = ? WHERE Username = ? AND Role = ?", (enc_new, old_username, "systemadmin"))
            connection.commit()
        else:
            print("Failed to connect to the database.")
    
    def set_new_first_name(self, username, new_first_name):
        connection = self.db_context.connect()
        if connection:
            cursor = connection.cursor()
            enc_first_name = encrypt(new_first_name)
            cursor.execute("UPDATE User SET FirstName = ? WHERE Username = ? AND Role = ?", (enc_first_name, username, "systemadmin"))
            connection.commit()
        else:
            print("Failed to connect to the database.")
    
    def set_new_last_name(self, username, new_last_name):
        connection = self.db_context.connect()
        if connection:
            cursor = connection.cursor()
            enc_last_name = encrypt(new_last_name)
            cursor.execute("UPDATE User SET LastName = ? WHERE Username = ? AND Role = ?", (enc_last_name, username, "systemadmin"))
            connection.commit()
        else:
            print("Failed to connect to the database.")
    
    def reset_password_function(self, username, new_password, role):
        connection = self.db_context.connect()
        if connection:
            cursor = connection.cursor()
            cursor.execute(
                "UPDATE User SET Password = ?, ResettedPasswordCheck = 1 WHERE Username = ? AND Role = ?",
                (new_password, username, role)
            )
            connection.commit()
        else:
            print("Failed to connect to the database.")
    
    def activate_inactive_account(self):
        connection = self.db_context.connect()
        if not connection:
            print("No database connection.")
            return
        cursor = connection.cursor()
        cursor.execute("SELECT Username, Role FROM User WHERE IsActive = 0")
        users = cursor.fetchall()
        if not users:
            print("No inactive accounts found.")
            return
        print("\nInactive Accounts:")
        for idx, user in enumerate(users, 1):
            print(f"[{idx}] Username: {decrypt(user[0])}, Role: {user[1]}")
        try:
            choice = int(input("Enter the number of the account to activate: ").strip())
            if 1 <= choice <= len(users):
                username = users[choice-1][0]
                cursor.execute("UPDATE User SET IsActive = 1 WHERE Username = ?", (username,))
                connection.commit()
                print(f"Account '{decrypt(username)}' has been activated.")
                logger = EncryptedLogger()
                logger.log_entry("super_admin", "Activated Account", f"Username: {decrypt(username)} activated", "No")
            else:
                print("Invalid selection.")
        except ValueError:
            print("Invalid input. Please enter a number.")

    def confirm_password(self):
        password = input("Enter your current password: ")
        if (password == "Admin_123?"):
            return True
        else:
            return False
