import sqlite3
import os


class DbContext:
    def __init__(self, db_name="data.db"):
        # Get the parent directory of the current file's directory
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        # Construct the correct db path
        self.db_name = os.path.join(base_dir, db_name)
        print("Database path:", self.db_name)
        self.connection = None

    def connect(self):
        """Establish a connection to the SQLite database."""
        self.connection = sqlite3.connect(self.db_name)
        print(f"Connected to {self.db_name}")

    def create_table(self, table_name, schema):
        if self.connection:
            cursor = self.connection.cursor()
            cursor.execute(f"CREATE TABLE IF NOT EXISTS {table_name} ({schema})")
            self.connection.commit()
            print(f"Table '{table_name}' created or already exists.")
        else:
            print("No database connection. Call connect() first.")

    def initialize_database(self):
        """Initialize the database by creating all required tables."""
        self.connect()

        # Define the schema for the User (Charge Detail Record) table
        user_schema = """
            Username TEXT PRIMARY KEY,
            Password TEXT NOT NULL
        """

        # Create the User table
        self.create_table("User", user_schema)
        self.close()

    def insert_User(self, user_data):
        """Insert a new User record into the database."""
        if self.connection:
            cursor = self.connection.cursor()
            columns = ", ".join(user_data.keys())
            placeholders = ", ".join(["?"] * len(user_data))
            sql = f"INSERT INTO User ({columns}) VALUES ({placeholders})"
            cursor.execute(sql, list(user_data.values()))
            self.connection.commit()
            print(f"Inserted new User record with ID: {user_data['Username']}")
        else:
            print("No database connection. Call connect() first.")

    def close(self):
        """Close the database connection."""
        if self.connection:
            self.connection.close()
            print(f"Connection to {self.db_name} closed.")
