from DbContext.crypto_utils import hash_password
from DbContext.encrypted_logger import EncryptedLogger, fernet
import os
from systemAdmin.system_admin import systemAdmin
from traveller.Traveller_menu import traveller_menu
from um_members import pre_login_menu
from scooter.Scooter import main
import getpass

from valid_in_out_put import validate_input_pass, validate_input_username
from validation.isValidName import is_valid_name

def system_admin_menu(username):
    current_user = username  # Replace with actual logged-in username
    sysAd= systemAdmin()
    logger = EncryptedLogger()
    
    
    while True:
        print(f"\nWelcome, {current_user}!")
        print("\nSYSTEM ADMIN MENU")
        print("[1] View all user accounts")
        print("[2] Manage Service Engineers")
        print("[3] Edit your account")
        print("[4] Manage Travellers")
        print("[5] Manage Scooters")
        print("[6] View Logs")
        print("[7] Go Back")
        print("[8] Logout")
        print("[9] Exit")
        choice = input("Enter your choice: ")
        
        if choice == "1":
            sysAd.view_all_users(username)
        elif choice == "2":
            system_admin_service_engineer_menu(username)
        elif choice == "3":
            username = edit_account_menu(username)
        elif choice == "4":
            traveller_menu(username)
        elif choice == "5":
            main("systemadmin", username)
        elif choice == "6":
            logger = EncryptedLogger()
            # Read and separate logs by status (like super admin)
            if not hasattr(logger, 'logfile_path') or not logger.logfile_path:
                print("No log file found.")
            elif not os.path.exists(logger.logfile_path):
                print("No log file found.")
            else:
                new_logs = []
                old_logs = []
                all_rows = []
                with open(logger.logfile_path, "r") as f:
                    for line in f:
                        decrypted = fernet.decrypt(line.strip().encode()).decode()
                        parts = decrypted.split("|")
                        if len(parts) == 8:
                            if parts[-1] == "new":
                                new_logs.append(parts)
                            else:
                                old_logs.append(parts)
                        all_rows.append(parts)
                # Print old logs table
                if old_logs:
                    print("\n--- OLD LOGS ---")
                    logger._print_table(old_logs)
                else:
                    print("\nNo old logs.")
                # Print new logs table
                if new_logs:
                    print("\n--- NEW LOGS ---")
                    logger._print_table(new_logs)
                else:
                    print("\nNo new logs.")
                # Mark all new logs as old
                if new_logs:
                    updated_lines = []
                    for row in all_rows:
                        if len(row) == 8 and row[-1] == "new":
                            row[-1] = "old"
                        updated_lines.append(fernet.encrypt("|".join(row).encode()).decode())
                    with open(logger.logfile_path, "w") as f:
                        for line in updated_lines:
                            f.write(line + "\n")
        elif choice == "7":
            return  # Go back to previous menu
        elif choice == "8":
            print("👋 Logging out.")
            from um_members import pre_login_menu
            logger.log_entry(f"{username}", "Logged out", f"Success", "No")
            pre_login_menu()
            return
        elif choice == "9":
            logger.log_entry(f"{username}", "Exited the system", f"Success", "No")
            print("👋 Exiting system.")
            exit()
        else:
            print("Invalid choice. Please try again.")

def system_admin_service_engineer_menu(username):
    sysAd= systemAdmin()
    while True:
        print("\nSERVICE ENGINEER MANAGEMENT")
        print("[1] Create Service Engineer Account")
        print("[2] Update existing Service Engineer Account")
        print("[3] Delete Service Engineer Account")
        print("[4] Go Back")
        choice = input("\nEnter your choice: ")
        if choice == "1":
            print("\n-- Create Service Engineer --")
            sysAd.create_service_engineer(username)
        elif choice == "2":
            print("Updating existing Service Engineer Account...")
            sysAd.update_service_engineer(username)
        elif choice == "3":
            print("Deleting Service Engineer Account...")
            sysAd.delete_service_engineer(username)            
        elif choice == "4":
            return
        else:
            print("Invalid choice. Please try again.")

