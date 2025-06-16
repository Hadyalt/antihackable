import sqlite3
import time
from DbContext.DbContext import DbContext
from DbContext.crypto_utils import encrypt, decrypt, hash_password, verify_password
from DbContext.encrypted_logger import EncryptedLogger
from scooter import Scooter
from SuperAdmin import super_admin_menu as SuperMenu
from systemAdmin import system_admin_menu as SystemMenu
from serviceEngineer import ServiceEngineer_menu
from DbContext.backup_utils import create_backup, list_backups, restore_backup

DB_PATH = "data.db"

# === LOGIN ===
def login():
    logger = EncryptedLogger()
    max_attempts = 5
    # Use a persistent attribute to store timeout duration between login calls
    if not hasattr(login, "timeout_duration"):
        login.timeout_duration = 15  # start at 15 seconds
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
                # Reset timeout on successful login
                login.timeout_duration = 15
                return "superadmin" , "super_Admin"

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
                cursor.execute("SELECT password, role FROM User WHERE Username = ?", (found_enc_username,))
                result = cursor.fetchone()
                conn.close()
                if result:
                    stored_hash, role = result
                    if verify_password(password, stored_hash):
                        print(f"✅ Login successful. Welcome, {role}!")
                        logger.log_entry(username, "Login attempt", "Success", "No")
                        # Reset timeout on successful login
                        login.timeout_duration = 15
                        return role, username
                    else:
                        print("❌ Incorrect password.")
                        logger.log_entry(username, "Login attempt", "Incorrect password", "Yes" if attempt >= 4 else "No")
                else:
                    print("❌ Username not found.")
                    logger.log_entry(username, "Login attempt", "Username not found", "Yes" if attempt >= 4 else "No")
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
    print("\n" + "=" * 50)
    print(f"🛴 URBAN MOBILITY SYSTEM - Logged in as: {role.upper()}")
    print("=" * 50)
    print("Choose an option:\n")

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
            exit()
        else:
            print("Invalid choice.")
    elif role == "systemadmin":
        print("1. System Admin Menu")
        print("2. Backup & Restore")
        print("3. Exit")
        choice = input("Enter your choice: ")
        if choice == "1":
            SystemMenu.system_admin_menu(username)
        elif choice == "2":
            backup_menu(role)
        elif choice == "3":
            exit()
        else:
            print("Invalid choice.")
    elif role == "serviceengineer":
        ServiceEngineer_menu.main(username)
    else:
        print("Invalid role.")
        return

def backup_menu(role):
    print("\n=== BACKUP & RESTORE MENU ===")
    print("1. Create Backup")
    print("2. List Backups")
    print("3. Restore Backup")
    print("4. Exit Backup Menu")
    while True:
        choice = input("Enter your choice: ").strip()
        if choice == "1":
            backup_path = create_backup()
            print(f"Backup created: {backup_path}")
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
            print("Available backups:")
            for idx, b in enumerate(backups, 1):
                print(f"{idx}. {b}")
            sel = input("Select backup number to restore: ").strip()
            try:
                sel_idx = int(sel) - 1
                if sel_idx < 0 or sel_idx >= len(backups):
                    print("Invalid selection.")
                    continue
                # Super Admin can restore any, System Admin only the latest
                if role == "systemadmin" and sel_idx != len(backups) - 1:
                    print("System Admin can only restore the latest backup.")
                    continue
                restore_backup(backups[sel_idx])
                print("Restore complete. Please restart the application.")
                exit()
            except Exception as e:
                print(f"Restore failed: {e}")
        elif choice == "4":
            break
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
                    again = input("\nReturn to menu? (y/n): ").strip().lower()
                    if again != "y":
                        print("👋 Logging out...\n")
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
        pre_login_menu()
