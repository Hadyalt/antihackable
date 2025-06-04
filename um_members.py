from menu import main
from scooter import Scooter
from DbContext.DbContext import DbContext
import os

def main_menu():
    print("Choose an option:")
    print("1. Initialize database")
    print("2. Go to scooter.py")
    print("3. Go to SuperAdmin menu")
    choice = input("Enter your choice (1 or 2): ")
    if choice == "1":
        db_context = DbContext()
        db_context.initialize_database()
        print("Database initialized successfully.")
    elif choice == "2":
        Scooter.main()
    elif choice == "3":
        main.run()

    else:
        print("Invalid choice.")

if __name__ == "__main__":
    main_menu()