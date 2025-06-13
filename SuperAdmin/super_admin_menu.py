from SuperAdmin.super_admin import SuperAdmin
from systemAdmin.system_admin import systemAdmin
from traveller.Traveller_menu import traveller_menu


def super_admin_menu():
    while True:
        print("\nSUPER ADMIN MENU")
        print("1. Manage System Admins")
        print("2. Manage Service Engineers")
        print("3. Manage Travellers")
        print("4. Manage Scooters")
        print("5. View Logs")
        print("6. Backup & Restore")
        print("7. Exit")
        choice = input("\nEnter your choice: ")
        
        if choice == "1":
            super_admin_system_admin_menu()
        elif choice == "2":
            super_admin_service_engineer_menu()
        elif choice == "3":
            traveller_menu()
        elif choice == "7":
            print("Exiting...")
            break
        else:
            print("Invalid choice. Please try again.")

def super_admin_service_engineer_menu():
    sysAd = systemAdmin()
    
    while True:
        print("\nSERVICE ENGINEER MANAGEMENT")
        print("1. Create Service Engineer Account")
        
        print("5. Go Back")
        
        choice = input("\nEnter your choice: ")
        
        if choice == "1":
            print("\n-- Create System Admin --")
            sysAd.create_service_engineer()
        elif choice == "2":
            print("Updating existing System Admin Account...")
            
        elif choice == "3":
            print("Deleting System Admin Account...")
            
        elif choice == "4":
            print("Resetting password for existing System Admin Account...")
            # Implement password reset logic here
        elif choice == "5":
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
        print("4. Reset the password for an existing System Admin Account")
        print("5. Go Back")
        
        choice = input("\nEnter your choice: ")
        
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
            print("Resetting password for existing System Admin Account...")
            # Implement password reset logic here
        elif choice == "5":
            break
        else:
            print("Invalid choice. Please try again.")
