from DbContext.encrypted_logger import EncryptedLogger, fernet
from SuperAdmin.super_admin import SuperAdmin
from systemAdmin.system_admin import systemAdmin
from systemAdmin.system_admin_menu import system_admin_service_engineer_menu
from traveller.Traveller_menu import traveller_menu
from scooter.Scooter import main
import os


def super_admin_menu(username):
    current_user = username
    print(f"\nWelcome, {current_user}!")
    while True:
        print("\nSUPER ADMIN MENU")
        print("1. Manage System Admins")
        print("2. Manage Service Engineers")
        print("3. Manage Travellers")
        print("4. Manage Scooters")
        print("5. View Logs")
        print("6. View All user accounts")
        print("7. Activate Inactive Accounts")
        print("8. Exit")
        choice = input("\nEnter your choice: ")
        
        if choice == "1":
            super_admin_system_admin_menu()
        elif choice == "2":
            system_admin_service_engineer_menu(username)
        elif choice == "3":
            traveller_menu(username)
        elif choice == "4":
            main("superadmin", username)
        elif choice == "5":
            logger = EncryptedLogger()
            # Read and separate logs by status
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
        elif choice == "6":
            sysAd= systemAdmin()
            print("\n-- View All User Accounts --")
            sysAd.view_all_users()
        elif choice == "7":
            sa = SuperAdmin()
            sa.activate_inactive_account()
        elif choice == "8":
            print("Exiting...")
            break
        else:
            print("Invalid choice. Please try again.")

def super_admin_system_admin_menu():
    sa = SuperAdmin()
    
    while True:
        print("\nSYSTEM ADMIN MANAGEMENT")
        print("1. Create System Admin Account")
        print("2. Update existing System Admin Account")
        print("3. Delete System Admin Account")
        print("4. Go Back")
        
        choice = input("\nEnter your choice: ").strip()
        
        if choice == "1":
            print("\n-- Create System Admin --")
            sa.create_system_admin()
        elif choice == "2":
            print("Updating existing System Admin Account...")
            sa.update_system_admin()
        elif choice == "3":
            print("Deleting System Admin Account...")
            sa.delete_system_admin()
        elif choice == "4":
            break
        else:
            print("Invalid choice. Please try again.")

def super_admin_service_engineer_menu(username):
    sysAd = systemAdmin()
    
    while True:
        print("\nSERVICE ENGINEER MANAGEMENT")
        print("1. Create Service Engineer Account")
        print("2. Update existing Service Engineer Account")
        print("3. Delete Service Engineer Account")
        print("4. Go Back")
        choice = input("\nEnter your choice: ")
        
        if choice == "1":
            print("\n-- Create System Admin --")
            sysAd.create_service_engineer(username)
        
        elif choice == "2":
            print("Updating existing Service Engineer Account...")
            sysAd.update_service_engineer(username)
            
        elif choice == "3":
            print("Deleting Service Engineer Account...")
            sysAd.delete_service_engineer(username)
            
        elif choice == "4":
            print("Resetting password for existing Service Engineer Account...")
            # Implement password reset logic here
            sysAd.reset_password_service_engineer()
        elif choice == "5":
            return
        else:
            print("Invalid choice. Please try again.")