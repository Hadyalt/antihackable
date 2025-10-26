from sqlite3 import OperationalError
import sqlite3
from DbContext.DbContext import DbContext
from DbContext.crypto_utils import encrypt, decrypt, hash_password, verify_password
from DbContext.encrypted_logger import EncryptedLogger
import getpass
from datetime import datetime
from valid_in_out_put import validate_input_username, validate_input_pass, validate_username
from validation.isValidName import is_valid_name


class SuperAdmin:
    def __init__(self):
        self.db_context = DbContext()

    def create_system_admin(self):
        verified_username = False
        while not verified_username:
            verified_username, user_name = validate_input_username(input("Enter username: "))
            if not verified_username:
                print("Invalid username or already exists. Please try again.")
        
        verified_password = False
        while not verified_password:
            verified_password, password = validate_input_pass(getpass.getpass("Enter password: "))
            if not verified_password:
                print("Invalid password. Please try again.")
        
        verified_first_name = False
        while not verified_first_name:
            firstname = input("Enter first name: ")
            verified_first_name = is_valid_name(firstname)
            if not verified_first_name:
                print("Invalid first name. Please try again.")
        
        verified_last_name = False
        while not verified_last_name:
            lastname = input("Enter last name: ")
            verified_last_name = is_valid_name(lastname)
            if not verified_last_name:
                print("Invalid last name. Please try again.")

        hashed = hash_password(password)
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        system_data = {
            "Username": encrypt(user_name),
            "Password": hashed,
            "FirstName": encrypt(firstname),
            "LastName": encrypt(lastname),
            "RegistrationDate": encrypt(current_time),
            "ResettedPasswordCheck": encrypt("1"),
            "Role": encrypt("systemadmin"),
            "IsActive": encrypt("1")
        }

        self.db_context.insert_User(system_data)
        logger = EncryptedLogger()
        logger.log_entry("super_admin", "Created System Admin Account", f"username: {user_name}", "No")
        return user_name

    
    def update_system_admin(self):
        try:
            sysAdmins = self.view_all_system_admins()
            if not sysAdmins:
                print("No system admins available to update.")
                return
            is_valid, username_to_update = validate_username(input("Enter the username of the system admin you want to update: "))
            if not is_valid:
                print("Invalid username format.")
                return
            matching_users = [user for user in sysAdmins if decrypt(user[0]).lower() == username_to_update.lower()]
            if not matching_users:
                print(f"No system admin found with username '{username_to_update}'.")
                return
            print ("What do you want to do")
            print(f"1. Update Username: ({decrypt(matching_users[0][0])})")
            print("2. Reset Password")
            print("3. Update First Name")
            print("4. Update Last Name")
            print("5. Go Back")
            choice = input("Enter your choice (1, 2, 3, 4 or 5): ")
            if choice == "1":  
                if self.confirm_password():
                    tries = 0
                    while tries < 3:
                        new_username = input("Enter the new username: ")
                        verified, new_username = validate_input_username(new_username)
                        if verified:
                            self.set_new_username(matching_users[0][0], new_username)
                            print(f"System admin {decrypt(matching_users[0][0])} updated to {new_username}.")
                            logger = EncryptedLogger()
                            logger.log_entry("super_admin", "Updated System Admin Username", f"Old: {decrypt(matching_users[0][0])}, New: {new_username}", "No")
                            break
                        else:
                            print("Invalid username format or already exists.")
                            tries += 1
                            print(f"You have {3 - tries} tries left.")
                    if tries == 3:
                        print("Failed to reset password after 3 invalid attempts.")
                        logger = EncryptedLogger()
                        logger.log_entry("super_admin", "Tried to update with wrong format 3 times", f" ", "Yes")
                else:
                    logger = EncryptedLogger()
                    logger.log_entry(f"super_admin", "Too many wrong password attempts", f"Could not confirm his own identity", "Yes")
                    from um_members import pre_login_menu
                    pre_login_menu()
            elif choice == "2":
                if self.confirm_password():
                    tries = 0
                    while tries < 3:
                        password = getpass.getpass("Enter new password: ")
                        verified_password, password = validate_input_pass(password)
                        if verified_password:
                            hashed = hash_password(password)
                            self.reset_password_function(matching_users[0][0], hashed)
                            print(f"Password for system admin {decrypt(matching_users[0][0])} has been updated.")
                            logger = EncryptedLogger()
                            logger.log_entry("super_admin", "Reset System Admin Password", f"Username: {decrypt(matching_users[0][0])} had their password reset ", "No")
                            break
                        else:
                            print("Invalid password format.")
                            tries += 1
                            print(f"You have {3 - tries} tries left.")
                    if tries == 3:
                        print("Failed to reset password after 3 invalid attempts.")
                        logger = EncryptedLogger()
                        logger.log_entry("super_admin", "Failed System Admin Password Reset", f"Username: {decrypt(matching_users[0][0])} - 3 invalid password attempts", "Yes")
                else:
                    logger = EncryptedLogger()
                    logger.log_entry(f"super_admin", "Too many wrong password attempts", f"Could not confirm his own identity", "Yes")
                    from um_members import pre_login_menu
                    pre_login_menu()
            elif choice == "3":
                tries = 0
                while tries < 3:
                    new_first_name = input("Enter the new first name: ")
                    if is_valid_name(new_first_name):
                        self.set_new_first_name(matching_users[0][0], new_first_name)
                        print(f"First name for system admin {decrypt(matching_users[0][0])} has been updated to {new_first_name}.")
                        logger = EncryptedLogger()
                        logger.log_entry("super_admin", "Updated System Admin First Name", f"New First Name: {new_first_name}", "No")
                        break
                    else:
                        print("Invalid first name format.")
                        tries += 1
                        print(f"You have {3 - tries} tries left.")
                if tries == 3:
                    print("Failed to update first name after 3 invalid attempts.")
                    logger = EncryptedLogger()
                    logger.log_entry("super_admin", "Too many wrong first name attempts", f" ", "Yes")
            elif choice == "4":
                tries = 0
                while tries < 3:
                    new_last_name = input("Enter the new last name: ")
                    if is_valid_name(new_last_name):
                        self.set_new_last_name(matching_users[0][0], new_last_name)
                        print(f"Last name for system admin {decrypt(matching_users[0][0])} has been updated to {new_last_name}.")
                        logger = EncryptedLogger()
                        logger.log_entry("super_admin", "Updated System Admin Last Name", f"New Last Name: {new_last_name}", "No")
                        break
                    else:
                        print("Invalid last name format.")
                        tries += 1
                        print(f"You have {3 - tries} tries left.")
                if tries == 3:
                    print("Failed to update last name after 3 invalid attempts.")
                    logger = EncryptedLogger()
                    logger.log_entry("super_admin", "Too many wrong last name attempts", f" ", "Yes")
            elif choice == "5":
                print("Going back to the previous menu.")
                return
            else:
                print("Invalid choice. Please try again.")

        ## --- Specific exceptions ---
        except sqlite3.OperationalError as e:
            print(f"Operational Error: database or SQL issue. Contact Administrator.")
            logger = EncryptedLogger()
            logger.log_entry("System", "Operational Error on updating super_admin", f"{e}", "Yes")
            return
        except sqlite3.InterfaceError as e:
            print(f"Interface Error: invalid parameter binding. Contact Administrator.")
            logger = EncryptedLogger()
            logger.log_entry("System", "Interface Error on updating super_admin", f"{e}", "Yes")
            return
        except sqlite3.IntegrityError as e:
            print(f"Integrity Error: There was a data integrity issue. Contact Administrator.")
            logger = EncryptedLogger()
            logger.log_entry("System", "Integrity Error on updating super_admin", f"{e}", "Yes")
            return
        except sqlite3.DatabaseError as e:
            print(f"Database Error: possible corruption or I/O issue. Contact Administrator.")
            logger = EncryptedLogger()
            logger.log_entry("System", "Database Error on updating super_admin", f"{e}", "Yes")
            return
        except TypeError as e:
            print(f"Type Error: invalid argument type.")
            logger = EncryptedLogger()
            logger.log_entry("System", "Type Error on updating super_admin", f"{e}", "Yes")
            return
        except Exception as e:
            print(f"Unexpected Exception occurred.")
            logger = EncryptedLogger()
            logger.log_entry("System", "Unexpected Error on updating super_admin", f"{e}", "Yes")
            return
        
    def delete_system_admin(self):
        try:
            sysAdmins = self.view_all_system_admins()
            if not sysAdmins:
                print("No system admins available to delete.")
                return
            is_valid, username_to_delete = validate_username(input("Enter the username of the system admin you want to delete: "))
            if not is_valid:
                print("Invalid username format.")
                return
            matching_users = [user for user in sysAdmins if decrypt(user[0]).lower() == username_to_delete.lower()]
            if not matching_users:
                print(f"No system admin found with username '{username_to_delete}'.")
                return
            if self.confirm_password():
                connection = self.db_context.connect()
                if connection:
                    cursor = connection.cursor()
                    enc_username = matching_users[0][0]
                    cursor.execute("DELETE FROM User WHERE Username = ?", (enc_username,))
                    connection.commit()
                    print(f"System admin '{decrypt(matching_users[0][0])}' has been deleted.")
                    logger = EncryptedLogger()
                    logger.log_entry("super_admin", "Deleted System Admin Account", f"Username: {decrypt(matching_users[0][0])} is deleted" , "No")
                else:
                    print("Failed to connect to the database.")
            else:
                logger = EncryptedLogger()
                logger.log_entry(f"super_admin", "Too many wrong password attempts", f"Could not confirm his own identity", "Yes")
                from um_members import pre_login_menu
                pre_login_menu()
        
        ## --- Specific exceptions ---
        except sqlite3.OperationalError as e:
            print(f"Operational Error: database or SQL issue. Contact Administrator.")
            logger = EncryptedLogger()
            logger.log_entry("System", "Operational Error on deleting system_admin", f"{e}", "Yes")
            return
        except sqlite3.DatabaseError as e:
            print(f"Database Error: possible corruption or I/O issue. Contact Administrator.")
            logger = EncryptedLogger()
            logger.log_entry("System", "Database Error on deleting system_admin", f"{e}", "Yes")
            return
        except sqlite3.IntegrityError as e:
            print(f"Integrity Error: There was a data integrity issue. Contact Administrator.")
            logger = EncryptedLogger()
            logger.log_entry("System", "Integrity Error on deleting system_admin", f"{e}", "Yes")
            return
        except TypeError as e:
            print(f"Type Error: invalid argument type.")
            logger = EncryptedLogger()
            logger.log_entry("System", "Type Error on deleting system_admin", f"{e}", "Yes")
            return
        except ValueError as e:
            print(f"Value Error: {e}")
            logger = EncryptedLogger()
            logger.log_entry("System", "Value Error on deleting system_admin", f"{e}", "Yes")
            return
        except Exception as e:
            print(f"Unexpected Exception occurred.")
            logger = EncryptedLogger()
            logger.log_entry("System", "Unexpected Error on deleting system_admin", f"{e}", "Yes")
            return
        
    def view_all_system_admins(self):
        try:
            connection = self.db_context.connect()
            if connection:
                cursor = connection.cursor()
                cursor.execute("SELECT Username, Role FROM User")
                users = cursor.fetchall()
                system_admins = []
                for user in users:
                    if decrypt(user[1]) == "systemadmin":
                        system_admins.append(user)
                if system_admins:
                    print(f"Retrieved {len(system_admins)} system admin(s):")
                    for user in system_admins:
                        print(f"- {decrypt(user[0])}")
                    return system_admins
                else:
                    print("No system admin accounts found.")
                    return []
            else:
                print("No database connection.")
                return "Error"
    
        ## --- Specific exceptions ---
        except sqlite3.OperationalError as e:
            # Happens if table doesn't exist, DB is locked, or SQL syntax is wrong
            print(f"Operational Error: database or SQL issue. Contact Administrator.")
            logger = EncryptedLogger()
            logger.log_entry("System", "Operational Error on getting all system_admins", f"{e}", "Yes")
            return None
        except sqlite3.DatabaseError as e:
            # Base class for all database-related errors (corrupted DB, etc.)
            print(f"Database Error: possible corruption or I/O issue. Contact Administrator.")
            logger = EncryptedLogger()
            logger.log_entry("System", "Database Error on getting all system_admins", f"{e}", "Yes")
            return None
        except sqlite3.InterfaceError as e:
            # Raised if wrong data types or bindings are passed to SQL placeholders
            print(f"Interface Error: invalid parameter binding. Contact Administrator.")
            logger = EncryptedLogger()
            logger.log_entry("System", "Interface Error on getting all system_admins", f"{e}", "Yes")
            return None
        except Exception as e:
            # Catch-all for anything unexpected
            print(f"Unexpected Exception occurred.")
            logger = EncryptedLogger()
            logger.log_entry("System", "Unexpected Error on getting all system_admins", f"{e}", "Yes")
            return None

    def view_all_service_engineers(self):
        try:
            connection = self.db_context.connect()
            if connection:
                cursor = connection.cursor()
                cursor.execute("SELECT Username FROM User WHERE Role = ? ", ("serviceengineer",))
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
            
        ## --- Specific exceptions ---
        except sqlite3.OperationalError as e:
            # Happens if table doesn't exist, DB is locked, or SQL syntax is wrong
            print(f"Operational Error: database or SQL issue. Contact Administrator.")
            logger = EncryptedLogger()
            logger.log_entry("System", "Operational Error on getting all service engineers", f"{e}", "Yes")
            return None
        except sqlite3.DatabaseError as e:
            # Base class for all database-related errors (corrupted DB, etc.)
            print(f"Database Error: possible corruption or I/O issue. Contact Administrator.")
            logger = EncryptedLogger()
            logger.log_entry("System", "Database Error on getting all service engineers", f"{e}", "Yes")
            return None
        except sqlite3.InterfaceError as e:
            # Raised if wrong data types or bindings are passed to SQL placeholders
            print(f"Interface Error: invalid parameter binding. Contact Administrator.")
            logger = EncryptedLogger()
            logger.log_entry("System", "Interface Error on getting all service engineers", f"{e}", "Yes")
            return None
        except Exception as e:
            # Catch-all for anything unexpected
            print(f"Unexpected Exception occurred.")
            logger = EncryptedLogger()
            logger.log_entry("System", "Unexpected Error on getting all service engineers", f"{e}", "Yes")
            return None

    def set_new_username(self, old_username, new_username):
        try:
            connection = self.db_context.connect()
            if connection:
                cursor = connection.cursor()
                enc_new = encrypt(new_username)
                cursor.execute(
                    "UPDATE User SET Username = ? WHERE Username = ?",
                    (enc_new, old_username)
                )
                connection.commit()
            else:
                print("Failed to connect to the database.")

        ## --- Specific exceptions ---
        except sqlite3.OperationalError as e:
            print("Operational Error: database or SQL issue.")
            logger = EncryptedLogger()
            logger.log_entry("System", "Operational Error in set_new_username", f"{e}", "Yes")
        except sqlite3.DatabaseError as e:
            print("Database Error: possible corruption or I/O issue.")
            logger = EncryptedLogger()
            logger.log_entry("System", "Database Error in set_new_username", f"{e}", "Yes")
        except sqlite3.InterfaceError as e:
            print("Interface Error: invalid SQL parameters.")
            logger = EncryptedLogger()
            logger.log_entry("System", "Interface Error in set_new_username", f"{e}", "Yes")
        except Exception as e:
            print("Unexpected error occurred while updating username.")
            logger = EncryptedLogger()
            logger.log_entry("System", "Unexpected Error in set_new_username", f"{e}", "Yes")


    def set_new_first_name(self, username, new_first_name):
        try:
            connection = self.db_context.connect()
            if connection:
                cursor = connection.cursor()
                enc_first_name = encrypt(new_first_name)
                cursor.execute(
                    "UPDATE User SET FirstName = ? WHERE Username = ?",
                    (enc_first_name, username)
                )
                connection.commit()
            else:
                print("Failed to connect to the database.")

        ## --- Specific exceptions ---
        except sqlite3.OperationalError as e:
            print("Operational Error: database or SQL issue.")
            logger = EncryptedLogger()
            logger.log_entry("System", "Operational Error in set_new_first_name", f"{e}", "Yes")
        except sqlite3.DatabaseError as e:
            print("Database Error: possible corruption or I/O issue.")
            logger = EncryptedLogger()
            logger.log_entry("System", "Database Error in set_new_first_name", f"{e}", "Yes")
        except sqlite3.InterfaceError as e:
            print("Interface Error: invalid SQL parameters.")
            logger = EncryptedLogger()
            logger.log_entry("System", "Interface Error in set_new_first_name", f"{e}", "Yes")
        except Exception as e:
            print("Unexpected error occurred while updating first name.")
            logger = EncryptedLogger()
            logger.log_entry("System", "Unexpected Error in set_new_first_name", f"{e}", "Yes")


    def set_new_last_name(self, username, new_last_name):
        try:
            connection = self.db_context.connect()
            if connection:
                cursor = connection.cursor()
                enc_last_name = encrypt(new_last_name)
                cursor.execute(
                    "UPDATE User SET LastName = ? WHERE Username = ?",
                    (enc_last_name, username)
                )
                connection.commit()
            else:
                print("Failed to connect to the database.")

        ## --- Specific exceptions ---
        except sqlite3.OperationalError as e:
            print("Operational Error: database or SQL issue.")
            logger = EncryptedLogger()
            logger.log_entry("System", "Operational Error in set_new_last_name", f"{e}", "Yes")
        except sqlite3.DatabaseError as e:
            print("Database Error: possible corruption or I/O issue.")
            logger = EncryptedLogger()
            logger.log_entry("System", "Database Error in set_new_last_name", f"{e}", "Yes")
        except sqlite3.InterfaceError as e:
            print("Interface Error: invalid SQL parameters.")
            logger = EncryptedLogger()
            logger.log_entry("System", "Interface Error in set_new_last_name", f"{e}", "Yes")
        except Exception as e:
            print("Unexpected error occurred while updating last name.")
            logger = EncryptedLogger()
            logger.log_entry("System", "Unexpected Error in set_new_last_name", f"{e}", "Yes")


    def reset_password_function(self, username, new_password):
        try:
            connection = self.db_context.connect()
            if connection:
                cursor = connection.cursor()
                cursor.execute(
                    "UPDATE User SET Password = ?, ResettedPasswordCheck = ? WHERE Username = ?",
                    (new_password, encrypt("1"), username)
                )
                connection.commit()
            else:
                print("Failed to connect to the database.")

        ## --- Specific exceptions ---
        except sqlite3.OperationalError as e:
            print("Operational Error: database or SQL issue.")
            logger = EncryptedLogger()
            logger.log_entry("System", "Operational Error in reset_password_function", f"{e}", "Yes")
        except sqlite3.DatabaseError as e:
            print("Database Error: possible corruption or I/O issue.")
            logger = EncryptedLogger()
            logger.log_entry("System", "Database Error in reset_password_function", f"{e}", "Yes")
        except sqlite3.InterfaceError as e:
            print("Interface Error: invalid SQL parameters.")
            logger = EncryptedLogger()
            logger.log_entry("System", "Interface Error in reset_password_function", f"{e}", "Yes")
        except Exception as e:
            print("Unexpected error occurred while resetting password.")
            logger = EncryptedLogger()
            logger.log_entry("System", "Unexpected Error in reset_password_function4", f"{e}", "Yes")


    def activate_inactive_account(self):
        try:
            connection = self.db_context.connect()
            if not connection:
                print("No database connection.")
                return
            
            cursor = connection.cursor()
            cursor.execute("SELECT Username, role, isActive FROM User ")
            users = cursor.fetchall()
            
            if not users:
                print("No accounts found.")
                return
            inactive_users = []
            for user in users:
                if decrypt(user[2]) == "0":
                    inactive_users.append(user)
            if inactive_users == []:
                print("No inactive accounts found.")
                return
            print("\nInactive Accounts:")
            for idx, user in enumerate(inactive_users, 1):
                print(f"[{idx}] Username: {decrypt(user[0])}, Role: {user[1]}")

            try:
                choice = int(input("Enter the number of the account to activate: "))
                if 1 <= choice <= len(inactive_users):
                    username = inactive_users[choice-1][0]
                    cursor.execute("UPDATE User SET IsActive = ? WHERE Username = ?", (encrypt("1"), username))
                    connection.commit()
                    print(f"Account '{decrypt(username)}' has been activated.")
                    logger = EncryptedLogger()
                    logger.log_entry("super_admin", "Activated Account", f"Username: {decrypt(username)} activated", "No")
                else:
                    print("Invalid selection.")
            except ValueError:
                print("Invalid input. Please enter a number.")

        ## --- Specific exceptions ---
        except sqlite3.OperationalError as e:
            print("Operational Error: database or SQL issue.")
            logger = EncryptedLogger()
            logger.log_entry("System", "Operational Error in activate_inactive_account", f"{e}", "Yes")
        except sqlite3.DatabaseError as e:
            print("Database Error: possible corruption or I/O issue.")
            logger = EncryptedLogger()
            logger.log_entry("System", "Database Error in activate_inactive_account", f"{e}", "Yes")
        except sqlite3.InterfaceError as e:
            print("Interface Error: invalid SQL parameters.")
            logger = EncryptedLogger()
            logger.log_entry("System", "Interface Error in activate_inactive_account", f"{e}", "Yes")
        except Exception as e:
            print("Unexpected error occurred while activating account.")
            logger = EncryptedLogger()
            logger.log_entry("System", "Unexpected Error in activate_inactive_account", f"{e}", "Yes")


    def confirm_password(self):
        tries = 0
        while tries < 3:
            password = getpass.getpass("Enter your password: ")
            if password == "Admin_123?":
                return True
            else:
                tries += 1
                print(f"Incorrect password. You have {3 - tries} tries left.")
        return False