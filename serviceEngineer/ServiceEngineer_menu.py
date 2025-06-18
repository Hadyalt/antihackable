from DbContext.encrypted_logger import EncryptedLogger
from Login.verification import Verification
from serviceEngineer.ServiceEngineer import ServiceEngineer
from scooter import Scooter
from systemAdmin.system_admin import systemAdmin
from DbContext.crypto_utils import encrypt, decrypt, hash_password, verify_password
from input_output_utils import validate_input, sanitize_output



def display_menu():
    print(sanitize_output("\n==== Service Engineer Menu ===="))
    print(sanitize_output("1. Scooter Menu"))
    print(sanitize_output("2. Change My Password"))
    print(sanitize_output("3. Exit"))
    try:
        choice = validate_input(input("Enter your choice (1-3): ").strip(), pattern=r"^[1-3]$", context="Service Engineer Menu Choice")
    except ValueError as e:
        print(sanitize_output(f"Invalid input: {e}"))
        return None
    return choice


def reset_password_flow(current_user):
    engineer = ServiceEngineer()
    print(sanitize_output("\n** Password Reset **"))
    verified_password = False
    while not verified_password:
        password = input("Enter new password: ")
        verified_password = Verification.verify_Password(password)
        confirm_password = input("Confirm new password: ")
        if confirm_password != password:
            print(sanitize_output("Error: Passwords do not match!"))
            print(sanitize_output("Process cancelled."))
            break
    engineer.reset_password(current_user, password)
    print(sanitize_output("Password reset completed. Check system messages for status."))
    logger = EncryptedLogger()
    logger.log_entry(f"{current_user}", "Changed his own password", f" ", "No")


def main(username):
    # Get logged-in service engineer's username (from session/auth system)
    current_user = username  # Replace with actual logged-in username
    sysAd= systemAdmin()
    user = sysAd.get_username(username)
    if (sysAd.check_reset_password(user, "serviceengineer")):
        print(sanitize_output("You have a reset password, please reset it before proceeding."))
        verified_password = False
        while not verified_password:
            password = input("Enter password: ")
            verified_password = Verification.verify_Password(password)
        hashed_password = hash_password(password)
        print(sanitize_output(hashed_password))
        sysAd.reset_password_function(user, hashed_password, "serviceengineer")
        sysAd.reset_resetted_password_check(user, "serviceengineer")
        print(sanitize_output("Password reset completed. You can now proceed with the menu options."))
        logger = EncryptedLogger()
        logger.log_entry(f"{username}", "Reset his own password", f"Username: {username} picked a new password after it was changed by a higher account", "No")
    while True:
        choice = display_menu()
        if not choice:
            continue
        if choice == "1":
            Scooter.main("serviceengineer", current_user)
        elif choice == "2":
            reset_password_flow(current_user)
        elif choice == "3":
            print(sanitize_output("Exiting Service Engineer Portal. Goodbye!"))
            break
        else:
            print(sanitize_output("Invalid selection. Please choose a number between 1 and 3."))


if __name__ == "__main__":
    main()
