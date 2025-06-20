from DbContext.DbContext import DbContext
from DbContext.crypto_utils import encrypt, decrypt, hash_password, verify_password
from DbContext.encrypted_logger import EncryptedLogger
from Login.verification import Verification
import getpass
from valid_in_out_put import validate_input_user, validate_input_pass


class systemAdmin:
    def __init__(self):
        self.db_context = DbContext()
    
    def get_username(self, username):
        users = self.view_all_users_no_print()
        if not users:
            print("No users found in the system.")
            return
        matching_users = [user for user in users if decrypt(user[0]).lower() == username.lower()]
        if not matching_users:
            print(f"No user found with username '{username}'.")
            return
        return matching_users[0][0]

    # check if the user has a reset password variable called ResettedPasswordCheck using only the username
    def check_reset_password(self, username, role):
        connection = self.db_context.connect()
        if connection:
            cursor = connection.cursor()
            cursor.execute("SELECT ResettedPasswordCheck FROM User WHERE Username = ? AND Role = ?", (username, role))
            result = cursor.fetchone()
            connection.close()
            if result is None:
                print(f"No user found with username '{username}'.")
                return None
            if result[0] == 1:
                return True
            elif result[0] == 0:
                return False
            else:
                print(f"No user found with username '{username}'.")
                return None

    def reset_resetted_password_check(self, username, role):
        connection = self.db_context.connect()
        if connection:
            cursor = connection.cursor()
            cursor.execute("UPDATE User SET ResettedPasswordCheck = 0 WHERE Username = ? AND Role = ?", (username, role))
            connection.commit()
            connection.close()
            
        else:
            print("Failed to connect to the database.")

    def create_service_engineer(self, creator):
        verified_username = False
        while not verified_username:
            verified_username, user_name = validate_input_user(input("Enter username: ").strip())
            verified_username = Verification.verify_username(user_name)
        verified_password = False
        while not verified_password:
            password = validate_input_pass(getpass.getpass("Enter password: "))
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
            "Role": "serviceengineer",
            "IsActive": 1
        }
        self.db_context.insert_User(system_data)
        logger = EncryptedLogger()
        logger.log_entry(f"{creator}", "Created Service Engineer Account", f"username: {user_name}", "No")
        return user_name
    
    def view_all_users(self, viewer):
        connection = self.db_context.connect()
        if connection:
            cursor = connection.cursor()
            cursor.execute("SELECT Username, Role FROM User WHERE IsActive = 1")
            users = cursor.fetchall()
            if users:
                print("\nAll User Accounts:")
                for user in users:
                    print(f"- {decrypt(user[0])} ({user[1]})")
            else:
                print("No user accounts found.")
            connection.close()
        else:
            print("Failed to connect to the database.")
        logger = EncryptedLogger()
        logger.log_entry(f"{viewer}", "Viewed all users", f" ", "No")
        return users

    def view_all_users_no_print(self):
        connection = self.db_context.connect()
        if connection:
            cursor = connection.cursor()
            cursor.execute("SELECT Username, Role FROM User WHERE IsActive = 1")
            users = cursor.fetchall()
            if users:
                return users
            else:
                print("No user accounts found.")
            connection.close()
        else:
            print("Failed to connect to the database.")
    
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
        
    def update_service_engineer(self, updater):
        servEng = self.view_all_service_engineers()
        if not servEng:
            print("No service engineers available to update.")
            return
        username_to_update = input("Enter the username of the service engineer you want to update: ").strip().lower()

        # Check if the username exists in the servEng list
        matching_users = [user for user in servEng if decrypt(user[0]).lower() == username_to_update]
        if not matching_users:
            print(f"No service engineer found with username '{username_to_update}'.")
            return
        print ("What do you want to update?")
        print(f"1. Update Username: ({decrypt(matching_users[0][0])})")
        print("2. Reset Password")
        print("3. Update First Name")
        print("4. Update Last Name")
        print("5. Go Back")
        choice = input("Enter your choice (1, 2, 3, 4 or 5): ").strip()
        if choice == "1":
            if (self.confirm_password(updater)):
                new_username = input("Enter the new username: ").strip()
                if Verification.verify_username(new_username):
                    self.set_new_username(matching_users[0][0], new_username)
                    print(f"Service Engineer {decrypt(matching_users[0][0])} updated to {new_username}.")
                    logger = EncryptedLogger()
                    logger.log_entry(f"{updater}", "Updated Service Engineer Username", f"Old: {decrypt(matching_users[0][0])}, New: {new_username}", "No")
                else:
                    print("Invalid username format. Please try again.")
            else:
                logger = EncryptedLogger()
                logger.log_entry(f"{updater}", "Too many wrong password attempts", f"Could not confirm his own identity", "Yes")
                from um_members import pre_login_menu
                pre_login_menu()
        elif choice == "2":
            if (self.confirm_password(updater)):
                new_password = getpass.getpass("Enter the new password: ").strip()
                if Verification.verify_Password(new_password):
                    hashed = hash_password(new_password)
                    self.reset_password_function(matching_users[0][0], hashed, "serviceengineer")
                    print(f"Password for service engineer {decrypt(matching_users[0][0])} has been updated.")
                    logger = EncryptedLogger()
                    logger.log_entry(f"{updater}", "Reset Service Engineer Password", f"Username: {decrypt(matching_users[0][0])} had their password reset ", "No")
                else:
                    print("Invalid password format. Please try again.")
            else:
                logger = EncryptedLogger()
                logger.log_entry(f"{updater}", "Too many wrong password attempts", f"Could not confirm his own identity", "Yes")
                from um_members import pre_login_menu
                pre_login_menu()
        elif choice == "3":
            new_first_name = input("Enter the new first name: ").strip()
            if Verification.verify_name(new_first_name):
                self.set_new_first_name(matching_users[0][0], new_first_name)
                print(f"First name for service engineer {decrypt(matching_users[0][0])} has been updated to {new_first_name}.")
                logger = EncryptedLogger()
                logger.log_entry(f"{updater}", "Updated Service Engineer First Name", f"New First Name: {new_first_name}", "No")
        elif choice == "4":
            new_last_name = input("Enter the new last name: ").strip()
            if Verification.verify_name(new_last_name):
                self.set_new_last_name(matching_users[0][0], new_last_name)
                print(f"Last name for service engineer {decrypt(matching_users[0][0])} has been updated to {new_last_name}.")
                logger = EncryptedLogger()
                logger.log_entry(f"{updater}", "Updated Service Engineer Last Name", f"New Last Name: {new_last_name}", "No")
        elif choice == "5":
            print("Going back to the previous menu.")
            return
        else:
            print("Invalid choice. Please try again.")
    
    def delete_service_engineer(self, deletor): 
        servEng = self.view_all_service_engineers()
        if not servEng:
            print("No service engineers available to delete.")
            return
        username_to_delete = input("Enter the username of the service engineer you want to delete: ").strip()

        # Check if the username exists in the servEng list
        matching_users = [user for user in servEng if decrypt(user[0]).lower() == username_to_delete.lower()]  # assumes username is in column 0
        if not matching_users:
            print(f"No service engineer found with username '{username_to_delete}'.")
            return
        if self.confirm_password(deletor):
            connection = self.db_context.connect()
            if connection:
                cursor = connection.cursor()
                enc_username = matching_users[0][0]
                cursor.execute("DELETE FROM User WHERE Username = ? AND Role = ?", (enc_username, "serviceengineer"))
                connection.commit()
                print(f"service engineer '{decrypt(matching_users[0][0])}' has been deleted.")
                logger = EncryptedLogger()
                logger.log_entry(f"{deletor}", "Deleted a Service Engineer Account", f"username: {decrypt(matching_users[0][0])} is deleted", "No")
            else:
                print("Failed to connect to the database.")
        else:
            logger = EncryptedLogger()
            logger.log_entry(f"{deletor}", "Too many wrong password attempts", f"Could not confirm his own identity", "Yes")
            from um_members import pre_login_menu
            pre_login_menu()
    
    def delete_account(self, username):
        connection = self.db_context.connect()
        if connection:
            cursor = connection.cursor()
            cursor.execute("DELETE FROM User WHERE Username = ? AND Role = ?", (username, "systemadmin"))
            connection.commit()
            return True
        else:
            print("Failed to connect to the database.")
            return False

    def set_new_username(self, old_username, new_username):
        connection = self.db_context.connect()
        if connection:
            cursor = connection.cursor()
            enc_new = encrypt(new_username)
            cursor.execute("UPDATE User SET Username = ? WHERE LOWER(Username) = LOWER(?) AND Role = ?", (enc_new, old_username, "serviceengineer"))
            connection.commit()
            return True
        else:
            print("Failed to connect to the database.")
            return False
    
    def set_new_username_system(self, old_username, new_username):
        connection = self.db_context.connect()
        if connection:
            cursor = connection.cursor()
            enc_username = encrypt(new_username)
            cursor.execute("UPDATE User SET Username = ? WHERE LOWER(Username) = LOWER(?) AND Role = ?", (enc_username, old_username, "systemadmin"))
            connection.commit()
            return True
        else:
            print("Failed to connect to the database.")
            return False
    
    def set_new_first_name(self, username, new_first_name):
        connection = self.db_context.connect()
        if connection:
            cursor = connection.cursor()
            enc_first_name = encrypt(new_first_name)
            cursor.execute("UPDATE User SET FirstName = ? WHERE Username = ? AND Role = ?", (enc_first_name, username, "serviceengineer"))
            connection.commit()
        else:
            print("Failed to connect to the database.")
    
    def set_new_last_name(self, username, new_last_name):
        connection = self.db_context.connect()
        if connection:
            cursor = connection.cursor()
            enc_last_name = encrypt(new_last_name)
            cursor.execute("UPDATE User SET LastName = ? WHERE Username = ? AND Role = ?", (enc_last_name, username, "serviceengineer"))
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
    
    def reset_password_system(self, username, new_password):
        connection = self.db_context.connect()
        if connection:
            cursor = connection.cursor()
            cursor.execute("UPDATE User SET Password = ? WHERE LOWER(Username) = LOWER(?) AND Role = ?", (new_password, username, "systemadmin"))
            connection.commit()
            return True
        else:
            print("Failed to connect to the database.")
            return False

    def reset_password_service_engineer(self, resetter):
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

        new_password = getpass.getpass("Enter the new temporary password: ").strip()
        if Verification.verify_Password(new_password):
            hashed_password = hash_password(new_password)
            self.reset_password_function(username_to_reset, hashed_password, "serviceengineer")
            print(f"Password for service engineer {username_to_reset} has been reset.")
            logger = EncryptedLogger()
            logger.log_entry(f"{resetter}", "Resetted the password of a Service Engineer Account", f"username: {username_to_reset} had his password reset", "No")
        else:
            print("Invalid password format. Please try again.")
 
    def confirm_password(self, username):
        tries = 0
        max_tries = 3
        if username.lower() == "super_admin":
            while tries < max_tries:
                password = getpass.getpass("Enter your password: ")
                if password == "Admin_123?":
                    return True
                else:
                    tries += 1
                    print(f"Incorrect password. You have {max_tries - tries} tries left.")
            return False
        else:
            while tries < max_tries:
                all_users = self.view_all_users_no_print()
                if not all_users:
                    print("No users found in the system.")
                    tries += 1
                    print(f"Incorrect password. You have {max_tries - tries} tries left.")
                    continue
                matching_users = [user for user in all_users if decrypt(user[0]).lower() == username.lower()]
                if not matching_users:
                    print(f"No user found with username '{username}'.")
                    tries += 1
                    print(f"Incorrect password. You have {max_tries - tries} tries left.")
                    continue
                password = getpass.getpass("Enter your current password: ")
                if not password:
                    tries += 1
                    print(f"Incorrect password. You have {max_tries - tries} tries left.")
                    continue
                hashed_password_database = self.get_hashed_password(matching_users[0][0])
                if not hashed_password_database:
                    tries += 1
                    print(f"Incorrect password. You have {max_tries - tries} tries left.")
                    continue
                if verify_password(password, hashed_password_database):
                    return True
                else:
                    tries += 1
                    print(f"Incorrect password. You have {max_tries - tries} tries left.")
            return False  
    
    def get_hashed_password(self, username):
        connection = self.db_context.connect()
        if connection:
            cursor = connection.cursor()
            cursor.execute("SELECT Password FROM User WHERE Username = ?", (username, ))
            result = cursor.fetchone()
            connection.close()
            if result:
                return result[0]
            else:
                print(f"No user found with username '{username}'.")
                return None
        else:
            print("Failed to connect to the database.")
            return None



