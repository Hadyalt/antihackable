import sqlite3
from DbContext.DbContext import DbContext
from DbContext.crypto_utils import encrypt, decrypt, hash_password, verify_password
from scooter import Scooter
from SuperAdmin import super_admin_menu as SuperMenu
from systemAdmin import system_admin_menu as SystemMenu
from serviceEngineer import ServiceEngineer_menu
from DbContext.backup_utils import create_backup, list_backups, restore_backup


DB_PATH = "data.db"

# === LOGIN ===
def login():
    print("\n" + "=" * 50)
    print("🔐 URBAN MOBILITY - LOGIN")
    print("=" * 50)
    username = input("Username: ").strip()
    password = input("Password: ").strip()

    # Hardcoded super admin
    if username.lower() == "super_admin" and password == "Admin_123?":
        print("✅ Super Admin login successful.")
        return "superadmin" , "super_Admin"

    # DB login (encrypted username)
    enc_username = encrypt(username)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT password, role FROM User WHERE Username = ?", (enc_username,))
    result = cursor.fetchone()
    conn.close()

    if result:
        stored_hash, role = result
        if verify_password(password, stored_hash):
            print(f"✅ Login successful. Welcome, {role}!")
            return role, username
        else:
            print("❌ Incorrect password.")
    else:
        print("❌ Username not found.")

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
