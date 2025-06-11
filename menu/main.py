# from Login.verification import Verification
# from SuperAdmin.super_admin import SuperAdmin

# def display_menu():
#         print("Welcome to the Main Menu")
#         print("1. Create a System Admin Account")
#         print("2. Exit")

# def run():
#     display_menu()
#     choice = input("Enter your choice: ")
#     if choice == '1':
#         super_admin = SuperAdmin()
#         verified_username = False
#         verified_password = False
#         while (not verified_username):
#             user_name = input("Enter the username for the new System Admin: ")
#             verified_username = Verification.verify_UserName(user_name)
#         while (not verified_password):
#             password = input("Enter the password for the new System Admin: ")
#             verified_password = Verification.verify_Password(password)
#         super_admin.create_system_admin(user_name, password)
#         print(f"System Admin account '{user_name}' created successfully.")
#     elif choice == '2':
#         print("Exiting...")
#         exit()
#     else:
#         print("Invalid choice, please try again.")

