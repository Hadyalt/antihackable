import sqlite3
import time
import os
import getpass
from DbContext.DbContext import DbContext
from DbContext.crypto_utils import encrypt, decrypt, hash_password, verify_password
from DbContext.encrypted_logger import EncryptedLogger, fernet
from Login.verification import Verification
from SuperAdmin import super_admin_menu as SuperMenu
from systemAdmin import system_admin_menu as SystemMenu
from serviceEngineer import ServiceEngineer_menu
from backup.backup_menu import backup_menu
from systemAdmin.system_admin import systemAdmin
from valid_in_out_put import sanitize_output,validate_input_user,validate_input_pass

DB_PATH = "data.db"


# === LOGIN ===
def login():
    logger = EncryptedLogger()
    max_attempts = 5
    # Use persistent attributes to store timeout duration and failed attempts per username
    if not hasattr(login, "timeout_duration"):
        login.timeout_duration = 15  # start at 15 seconds
    if not hasattr(login, "user_attempts"):
        login.user_attempts = {}  # {username: failed_attempts}
    while True:
        for attempt in range(1, max_attempts + 1):
            print("\n" + "=" * 50)
            print("🔐 URBAN MOBILITY - LOGIN")
            print("=" * 50)
            username = validate_input_user(input("Username: ").strip())
            password = validate_input_pass(getpass.getpass("Password: ").strip())

            # Hardcoded super admin
            if username == "super_admin" and password == "Admin_123?":
                print(sanitize_output("✅ Super Admin login successful."))
                logger.log_entry("super_admin", "Logged in", " ", "No")
                # Reset timeout and attempts on successful login
                login.timeout_duration = 15
                login.user_attempts.clear()
                return "superadmin", "super_admin"

            # Fetch all users and decrypt usernames
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("SELECT Username FROM User")
            users = cursor.fetchall()
            found_enc_username = None
            for (enc_username,) in users:
                try:
                    dec_username = decrypt(enc_username)
                    if dec_username == username:
                        found_enc_username = enc_username
                        break
                except Exception:
                    continue
            if not found_enc_username:
                # Generic error message
                print(sanitize_output("❌ Wrong username or password."))
                logger.log_entry(
                    username,
                    "Login attempt",
                    "Username not found",
                    "Yes" if attempt >= 4 else "No",
                )
                conn.close()
            else:
                # Now fetch password and role for the found encrypted username
                cursor.execute(
                    "SELECT password, role, IsActive FROM User WHERE Username = ?",
                    (found_enc_username,),
                )
                result = cursor.fetchone()
                if result:
                    stored_hash, role, is_active = result
                    if not is_active:
                        print(
                            sanitize_output(
                                "❌ This account is inactive. Please contact an administrator."
                            )
                        )
                        # Track and log every attempt to log in to an inactive account
                        login.user_attempts[username] = (
                            login.user_attempts.get(username, 0) + 1
                        )
                        logger.log_entry(
                            username,
                            "Login attempt",
                            f"Attempted login to inactive account (attempt {login.user_attempts[username]})",
                            "Yes",
                        )
                        conn.close()
                        # Increment the global attempt counter for timeout
                        if attempt < max_attempts:
                            print(
                                sanitize_output(
                                    f"Attempt {attempt} of {max_attempts}. Try again."
                                )
                            )
                            continue
                        else:
                            print(
                                sanitize_output(
                                    f"❌ Too many failed login attempts. Please wait {login.timeout_duration} seconds before trying again."
                                )
                            )
                            logger.log_entry(
                                username,
                                "Login attempt",
                                f"Max attempts reached - timeout {login.timeout_duration}s",
                                "Yes",
                            )
                            logger.log_entry(
                                username,
                                "Login timeout",
                                f"User timed out for {login.timeout_duration} seconds after 5 failed attempts",
                                "Yes",
                            )
                            time.sleep(login.timeout_duration)
                            login.timeout_duration *= (
                                2  # double the timeout for next time
                            )
                            break
                    if verify_password(password, stored_hash):
                        print(sanitize_output(f"✅ Login successful. Welcome, {role}!"))
                        logger.log_entry(username, "Login attempt", "Success", "No")
                        # Reset timeout and attempts on successful login
                        login.timeout_duration = 15
                        login.user_attempts.pop(username, None)
                        conn.close()
                        return role, username
                    else:
                        # Generic error message
                        print(sanitize_output("❌ Wrong username or password."))
                        logger.log_entry(
                            username,
                            "Login attempt",
                            "Incorrect password",
                            "Yes" if attempt >= 4 else "No",
                        )
                        # Track failed attempts for this username
                        login.user_attempts[username] = (
                            login.user_attempts.get(username, 0) + 1
                        )
                        # If 5 wrong attempts for a valid username, deactivate and log
                        if login.user_attempts[username] >= 5:
                            print(
                                sanitize_output(
                                    "❌ Too many failed attempts for this user. Account is now inactive."
                                )
                            )
                            logger.log_entry(
                                username,
                                "Account locked",
                                "User made 5 failed login attempts. Account set to inactive.",
                                "Yes",
                            )
                            cursor.execute(
                                "UPDATE User SET IsActive = 0 WHERE Username = ?",
                                (found_enc_username,),
                            )
                            conn.commit()
                            conn.close()
                            # Do not allow further attempts for this username in this session
                            break
                else:
                    # Generic error message
                    print(sanitize_output("❌ Wrong username or password."))
                    logger.log_entry(
                        username,
                        "Login attempt",
                        "Username not found",
                        "Yes" if attempt >= 4 else "No",
                    )
                conn.close()
            if attempt < max_attempts:
                print(
                    sanitize_output(f"Attempt {attempt} of {max_attempts}. Try again.")
                )
            else:
                print(
                    sanitize_output(
                        f"❌ Too many failed login attempts. Please wait {login.timeout_duration} seconds before trying again."
                    )
                )
                logger.log_entry(
                    username,
                    "Login attempt",
                    f"Max attempts reached - timeout {login.timeout_duration}s",
                    "Yes",
                )
                logger.log_entry(
                    username,
                    "Login timeout",
                    f"User timed out for {login.timeout_duration} seconds after 5 failed attempts",
                    "Yes",
                )
                time.sleep(login.timeout_duration)
                login.timeout_duration *= 2  # double the timeout for next time
                break  # restart login attempts after timeout
        return None, None


