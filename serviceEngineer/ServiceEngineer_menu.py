from DbContext.encrypted_logger import EncryptedLogger
from Login.verification import Verification
from serviceEngineer.ServiceEngineer import ServiceEngineer
from scooter import Scooter
from systemAdmin.system_admin import systemAdmin
from DbContext.crypto_utils import encrypt, decrypt, hash_password, verify_password


def display_menu():
    print("\n==== Service Engineer Menu ====")
    print("1. Scooter Menu")
    print("2. Change My Password")
    print("3. Exit")
    return input("Enter your choice (1-3): ").strip()


def reset_password_flow(current_user):
    engineer = ServiceEngineer()
    sysAd = systemAdmin()
    if (sysAd.confirm_password(current_user)):
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
        logger = EncryptedLogger()
        logger.log_entry(f"{current_user}", "Changed his own password", f" ", "No")
    else:
        logger = EncryptedLogger()
        logger.log_entry(f"{current_user}", "Too many wrong password attempts", f"Could not confirm his own identity", "Yes")
        from um_members import pre_login_menu
        pre_login_menu()


def main(username):
    # Get logged-in service engineer's username (from session/auth system)
    current_user = username  # Replace with actual logged-in username
    sysAd= systemAdmin()
    user = sysAd.get_username(username)
    if (sysAd.check_reset_password(user, "serviceengineer")):
        print("You have a reset password, please reset it before proceeding.")
        verified_password = False
        while not verified_password:
            password = input("Enter password: ")
            verified_password = Verification.verify_Password(password)
        hashed_password = hash_password(password)
        sysAd.reset_password_function(user, hashed_password, "serviceengineer")
        sysAd.reset_resetted_password_check(user, "serviceengineer")
        print("Password reset completed. You can now proceed with the menu options.")
        logger = EncryptedLogger()
        logger.log_entry(f"{username}", "Reset his own password", f"Username: {username} picked a new password after it was changed by a higher account", "No")

    while True:
        choice = display_menu()
        if choice == "1":
            Scooter.main("serviceengineer", current_user)
        elif choice == "2":
            reset_password_flow(current_user)
        elif choice == "3":
            print("Exiting Service Engineer Portal. Goodbye!")
            break
        else:
            print("Invalid selection. Please choose a number between 1 and 3.")


if __name__ == "__main__":
    main()
