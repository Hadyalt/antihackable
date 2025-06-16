from DbContext.encrypted_logger import EncryptedLogger
from SuperAdmin.super_admin import SuperAdmin
from systemAdmin.system_admin import systemAdmin
from systemAdmin.system_admin_menu import system_admin_service_engineer_menu
from traveller.Traveller_menu import traveller_menu
from scooter.Scooter import main


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
        print("7. Exit")
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
            logger.read_logs(table_format=True)
        elif choice == "6":
            sysAd= systemAdmin()
            print("\n-- View All User Accounts --")
            sysAd.view_all_users()
        elif choice == "7":
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