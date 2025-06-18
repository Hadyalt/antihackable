import sqlite3
import time
import os
from DbContext.DbContext import DbContext
from DbContext.crypto_utils import encrypt, decrypt, hash_password, verify_password
from DbContext.encrypted_logger import EncryptedLogger, fernet
from Login.verification import Verification
from SuperAdmin import super_admin_menu as SuperMenu
from systemAdmin import system_admin_menu as SystemMenu
from serviceEngineer import ServiceEngineer_menu
from DbContext.backup_utils import create_backup, list_backups, restore_backup, delete_backup
from systemAdmin.system_admin import systemAdmin
from input_output_utils import validate_input, sanitize_output

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
            print(sanitize_output("\n" + "=" * 50))
            print(sanitize_output("🔐 URBAN MOBILITY - LOGIN"))
            print(sanitize_output("=" * 50))
            username = validate_input(input("Username: ").strip(), min_length=1, context="Login Username")
            password = validate_input(input("Password: ").strip(), min_length=1, context="Login Password")

            # Hardcoded super admin
            if username.lower() == "super_admin" and password == "Admin_123?":
                print(sanitize_output("✅ Super Admin login successful."))
                logger.log_entry("super_admin", "Logged in", " ", "No")
                # Reset timeout and attempts on successful login
                login.timeout_duration = 15
                login.user_attempts.clear()
                return "superadmin" , "super_admin"

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
                print(sanitize_output("❌ Username not found."))
                logger.log_entry(username, "Login attempt", "Username not found", "Yes" if attempt >= 4 else "No")
                conn.close()
            else:
                # Now fetch password and role for the found encrypted username
                cursor.execute("SELECT password, role, IsActive FROM User WHERE Username = ?", (found_enc_username,))
                result = cursor.fetchone()
                if result:
                    stored_hash, role, is_active = result
                    if not is_active:
                        print(sanitize_output("❌ This account is inactive. Please contact an administrator."))
                        # Track and log every attempt to log in to an inactive account
                        login.user_attempts[username] = login.user_attempts.get(username, 0) + 1
                        logger.log_entry(username, "Login attempt", f"Attempted login to inactive account (attempt {login.user_attempts[username]})", "Yes")
                        conn.close()
                        # Increment the global attempt counter for timeout
                        if attempt < max_attempts:
                            print(sanitize_output(f"Attempt {attempt} of {max_attempts}. Try again."))
                            continue
                        else:
                            print(sanitize_output(f"❌ Too many failed login attempts. Please wait {login.timeout_duration} seconds before trying again."))
                            logger.log_entry(username, "Login attempt", f"Max attempts reached - timeout {login.timeout_duration}s", "Yes")
                            logger.log_entry(username, "Login timeout", f"User timed out for {login.timeout_duration} seconds after 5 failed attempts", "Yes")
                            time.sleep(login.timeout_duration)
                            login.timeout_duration *= 2  # double the timeout for next time
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
                        print(sanitize_output("❌ Incorrect password."))
                        logger.log_entry(username, "Login attempt", "Incorrect password", "Yes" if attempt >= 4 else "No")
                        # Track failed attempts for this username
                        login.user_attempts[username] = login.user_attempts.get(username, 0) + 1
                        # If 5 wrong attempts for a valid username, deactivate and log
                        if login.user_attempts[username] >= 5:
                            print(sanitize_output("❌ Too many failed attempts for this user. Account is now inactive."))
                            logger.log_entry(username, "Account locked", "User made 5 failed login attempts. Account set to inactive.", "Yes")
                            cursor.execute("UPDATE User SET IsActive = 0 WHERE Username = ?", (found_enc_username,))
                            conn.commit()
                            conn.close()
                            # Do not allow further attempts for this username in this session
                            break
                else:
                    print(sanitize_output("❌ Username not found."))
                    logger.log_entry(username, "Login attempt", "Username not found", "Yes" if attempt >= 4 else "No")
                conn.close()
            if attempt < max_attempts:
                print(sanitize_output(f"Attempt {attempt} of {max_attempts}. Try again."))
            else:
                print(sanitize_output(f"❌ Too many failed login attempts. Please wait {login.timeout_duration} seconds before trying again."))
                logger.log_entry(username, "Login attempt", f"Max attempts reached - timeout {login.timeout_duration}s", "Yes")
                logger.log_entry(username, "Login timeout", f"User timed out for {login.timeout_duration} seconds after 5 failed attempts", "Yes")
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
        if hasattr(logger, 'logfile_path') and logger.logfile_path and os.path.exists(logger.logfile_path):
            with open(logger.logfile_path, "r") as f:
                for line in f:
                    decrypted = fernet.decrypt(line.strip().encode()).decode()
                    parts = decrypted.split("|")
                    if len(parts) == 8 and parts[-1] == "new" and parts[-2].lower() == "yes":
                        suspicious_new_log_count += 1
        if suspicious_new_log_count > 0:
            print(sanitize_output(f"\n⚠️  ALERT: There are {suspicious_new_log_count} new suspicious logs that need to be reviewed!\n"))
    print(sanitize_output("\n" + "=" * 50))
    print(sanitize_output(f"🛴 URBAN MOBILITY SYSTEM - Logged in as: {role.upper()}"))
    print(sanitize_output("=" * 50))
    if role == "superadmin":
        print(sanitize_output("1. Super Admin Menu"))
        print(sanitize_output("2. Backup & Restore"))
        print(sanitize_output("3. Exit"))
        try:
            choice = validate_input(input("Enter your choice: ").strip(), pattern=r"^[1-3]$", context="SuperAdmin Main Menu Choice")
        except ValueError as e:
            print(sanitize_output(f"Invalid input: {e}"))
            return
        if choice == "1":
            SuperMenu.super_admin_menu(username)
        elif choice == "2":
            backup_menu(role)
        elif choice == "3":
            print(sanitize_output("👋 Logging out."))
            return
        else:
            print(sanitize_output("Invalid choice."))
    elif role == "systemadmin":
        sysAd= systemAdmin()
        user = sysAd.get_username(username)
        if (sysAd.check_reset_password(user, "systemadmin")):
            print("You have a reset password, please reset it before proceeding.")
            verified_password = False
            while not verified_password:
                password = input("Enter password: ")
                verified_password = Verification.verify_Password(password)
            hashed_password = hash_password(password)
            sysAd.reset_password_function(user, hashed_password, "systemadmin")
            sysAd.reset_resetted_password_check(user, "systemadmin")
            print("Password reset completed. You can now proceed with the menu options.")
            logger = EncryptedLogger()
            logger.log_entry(f"{username}", "Reset his own password", f"Username: {username} picked a new password after it was changed by a higher account", "No")

        print(sanitize_output("1. System Admin Menu"))
        print(sanitize_output("2. Backup & Restore"))
        print(sanitize_output("3. Exit"))
        try:
            choice = validate_input(input("Enter your choice: ").strip(), pattern=r"^[1-3]$", context="SystemAdmin Main Menu Choice")
        except ValueError as e:
            print(sanitize_output(f"Invalid input: {e}"))
            return
        if choice == "1":
            SystemMenu.system_admin_menu(username)
        elif choice == "2":
            backup_menu(role)
        elif choice == "3":
            exit()
        else:
            print(sanitize_output("Invalid choice."))
    elif role == "serviceengineer":
        ServiceEngineer_menu.main(username)
    else:
        print(sanitize_output("Invalid role."))
        return

