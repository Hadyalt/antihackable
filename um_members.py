import sqlite3
import time
import os
import random
import string
from DbContext.DbContext import DbContext
from DbContext.crypto_utils import encrypt, decrypt, hash_password, verify_password
from DbContext.encrypted_logger import EncryptedLogger, fernet
from Login.verification import Verification
from scooter import Scooter
from SuperAdmin import super_admin_menu as SuperMenu
from systemAdmin import system_admin_menu as SystemMenu
from serviceEngineer import ServiceEngineer_menu
from DbContext.backup_utils import create_backup, list_backups, restore_backup, delete_backup
from systemAdmin.system_admin import systemAdmin

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
            username = input("Username: ").strip()
            password = input("Password: ").strip()

            # Hardcoded super admin
            if username.lower() == "super_admin" and password == "Admin_123?":
                print("✅ Super Admin login successful.")
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
                print("❌ Username not found.")
                logger.log_entry(username, "Login attempt", "Username not found", "Yes" if attempt >= 4 else "No")
                conn.close()
            else:
                # Now fetch password and role for the found encrypted username
                cursor.execute("SELECT password, role, IsActive FROM User WHERE Username = ?", (found_enc_username,))
                result = cursor.fetchone()
                if result:
                    stored_hash, role, is_active = result
                    if not is_active:
                        print("❌ This account is inactive. Please contact an administrator.")
                        # Track and log every attempt to log in to an inactive account
                        login.user_attempts[username] = login.user_attempts.get(username, 0) + 1
                        logger.log_entry(username, "Login attempt", f"Attempted login to inactive account (attempt {login.user_attempts[username]})", "Yes")
                        conn.close()
                        # Increment the global attempt counter for timeout
                        if attempt < max_attempts:
                            print(f"Attempt {attempt} of {max_attempts}. Try again.")
                            continue
                        else:
                            print(f"❌ Too many failed login attempts. Please wait {login.timeout_duration} seconds before trying again.")
                            logger.log_entry(username, "Login attempt", f"Max attempts reached - timeout {login.timeout_duration}s", "Yes")
                            logger.log_entry(username, "Login timeout", f"User timed out for {login.timeout_duration} seconds after 5 failed attempts", "Yes")
                            time.sleep(login.timeout_duration)
                            login.timeout_duration *= 2  # double the timeout for next time
                            break
                    if verify_password(password, stored_hash):
                        print(f"✅ Login successful. Welcome, {role}!")
                        logger.log_entry(username, "Login attempt", "Success", "No")
                        # Reset timeout and attempts on successful login
                        login.timeout_duration = 15
                        login.user_attempts.pop(username, None)
                        conn.close()
                        return role, username
                    else:
                        print("❌ Incorrect password.")
                        logger.log_entry(username, "Login attempt", "Incorrect password", "Yes" if attempt >= 4 else "No")
                        # Track failed attempts for this username
                        login.user_attempts[username] = login.user_attempts.get(username, 0) + 1
                        # If 5 wrong attempts for a valid username, deactivate and log
                        if login.user_attempts[username] >= 5:
                            print("❌ Too many failed attempts for this user. Account is now inactive.")
                            logger.log_entry(username, "Account locked", "User made 5 failed login attempts. Account set to inactive.", "Yes")
                            cursor.execute("UPDATE User SET IsActive = 0 WHERE Username = ?", (found_enc_username,))
                            conn.commit()
                            conn.close()
                            # Do not allow further attempts for this username in this session
                            break
                else:
                    print("❌ Username not found.")
                    logger.log_entry(username, "Login attempt", "Username not found", "Yes" if attempt >= 4 else "No")
                conn.close()
            if attempt < max_attempts:
                print(f"Attempt {attempt} of {max_attempts}. Try again.")
            else:
                print(f"❌ Too many failed login attempts. Please wait {login.timeout_duration} seconds before trying again.")
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
            print(f"\n⚠️  ALERT: There are {suspicious_new_log_count} new suspicious logs that need to be reviewed!\n")

    print("\n" + "=" * 50)
    print(f"🛴 URBAN MOBILITY SYSTEM - Logged in as: {role.upper()}")
    print("=" * 50)

    if role == "superadmin":
        print("1. Super Admin Menu")
        print("2. Backup & Restore")
        print("3. Exit")
        choice = input("Enter your choice: ")
        if choice == "1":
            SuperMenu.super_admin_menu(username)
        elif choice == "2":
            backup_menu(role)
        elif choice == "3":
            print("👋 Logging out.")
            return
        else:
            print("Invalid choice.")
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

        print("1. System Admin Menu")
        print("2. Backup & Restore")
        print("3. Exit")
        choice = input("Enter your choice: ")
        if choice == "1":
            SystemMenu.system_admin_menu(username)
        elif choice == "2":
            backup_menu(role, username)
        elif choice == "3":
            exit()
        else:
            print("Invalid choice.")
    elif role == "serviceengineer":
        ServiceEngineer_menu.main(username)
    else:
        print("Invalid role.")
        return