def edit_account_menu(username):
    sysAd= systemAdmin()
    while True:
        print(f"\nEDIT ACCOUNT MENU FOR {username}")
        print("[1] Change Username")
        print("[2] Change Password")
        print("[3] Change First Name")
        print("[4] Change Last Name")
        print("[5] Delete Account")
        print("[6] Go Back")
        choice = input("\nEnter your choice: ")

        if choice == "1":
            if sysAd.confirm_password(username):
                tries = 0
                while tries < 3:
                    new_username = input("Enter username: ")
                    verified_username, new_username = validate_input_username(new_username)
                    if verified_username:
                        user = sysAd.get_username(username)
                        if sysAd.set_new_username_system(user, new_username):
                            print("Username updated successfully.")
                            logger = EncryptedLogger()
                            logger.log_entry(f"{username}", "Updated his own username", f"Old: {username}, New: {new_username}", "No")
                            username = new_username
                            break
                        else:
                            print("Failed to update username.")
                    else:
                        print("Invalid username format or already exists.")
                        tries += 1
                        print(f"You have {3 - tries} tries left.")
                if tries == 3:
                        print("Failed to update username after 3 invalid attempts.")
                        logger = EncryptedLogger()
                        logger.log_entry("super_admin", "Tried to update with wrong format 3 times", f" ", "Yes")
            else:
                logger = EncryptedLogger()
                logger.log_entry(f"{username}", "Too many wrong password attempts", f"Could not confirm his own identity", "Yes")
                pre_login_menu()

        elif choice == "2":
            if sysAd.confirm_password(username):
                tries = 0
                while tries < 3:
                    new_password = getpass.getpass("Enter new password: ")
                    verified_password, new_password = validate_input_pass(new_password)
                    if verified_password:
                        hashed_password = hash_password(new_password)
                        user = sysAd.get_username(username)
                        if sysAd.reset_password_system(user, hashed_password):
                            print("Password updated successfully.")
                            logger = EncryptedLogger()
                            logger.log_entry(f"{username}", "Updated his own password", f" ", "No")
                            break
                        else:
                            print("Failed to update password.")
                    else:
                        print("Invalid password format.")
                        tries += 1
                        print(f"You have {3 - tries} tries left.")
                if tries == 3:
                        print("Failed to update password after 3 invalid attempts.")
                        logger = EncryptedLogger()
                        logger.log_entry("super_admin", "Tried to update with wrong format 3 times", f" ", "Yes")
            else:
                logger = EncryptedLogger()
                logger.log_entry(f"{username}", "Too many wrong password attempts", f"Could not confirm his own identity", "Yes")
                pre_login_menu()
        elif choice == "3":
            tries = 0
            while tries < 3:
                new_first_name = input("Enter new first name: ")
                user = sysAd.get_username(username)
                if is_valid_name(new_first_name):
                    sysAd.set_new_first_name(user, new_first_name)
                    print("First name updated successfully.")
                    logger = EncryptedLogger()
                    logger.log_entry(f"{username}", "Updated his own first name", f"New: {new_first_name}", "No")
                    break
                else:
                    print("Invalid first name format.")
                    tries += 1
                    print(f"You have {3 - tries} tries left.")
            if tries == 3:
                print("Failed to update first name after 3 invalid attempts.")
                logger = EncryptedLogger()
                logger.log_entry(f"{username}", "Tried to update first name with wrong format 3 times", f" ", "Yes")

        elif choice == "4":
            tries = 0
            while tries < 3:
                new_last_name = input("Enter new last name: ")
                user = sysAd.get_username(username)
                if is_valid_name(new_last_name):
                    sysAd.set_new_last_name(user, new_last_name)
                    print("Last name updated successfully.")
                    logger = EncryptedLogger()
                    logger.log_entry(f"{username}", "Updated his own last name", f"New: {new_last_name}", "No")
                    break
                else:
                    print("Invalid last name format.")
                    tries += 1
                    print(f"You have {3 - tries} tries left.")
            if tries == 3:
                print("Failed to update last name after 3 invalid attempts.")
                logger = EncryptedLogger()
                logger.log_entry(f"{username}", "Tried to update last name with wrong format 3 times", f" ", "Yes")

        elif choice == "5":
            if sysAd.confirm_password(username):
                user = sysAd.get_username(username)
                sysAd.delete_account(user)
                print("Account deleted successfully. returning to main menu.")
                logger = EncryptedLogger()
                logger.log_entry(f"{username}", "Deleted his own account", f" ", "No")
                pre_login_menu()
            else:
                logger = EncryptedLogger()
                logger.log_entry(f"{username}", "Too many wrong password attempts", f"Could not confirm his own identity", "Yes")
                pre_login_menu()
        elif choice == "6":
            return username  # Go back to the previous menu
        else:
            print("Invalid choice. Please try again.")



