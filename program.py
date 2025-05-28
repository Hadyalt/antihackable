from DbContext.DbContext import DbContext


if __name__ == "__main__":
    db_context = DbContext()
    db_context.initialize_database()
    print("Database initialized successfully.")