def generate_restore_code(length=12):
    """Generate a random alphanumeric restore code."""
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

def add_restore_code(backup_name, system_admin, db_path=DB_PATH):
    code = generate_restore_code()
    enc_backup_name = encrypt(backup_name)
    enc_system_admin = encrypt(system_admin)
    enc_code = encrypt(code)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO backup_recovery_list (backup_name, system_admin, recovery_code, used)
        VALUES (?, ?, ?, 0)
    """, (enc_backup_name, enc_system_admin, enc_code))
    conn.commit()
    conn.close()
    return code

def revoke_restore_code(backup_name, system_admin, db_path=DB_PATH):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT id, backup_name, system_admin, used FROM backup_recovery_list")
    rows = cursor.fetchall()
    for row in rows:
        row_id, enc_backup_name, enc_system_admin, used = row
        if used == 0 and decrypt(enc_backup_name) == backup_name and decrypt(enc_system_admin) == system_admin:
            cursor.execute("""
                UPDATE backup_recovery_list
                SET used = 1, used_at = datetime('now')
                WHERE id = ?
            """, (row_id,))
            conn.commit()
            conn.close()
            return True
    conn.close()
    return False

def validate_restore_code(backup_name, system_admin, code, db_path=DB_PATH):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT id, backup_name, system_admin, recovery_code, used FROM backup_recovery_list")
    rows = cursor.fetchall()
    for row in rows:
        row_id, enc_backup_name, enc_system_admin, enc_code, used = row
        if (used == 0 and decrypt(enc_backup_name) == backup_name and
            decrypt(enc_system_admin) == system_admin and decrypt(enc_code) == code):
            cursor.execute("""
                UPDATE backup_recovery_list
                SET used = 1, used_at = datetime('now')
                WHERE id = ?
            """, (row_id,))
            conn.commit()
            conn.close()
            return True
    conn.close()
    return False

def get_system_admins(db_path=DB_PATH):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT Username FROM User WHERE Role = 'systemadmin' AND IsActive = 1")
    admins = [decrypt(row[0]) for row in cursor.fetchall()]
    conn.close()
    return admins

def get_decrypted_backups():
    backups = list_backups()
    # backups on disk are not encrypted, but in DB they are
    return backups

def backup_menu(role, username=None):
    while True:
        print("\n=== BACKUP & RESTORE MENU ===")
        print("1. Create Backup")
        print("2. List Backups")
        print("3. Restore Backup")
        print("4. Delete Backup")
        if role == "superadmin":
            print("5. Generate Restore-Code for System Admin")
            print("6. Revoke Restore-Code")
            print("7. Exit Backup Menu")
            valid_choices = ["1", "2", "3", "4", "5", "6", "7"]
        else:
            print("5. Exit Backup Menu")
            valid_choices = ["1", "2", "3", "4", "5"]
        choice = input("Enter your choice: ").strip()
        if choice not in valid_choices:
            print("Invalid choice. Please enter a valid option.")
            continue
        if choice == "1":
            backup_path = create_backup(username)
            print(f"Backup created: {backup_path}")
            if role == "superadmin":
                while True:
                    add_code = input("Do you want to add a recovery code for a System Admin? (yes/no): ").strip().lower()
                    if add_code not in ["yes", "no"]:
                        print("Invalid input. Please enter 'yes' or 'no'.")
                        continue
                    if add_code == "no":
                        break
                    admins = get_system_admins()
                    if not admins:
                        print("No active System Admins found.")
                        break
                    while True:
                        print("System Admins:")
                        for idx, admin in enumerate(admins, 1):
                            print(f"{idx}. {admin}")
                        sel = input("Select System Admin number: ").strip()
                        if not sel.isdigit() or int(sel) < 1 or int(sel) > len(admins):
                            print("Invalid selection. Please enter a valid number.")
                            continue
                        sel_idx = int(sel) - 1
                        try:
                            code = add_restore_code(os.path.basename(backup_path), admins[sel_idx])
                            print(f"Restore code for {admins[sel_idx]} and backup {os.path.basename(backup_path)}: {code}")
                            break
                        except Exception as e:
                            print(f"Failed to generate restore code: {e}")
                    break
        elif choice == "2":
            backups = list_backups()
            if backups:
                print("Available backups:")
                for b in backups:
                    print(f"- {b}")
            else:
                print("No backups found.")
        elif choice == "3":
            backups = list_backups()
            if not backups:
                print("No backups to restore.")
                continue
            while True:
                print("Available backups:")
                for idx, b in enumerate(backups, 1):
                    print(f"{idx}. {b}")
                sel = input("Select backup number to restore: ").strip()
                if not sel.isdigit() or int(sel) < 1 or int(sel) > len(backups):
                    print("Invalid selection. Please enter a valid number.")
                    continue
                sel_idx = int(sel) - 1
                if role == "systemadmin":
                    code = input("Enter your restore code: ").strip()
                    if not validate_restore_code(backups[sel_idx], username, code):
                        print("Invalid or already used restore code.")
                        continue
                try:
                    restore_backup(backups[sel_idx], username)
                    print("Restore complete. Please restart the application.")
                    exit()
                except Exception as e:
                    print(f"Restore failed: {e}")
                break
        elif choice == "4":
            backups = list_backups()
            if not backups:
                print("No backups to delete.")
                continue
            while True:
                print("Available backups:")
                for idx, b in enumerate(backups, 1):
                    print(f"{idx}. {b}")
                sel = input("Select backup number to delete: ").strip()
                if not sel.isdigit() or int(sel) < 1 or int(sel) > len(backups):
                    print("Invalid selection. Please enter a valid number.")
                    continue
                sel_idx = int(sel) - 1
                try:
                    delete_backup(backups[sel_idx], username)
                    print(f"Backup deleted: {backups[sel_idx]}")
                except Exception as e:
                    print(f"Delete failed: {e}")
                break
        elif role == "superadmin" and choice == "5":
            backups = list_backups()
            if not backups:
                print("No backups available.")
                continue
            while True:
                print("Available backups:")
                for idx, b in enumerate(backups, 1):
                    print(f"{idx}. {b}")
                sel = input("Select backup number: ").strip()
                if not sel.isdigit() or int(sel) < 1 or int(sel) > len(backups):
                    print("Invalid selection. Please enter a valid number.")
                    continue
                sel_idx = int(sel) - 1
                admins = get_system_admins()
                if not admins:
                    print("No active System Admins found.")
                    break
                while True:
                    print("System Admins:")
                    for idx, admin in enumerate(admins, 1):
                        print(f"{idx}. {admin}")
                    admin_sel = input("Select System Admin number: ").strip()
                    if not admin_sel.isdigit() or int(admin_sel) < 1 or int(admin_sel) > len(admins):
                        print("Invalid selection. Please enter a valid number.")
                        continue
                    admin_idx = int(admin_sel) - 1
                    try:
                        code = add_restore_code(backups[sel_idx], admins[admin_idx])
                        print(f"Restore code for {admins[admin_idx]} and backup {backups[sel_idx]}: {code}")
                        break
                    except Exception as e:
                        print(f"Failed to generate restore code: {e}")
                break
        elif role == "superadmin" and choice == "6":
            backups = list_backups()
            if not backups:
                print("No backups available.")
                continue
            while True:
                print("Available backups:")
                for idx, b in enumerate(backups, 1):
                    print(f"{idx}. {b}")
                sel = input("Select backup number: ").strip()
                if not sel.isdigit() or int(sel) < 1 or int(sel) > len(backups):
                    print("Invalid selection. Please enter a valid number.")
                    continue
                sel_idx = int(sel) - 1
                admins = get_system_admins()
                if not admins:
                    print("No active System Admins found.")
                    break
                while True:
                    print("System Admins:")
                    for idx, admin in enumerate(admins, 1):
                        print(f"{idx}. {admin}")
                    admin_sel = input("Select System Admin number: ").strip()
                    if not admin_sel.isdigit() or int(admin_sel) < 1 or int(admin_sel) > len(admins):
                        print("Invalid selection. Please enter a valid number.")
                        continue
                    admin_idx = int(admin_sel) - 1
                    try:
                        if revoke_restore_code(backups[sel_idx], admins[admin_idx]):
                            print(f"Restore code for {admins[admin_idx]} and backup {backups[sel_idx]} revoked.")
                        else:
                            print("No active restore code found to revoke.")
                        break
                    except Exception as e:
                        print(f"Failed to revoke restore code: {e}")
                break
        elif (role == "superadmin" and choice == "7") or (role != "superadmin" and choice == "5"):
            return
        else:
            print("Invalid choice.")

# === MAIN MENU BEFORE LOGIN ===
def pre_login_menu():
    while True:
        print("=" * 50)
        print("⚙️  URBAN MOBILITY CONSOLE")
        print("=" * 50)
        print("1. Login to System")
        print("2. Exit")

        choice = input("Enter your choice: ")

        if choice == "1":
            role, username = login()
            if role:
                while True:
                    show_main_menu(role, username)
                    break
        elif choice == "2":
            print("👋 Exiting system.")
            exit()
        else:
            print("❌ Invalid choice.")

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
