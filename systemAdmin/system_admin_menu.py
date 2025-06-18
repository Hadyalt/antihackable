from DbContext.encrypted_logger import EncryptedLogger, fernet
import os
from Login.verification import Verification
from systemAdmin.system_admin import systemAdmin
from traveller.Traveller_menu import traveller_menu
from um_members import pre_login_menu
from scooter.Scooter import main
from input_output_utils import validate_input, sanitize_output

def system_admin_menu(username):
    current_user = username
    print(sanitize_output(f"\nWelcome, {current_user}!"))
    sysAd= systemAdmin()
    while True:
        print(sanitize_output("\nSYSTEM ADMIN MENU"))
        print(sanitize_output("1. View all user accounts"))
        print(sanitize_output("2. Manage Service Engineers"))
        print(sanitize_output("3. Edit your account"))
        print(sanitize_output("4. Manage Travellers"))
        print(sanitize_output("5. Manage Scooters"))
        print(sanitize_output("6. View Logs"))
        print(sanitize_output("7. Exit"))
        try:
            choice = validate_input(input("\nEnter your choice: ").strip(), pattern=r"^[1-7]$", context="System Admin Menu Choice")
        except ValueError as e:
            print(sanitize_output(f"Invalid input: {e}"))
            continue
        if choice == "1":
            sysAd.view_all_users()
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
            if not hasattr(logger, 'logfile_path') or not logger.logfile_path:
                print(sanitize_output("No log file found."))
            elif not os.path.exists(logger.logfile_path):
                print(sanitize_output("No log file found."))
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
                if old_logs:
                    print(sanitize_output("\n--- OLD LOGS ---"))
                    logger._print_table(old_logs)
                else:
                    print(sanitize_output("\nNo old logs."))
                if new_logs:
                    print(sanitize_output("\n--- NEW LOGS ---"))
                    logger._print_table(new_logs)
                else:
                    print(sanitize_output("\nNo new logs."))
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
            print(sanitize_output("Exiting..."))
            return
        else:
            print(sanitize_output("Invalid choice. Please try again."))

def system_admin_service_engineer_menu(username):
    sysAd= systemAdmin()
    while True:
        print(sanitize_output("\nSERVICE ENGINEER MANAGEMENT"))
        print(sanitize_output("1. Create Service Engineer Account"))
        print(sanitize_output("2. Update existing Service Engineer Account"))
        print(sanitize_output("3. Delete Service Engineer Account"))
        print(sanitize_output("4. Go Back"))
        try:
            choice = validate_input(input("\nEnter your choice: ").strip(), pattern=r"^[1-4]$", context="Service Engineer Management Choice")
        except ValueError as e:
            print(sanitize_output(f"Invalid input: {e}"))
            continue
        if choice == "1":
            print(sanitize_output("\n-- Create Service Engineer --"))
            sysAd.create_service_engineer(username)
        elif choice == "2":
            print(sanitize_output("Updating existing Service Engineer Account..."))
            sysAd.update_service_engineer(username)
        elif choice == "3":
            print(sanitize_output("Deleting Service Engineer Account..."))
            sysAd.delete_service_engineer(username)
        elif choice == "4":
            return
        else:
            print(sanitize_output("Invalid choice. Please try again."))
    
def edit_account_menu(username):
    sysAd= systemAdmin()
    while True:
        print(sanitize_output(f"\nEDIT ACCOUNT MENU FOR {username}"))
        print(sanitize_output("1. Change Username"))
        print(sanitize_output("2. Change Password"))
        print(sanitize_output("3. Delete Account"))
        print(sanitize_output("4. Go Back"))
        try:
            choice = validate_input(input("\nEnter your choice: ").strip(), pattern=r"^[1-4]$", context="Edit Account Menu Choice")
        except ValueError as e:
            print(sanitize_output(f"Invalid input: {e}"))
            continue
        if choice == "1":
            verified_username = False
            while not verified_username:
                new_username = input("Enter username: ")
                verified_username = Verification.verify_username(new_username)
            user = sysAd.get_username(username)
            if sysAd.set_new_username_system(user, new_username):
                print(sanitize_output("Username updated successfully."))
                logger = EncryptedLogger()
                logger.log_entry(f"{username}", "Updated his own username", f"Old: {username}, New: {new_username}", "No")
                username = new_username
            else:
                print(sanitize_output("Failed to update username."))
        elif choice == "2":
            verified_password = False
            while not verified_password:
                new_password = input("Enter new password: ")
                verified_password = Verification.verify_Password(new_password)
            hashed_password = Verification.hash_password(new_password)
            user = sysAd.get_username(username)
            if sysAd.reset_password_system(user, hashed_password):
                print(sanitize_output("Password updated successfully."))
                logger = EncryptedLogger()
                logger.log_entry(f"{username}", "Updated his own password", f" ", "No")
            else:
                print(sanitize_output("Failed to update password."))
        elif choice == "3":
            user = sysAd.get_username(username)
            sysAd.delete_account(user)
            print(sanitize_output("Account deleted successfully. returning to main menu."))
            logger = EncryptedLogger()
            logger.log_entry(f"{username}", "Deleted his own account", f" ", "No")
            pre_login_menu()
        elif choice == "4":
            return username
        else:
            print(sanitize_output("Invalid choice. Please try again."))