# === ROLE-BASED MENU ===
def show_main_menu(role, username):
    # Alert for new suspicious logs if superadmin or systemadmin
    if role in ["superadmin", "systemadmin"]:
        logger = EncryptedLogger()
        suspicious_new_log_count = 0
        if (
            hasattr(logger, "logfile_path")
            and logger.logfile_path
            and os.path.exists(logger.logfile_path)
        ):
            with open(logger.logfile_path, "r") as f:
                for line in f:
                    decrypted = fernet.decrypt(line.strip().encode()).decode()
                    parts = decrypted.split("|")
                    if (
                        len(parts) == 8
                        and parts[-1] == "new"
                        and parts[-2].lower() == "yes"
                    ):
                        suspicious_new_log_count += 1
        if suspicious_new_log_count > 0:
            print(
                sanitize_output(
                    f"\n⚠️  ALERT: There are {suspicious_new_log_count} new suspicious logs that need to be reviewed!\n"
                )
            )

    while True:
        print("\n" + sanitize_output("=" * 50))
        print(sanitize_output(f"🛴 URBAN MOBILITY SYSTEM - Logged in as: {role.upper()}"))
        print(sanitize_output("=" * 50))

        if role == "superadmin":
            print("[1] Super Admin Menu")
            print("[2] Backup & Restore")
            print("[3] Logout")
            print("[4] Exit")
            choice = input("Enter your choice: ")
            if choice == "1":
                SuperMenu.super_admin_menu(username)
            elif choice == "2":
                backup_menu(role)
            elif choice == "3":
                print(sanitize_output("👋 Logging out."))
                from um_members import pre_login_menu
                pre_login_menu()
                return
            elif choice == "4":
                print("👋 Exiting system.")
                exit()
            else:
                print(sanitize_output("Invalid choice."))
        elif role == "systemadmin":
            sysAd = systemAdmin()
            user = sysAd.get_username(username)
            if sysAd.check_reset_password(user, "systemadmin"):
                print(
                sanitize_output(
                    "You have a reset password, please reset it before proceeding."
                )
            )
                verified_password = False
                while not verified_password:
                    password = validate_input_pass(getpass.getpass(sanitize_output("Enter password: ")))
                    verified_password = Verification.verify_Password(password)
                hashed_password = hash_password(password)
                sysAd.reset_password_function(user, hashed_password, "systemadmin")
                sysAd.reset_resetted_password_check(user, "systemadmin")
                print(
                sanitize_output(
                    "Password reset completed. You can now proceed with the menu options."
                )
            )
                logger = EncryptedLogger()
                logger.log_entry(
                f"{username}",
                "Reset his own password",
                f"Username: {username} picked a new password after it was changed by a higher account",
                "No",
            )

            print("[1] System Admin Menu")
            print("[2] Backup & Restore")
            print("[3] Logout")
            print("[4] Exit")
            choice = input("Enter your choice: ")
            if choice == "1":
                SystemMenu.system_admin_menu(username)
            elif choice == "2":
                backup_menu(role, username)
            elif choice == "3":
                print("👋 Logging out.")
                from um_members import pre_login_menu
                logger.log_entry(f"{username}", "Logged out", f"Success", "No")
                pre_login_menu()
                return
            elif choice == "4":
                logger.log_entry(f"{username}", "Exited system", f"Success", "No")
                print("👋 Exiting system.")
                exit()
            else:
                print(sanitize_output("Invalid choice."))
        elif role == "serviceengineer":
            print("[1] Service Engineer Menu")
            print("[2] Logout")
            print("[3] Exit")
            choice = input("Enter your choice: ")
            if choice == "1":
                ServiceEngineer_menu.main(username)
            elif choice == "2":
                print("👋 Logging out.")
                from um_members import pre_login_menu
                pre_login_menu()
                return
            elif choice == "3":
                print("👋 Exiting system.")
                exit()
            else:
                print("Invalid choice.")
        else:
            print("Invalid role.")
            return

# === MAIN MENU BEFORE LOGIN ===
def pre_login_menu():
    while True:
        print(sanitize_output("=" * 50))
        print(sanitize_output("⚙️  URBAN MOBILITY CONSOLE"))
        print(sanitize_output("=" * 50))
        print(sanitize_output("[1] Login to System"))
        print(sanitize_output("[2] Exit"))

        choice = input(sanitize_output("Enter your choice: "))

        if choice == "1":
            role, username = login()
            if role:
                while True:
                    show_main_menu(role, username)
                    break
        elif choice == "2":
            print(sanitize_output("👋 Exiting system."))
            exit()
        else:
            print(sanitize_output("❌ Invalid choice."))


# === START APP ===
if __name__ == "__main__":
    db_context = DbContext()
    db_context.initialize_database()
    while True:
        try:
            pre_login_menu()
        except KeyboardInterrupt:
            print(sanitize_output("\n👋 Exiting system."))
            exit()
