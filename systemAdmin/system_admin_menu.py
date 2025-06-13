from Login.verification import Verification
from systemAdmin.system_admin import systemAdmin
from um_members import pre_login_menu

def system_admin_menu(username):
    sysAd= systemAdmin()
    
    while True:
        print("\nSYSTEM ADMIN MENU")
        print("1. View all user accounts")
        print("2. Manage Service Engineers")
        print("3. Edit your account")   
        print("4. Backup & Restore")
        print("5. View Logs")
        print("6. Manage Travellers")
        print("7. Manage Scooters")
        print("8. Exit")
        choice = input("\nEnter your choice: ")
        
        if choice == "1":
            sysAd.view_all_users()
        elif choice == "2":
            system_admin_service_engineer_menu()
        elif choice == "3":
            username = edit_account_menu(username)
        elif choice == "8":
            print("Exiting...")
            break
        else:
            print("Invalid choice. Please try again.")

def system_admin_service_engineer_menu():
    sysAd= systemAdmin()
    
    while True:
        print("\nSERVICE ENGINEER MANAGEMENT")
        print("1. Create Service Engineer Account")
        print("2. Update existing System Admin Account")
        print("3. Delete System Admin Account")
        print("4. Reset the password for an existing System Admin Account")
        print("5. Go Back")
        choice = input("\nEnter your choice: ")
        
        if choice == "1":
            print("\n-- Create Service Engineer --")
            sysAd.create_service_engineer()
        elif choice == "2":
            print("Updating existing Service Engineer Account...")
            sysAd.update_service_engineer()
        elif choice == "3":
            print("Deleting System Admin Account...")
            sysAd.delete_service_engineer()
        elif choice == "4":
            print("Resetting password for existing System Admin Account...")
            # Implement password reset logic here
        elif choice == "5":
            break
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
            if sysAd.set_new_username_system(username, new_username):
                print("Username updated successfully.")
                username = new_username
            else:
                print("Failed to update username.")
        elif choice == "2":
            verified_password = False
            while not verified_password:
                new_password = input("Enter new password: ")
                verified_password = Verification.verify_Password(new_password)
            hashed_password = Verification.hash_password(new_password)
            if sysAd.reset_password_system(username, hashed_password):
                print("Password updated successfully.")
            else:
                print("Failed to update password.")
        elif choice == "3":
            sysAd.delete_account(username)
            print("Account deleted successfully. returning to main menu.")
            pre_login_menu()
        elif choice == "4":
            return username  # Go back to the previous menu
        else:
            print("Invalid choice. Please try again.")



