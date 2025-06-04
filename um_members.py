from DbContext.DbContext import DbContext
from scooter import Scooter

def main_menu():
    print("Choose an option:")
    print("1. Initialize database")
    print("2. Go to scooter.py")
    choice = input("Enter your choice (1 or 2): ")
    if choice == "1":
        db_context = DbContext()
        db_context.initialize_database()
        print("Database initialized successfully.")
    elif choice == "2":
        Scooter.main()
    else:
        print("Invalid choice.")

if __name__ == "__main__":
    main_menu()