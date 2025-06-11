import sqlite3
import hashlib
from DbContext.DbContext import DbContext
from scooter import Scooter
from SuperAdmin import super_admin_menu as SuperMenu
from systemAdmin import system_admin_menu as SystemMenu
from serviceEngineer import ServiceEngineer_menu


DB_PATH = "data.db"

# === SECURITY ===
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

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
        return "superadmin"

    # DB login
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT password, role FROM User WHERE LOWER(username) = ?", (username.lower(),))
    result = cursor.fetchone()
    conn.close()

    if result:
        stored_hash, role = result
        if hash_password(password) == stored_hash:
            print(f"✅ Login successful. Welcome, {role}!")
            return role, username
        else:
            print("❌ Incorrect password.")
    else:
        print("❌ Username not found.")

    return None

# === ROLE-BASED MENU ===
def show_main_menu(role, username):
    print("\n" + "=" * 50)
    print(f"🛴 URBAN MOBILITY SYSTEM - Logged in as: {role.upper()}")
    print("=" * 50)
    print("Choose an option:\n")

    if role == "superadmin":
        SuperMenu.super_admin_menu()
    elif role == "systemadmin":
        SystemMenu.system_admin_menu()
    elif role == "service_engineer":
        ServiceEngineer_menu(username)
    else:
        print("Invalid role.")
        return
    choice = input("\nEnter your choice: ")

        

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
            role,username = login()
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
