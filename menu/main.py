from SuperAdmin.super_admin import SuperAdmin

class MainMenu:
    def display_menu(self):
        print("Welcome to the Main Menu")
        print("1. Create a System Admin Account")
        print("2. Exit")

    def run(self):
        self.display_menu()
        choice = input("Enter your choice: ")
        if choice == '1':
            user_name = input("Enter the username for the new System Admin: ")
            password = input("Enter the password for the new System Admin: ")
            self.super_admin = SuperAdmin(user_name, password)
            self.super_admin.create_system_admin(user_name, password)
            print(f"System Admin account '{user_name}' created successfully.")
        elif choice == '2':
            print("Exiting...")
            exit()
        else:
            print("Invalid choice, please try again.")

