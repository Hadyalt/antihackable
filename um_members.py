import sqlite3
import hashlib
from DbContext.DbContext import DbContext
from scooter import Scooter
from SuperAdmin import super_admin_menu as SuperMenu

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
        return "super_admin"

    # DB login
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT password, role FROM users WHERE LOWER(username) = ?", (username.lower(),))
    result = cursor.fetchone()
    conn.close()

    if result:
        stored_hash, role = result
        if hash_password(password) == stored_hash:
            print(f"✅ Login successful. Welcome, {role}!")
            return role
        else:
            print("❌ Incorrect password.")
    else:
        print("❌ Username not found.")

    return None

# === ROLE-BASED MENU ===
def show_main_menu(role):
    print("\n" + "=" * 50)
    print(f"🛴 URBAN MOBILITY SYSTEM - Logged in as: {role.upper()}")
    print("=" * 50)
    print("Choose an option:\n")

    if role == "super_admin":
        SuperMenu.super_admin_menu()
    elif role == "system_admin":
        print("1. Manage Service Engineers")
        print("2. Manage Travellers")
        print("3. Manage Scooters")
        print("4. View Logs")
        print("5. Backup & Restore")
        print("6. Exit")
    elif role == "service_engineer":
        print("1. Update Scooter Info")
        print("2. Manage Travellers")
        print("3. Change My Password")
        print("4. Exit")
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
            role = login()
            if role:
                while True:
                    show_main_menu(role)
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
    while True:
        db_context = DbContext()
        db_context.initialize_database()
        pre_login_menu()
