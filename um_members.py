import sqlite3
import hashlib
from DbContext.DbContext import DbContext
from scooter import Scooter

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
        print("1. Manage System Admins")
        print("2. Manage Service Engineers")
        print("3. Manage Travellers")
        print("4. Manage Scooters")
        print("5. View Logs")
        print("6. Backup & Restore")
        print("7. Exit")
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
    if role == "super_admin":
        print(f"You selected option {choice} for managing system Administrators.")
        print("1. Create System Admin Account")
        print("2. Update existing System Admin Account")
        print("3. Delete System Admin Account")
        print("4. Reset the password for an existing System Admin Account")
        

        

# === MAIN MENU BEFORE LOGIN ===
def pre_login_menu():
    print("=" * 50)
    print("⚙️  URBAN MOBILITY CONSOLE")
    print("=" * 50)
    print("1. Initialize Database")
    print("2. Login to System")
    print("3. Run scooter.py")
    print("4. Exit")

    choice = input("Enter your choice: ")

    if choice == "1":
        db_context = DbContext()
        db_context.initialize_database()
        print("✅ Database initialized.")
    elif choice == "2":
        role = login()
        if role:
            while True:
                show_main_menu(role)
                again = input("\nReturn to menu? (y/n): ").strip().lower()
                if again != "y":
                    print("👋 Logging out...\n")
                    break
    elif choice == "3":
        Scooter.main()
    elif choice == "4":
        print("👋 Exiting system.")
        exit()
    else:
        print("❌ Invalid choice.")

# === START APP ===
if __name__ == "__main__":
    while True:
        pre_login_menu()
