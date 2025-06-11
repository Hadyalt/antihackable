from systemAdmin.system_admin import systemAdmin

def system_admin_menu():
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
            sysAd.create_service_engineer()
        elif choice == "8":
            print("Exiting...")
            break
        else:
            print("Invalid choice. Please try again.")