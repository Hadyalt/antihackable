from DbContext.encrypted_logger import EncryptedLogger
from Login.verification import Verification
from Login.verification import Verification
from systemAdmin.system_admin import systemAdmin
from traveller.Traveller_menu import traveller_menu
from um_members import pre_login_menu
from scooter.Scooter import main

def system_admin_menu(username):
    current_user = username  # Replace with actual logged-in username
    print(f"\nWelcome, {current_user}!")
    sysAd= systemAdmin()
    
    while True:
        # check the database if the systemadmin has a reset password
        if sysAd.check_reset_password(username):
            print("You have a reset password, please reset it before proceeding.")
            verified_password = False
            while not verified_password:
                password = input("Enter password: ")
                verified_password = Verification.verify_Password(password)
            hashed_password = Verification.hash_password(password)
            sysAd.reset_password_function(username, hashed_password, "systemadmin")
            sysAd.reset_resetted_password_check(username)
            print("Password reset completed. You can now proceed with the menu options.")
        
        print("\nSYSTEM ADMIN MENU")
        print("1. View all user accounts")
        print("2. Manage Service Engineers")
        print("3. Edit your account") 
        print("4. Manage Travellers")
        print("5. Manage Scooters")  
        print("6. View Logs")
        print("7. Exit")
        choice = input("\nEnter your choice: ")
        
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
            logger.read_logs(table_format=True)
        elif choice == "7":
            print("Exiting...")
            return
        else:
            print("Invalid choice. Please try again.")

def system_admin_service_engineer_menu(username):
    sysAd= systemAdmin()
    
    while True:
        print("\nSERVICE ENGINEER MANAGEMENT")
        print("1. Create Service Engineer Account")
        print("2. Update existing Service Engineer Account")
        print("3. Delete Service Engineer Account")
        print("4. Reset the password for an existing Service Engineer Account")
        print("5. Go Back")
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
            print("Resetting password for existing Service Engineer Account...")
            # Implement password reset logic here
            sysAd.reset_password_service_engineer(username)
        elif choice == "5":
            return
        else:
            print("Invalid choice. Please try again.")
    
def edit_account_menu(username):
    sysAd= systemAdmin()
    while True:
        print(f"\nEDIT ACCOUNT MENU FOR {username}")
        print("1. Change Username")
        print("2. Change Password")
        print("3. Delete Account")
        print("4. Go Back")
        choice = input("\nEnter your choice: ")
        
        if choice == "1":
            verified_username = False
            while not verified_username:
                new_username = input("Enter username: ")
                verified_username = Verification.verify_username(new_username)
            user = sysAd.get_username(username)
            if sysAd.set_new_username_system(user, new_username):
                print("Username updated successfully.")
                logger = EncryptedLogger()
                logger.log_entry(f"{username}", "Updated his own username", f"Old: {username}, New: {new_username}", "No")
                username = new_username
            else:
                print("Failed to update username.")
        elif choice == "2":
            verified_password = False
            while not verified_password:
                new_password = input("Enter new password: ")
                verified_password = Verification.verify_Password(new_password)
            hashed_password = Verification.hash_password(new_password)
            user = sysAd.get_username(username)
            if sysAd.reset_password_system(user, hashed_password):
                print("Password updated successfully.")
                logger = EncryptedLogger()
                logger.log_entry(f"{username}", "Updated his own password", f" ", "No")
            else:
                print("Failed to update password.")
        elif choice == "3":
            user = sysAd.get_username(username)
            sysAd.delete_account(user)
            print("Account deleted successfully. returning to main menu.")
            logger = EncryptedLogger()
            logger.log_entry(f"{username}", "Deleted his own account", f" ", "No")
            pre_login_menu()
        elif choice == "4":
            return username  # Go back to the previous menu
        else:
            print("Invalid choice. Please try again.")



