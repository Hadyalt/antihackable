import sqlite3
import os

class DbContext:
    def __init__(self, db_name="data.db"):
        # Get the parent directory of the current file's directory
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        # Construct the correct db path
        self.db_name = os.path.join(base_dir, db_name)
        # print("Database path:", self.db_name)
        self.connection = None

    def connect(self):
        """Establish a connection to the SQLite database."""
        self.connection = sqlite3.connect(self.db_name)
        return self.connection

    def create_table(self, table_name, schema):
        if self.connection:
            cursor = self.connection.cursor()
            cursor.execute(f"CREATE TABLE IF NOT EXISTS {table_name} ({schema})")
            self.connection.commit()
        else:
            print("No database connection. Call connect() first.")

    def initialize_database(self):
        """Initialize the database by creating all required tables and the master account."""
        self.connect()

        # Define the schema for the User table with a role and is_active flag
        user_schema = """
            Username TEXT PRIMARY KEY,
            Password TEXT NOT NULL,
            Role TEXT NOT NULL DEFAULT 'user',
            IsActive INTEGER NOT NULL DEFAULT 1
        """

        # Create the User table
        self.create_table("User", user_schema)
        # create the traveller table
        traveller_schema = """
            FirstName TEXT NOT NULL,
            LastName TEXT NOT NULL, 
            Birthday TEXT NOT NULL,
            Gender TEXT NOT NULL,
            StreetName TEXT NOT NULL,
            HouseNumber TEXT NOT NULL,
            ZipCode TEXT NOT NULL,
            City TEXT NOT NULL,
            EmailAddress TEXT NOT NULL,
            MobilePhone TEXT NOT NULL,
            DrivingLicenseNumber TEXT NOT NULL
        """
        self.create_table("Traveller", traveller_schema)

        # Create the AuditLog table
        audit_schema = """
            Id INTEGER PRIMARY KEY AUTOINCREMENT,
            Username TEXT NOT NULL,
            Action TEXT NOT NULL,
            Timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        """
        self.create_table("AuditLog", audit_schema)

        # Create the Scooter table
        scooter_schema = """
            Id INTEGER PRIMARY KEY AUTOINCREMENT,
            Brand TEXT NOT NULL,
            Model TEXT NOT NULL,
            SerialNumber TEXT NOT NULL UNIQUE,
            TopSpeed REAL NOT NULL,
            BatteryCapacity REAL NOT NULL,
            StateOfCharge REAL NOT NULL,
            TargetRangeSocMin REAL NOT NULL,
            TargetRangeSocMax REAL NOT NULL,
            LocationLat REAL NOT NULL,
            LocationLong REAL NOT NULL,
            OutOfService INTEGER NOT NULL DEFAULT 0,
            Mileage REAL NOT NULL,
            LastMaintenanceDate TEXT NOT NULL
        """
        self.create_table("Scooter", scooter_schema)

        # Insert master account if it doesn't exist
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM User WHERE Username = ?", ("super_admin",))
        if not cursor.fetchone():
            master_data = {
                "Username": "super_admin",
                "Password": "Admin_123?",
                "Role": "superadmin",
                "IsActive": 1
            }
            columns = ", ".join(master_data.keys())
            placeholders = ", ".join(["?"] * len(master_data))
            sql = f"INSERT INTO User ({columns}) VALUES ({placeholders})"
            cursor.execute(sql, list(master_data.values()))
            self.connection.commit()
            print("Super admin account created.")

        self.close()
    
    def log_action(self, username, action):
        """Log an action for auditing purposes."""
        if self.connection:
            cursor = self.connection.cursor()
            cursor.execute(
                "INSERT INTO AuditLog (Username, Action) VALUES (?, ?)",
                (username, action)
            )
            self.connection.commit()
        else:
            print("No database connection. Call connect() first.")

    def insert_User(self, user_data):
        self.connection = sqlite3.connect(self.db_name)
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
        self.connection.close()        

    def close(self):
        """Close the database connection."""
        if self.connection:
            self.connection.close()
