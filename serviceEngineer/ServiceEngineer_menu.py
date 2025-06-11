from Login.verification import Verification
from serviceEngineer.ServiceEngineer import ServiceEngineer


def display_menu():
    print("\n==== Service Engineer Menu ====")
    print("1. Update Scooter Info")
    print("2. Manage Travellers")
    print("3. Change My Password")
    print("4. Exit")
    return input("Enter your choice (1-4): ").strip()


def reset_password_flow(engineer, current_user):
    print("\n** Password Reset **")
    verified_password = False
    while not verified_password:
        password = input("Enter new password: ")
        verified_password = Verification.verify_Password(password)
        confirm_password = input("Confirm new password: ")
        if confirm_password != password:
            print("Error: Passwords do not match!")
            print("Process cancelled.")
            break
    engineer.reset_password(current_user, password)
    print("Password reset completed. Check system messages for status.")


def main(username):
    # Get logged-in service engineer's username (from session/auth system)
    current_user = username  # Replace with actual logged-in username

    engineer = ServiceEngineer()

    while True:
        choice = display_menu()

        if choice == "3":
            reset_password_flow(engineer, current_user)

        elif choice == "4":
            print("Exiting Service Engineer Portal. Goodbye!")
            break

        else:
            print("Invalid selection. Please choose 1 or 2.")


if __name__ == "__main__":
    main()