def backup_menu(role, username=None):
    while True:
        print(sanitize_output("\n=== BACKUP & RESTORE MENU ==="))
        print(sanitize_output("1. Create Backup"))
        print(sanitize_output("2. List Backups"))
        print(sanitize_output("3. Restore Backup"))
        print(sanitize_output("4. Delete Backup"))
        print(sanitize_output("5. Exit Backup Menu"))
        try:
            choice = validate_input(input("Enter your choice: ").strip(), pattern=r"^[1-5]$", context="Backup Menu Choice")
        except ValueError as e:
            print(sanitize_output(f"Invalid input: {e}"))
            continue
        if choice == "1":
            backup_path = create_backup(username)
            print(sanitize_output(f"Backup created: {backup_path}"))
        elif choice == "2":
            backups = list_backups()
            if backups:
                print(sanitize_output("Available backups:"))
                for b in backups:
                    print(sanitize_output(f"- {b}"))
            else:
                print(sanitize_output("No backups found."))
        elif choice == "3":
            backups = list_backups()
            if not backups:
                print(sanitize_output("No backups to restore."))
                continue
            print(sanitize_output("Available backups:"))
            for idx, b in enumerate(backups, 1):
                print(sanitize_output(f"{idx}. {b}"))
            sel = validate_input(input("Select backup number to restore: ").strip(), pattern=r"^\d+$", context="Backup Restore Selection")
            try:
                sel_idx = int(sel) - 1
                if sel_idx < 0 or sel_idx >= len(backups):
                    print(sanitize_output("Invalid selection."))
                    continue
                if role == "systemadmin" and sel_idx != len(backups) - 1:
                    print(sanitize_output("System Admin can only restore the latest backup."))
                    continue
                restore_backup(backups[sel_idx], username)
                print(sanitize_output("Restore complete. Please restart the application."))
                exit()
            except Exception as e:
                print(sanitize_output(f"Restore failed: {e}"))
        elif choice == "4":
            backups = list_backups()
            if not backups:
                print(sanitize_output("No backups to delete."))
                continue
            print(sanitize_output("Available backups:"))
            for idx, b in enumerate(backups, 1):
                print(sanitize_output(f"{idx}. {b}"))
            sel = validate_input(input("Select backup number to delete: ").strip(), pattern=r"^\d+$", context="Backup Delete Selection")
            try:
                sel_idx = int(sel) - 1
                if sel_idx < 0 or sel_idx >= len(backups):
                    print(sanitize_output("Invalid selection."))
                    continue
                delete_backup(backups[sel_idx], username)
                print(sanitize_output(f"Backup deleted: {backups[sel_idx]}"))
            except Exception as e:
                print(sanitize_output(f"Delete failed: {e}"))
        elif choice == "5":
            return
        else:
            print(sanitize_output("Invalid choice."))

# === MAIN MENU BEFORE LOGIN ===
def pre_login_menu():
    while True:
        print(sanitize_output("=" * 50))
        print(sanitize_output("⚙️  URBAN MOBILITY CONSOLE"))
        print(sanitize_output("=" * 50))
        print(sanitize_output("1. Login to System"))
        print(sanitize_output("2. Exit"))
        try:
            choice = validate_input(input("Enter your choice: ").strip(), pattern=r"^[1-2]$", context="Pre-login Menu Choice")
        except ValueError as e:
            print(sanitize_output(f"Invalid input: {e}"))
            continue
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
            print("\n👋 Exiting system.")
            exit()
