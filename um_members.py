from DbContext.DbContext import DbContext
from menu.main import MainMenu


if __name__ == "__main__":
    db_context = DbContext()
    db_context.initialize_database()
    print("Database initialized successfully.")
    main_menu = MainMenu()
    main_menu.run()

