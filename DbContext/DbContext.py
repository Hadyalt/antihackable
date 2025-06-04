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
        """Initialize the database by creating all required tables and the master account."""
        self.connect()

        # Define the schema for the User table with a role and is_active flag
        user_schema = """
            Username TEXT PRIMARY KEY,
            Password TEXT NOT NULL,
            Role TEXT NOT NULL DEFAULT 'user',
            IsActive INTEGER NOT NULL DEFAULT 1
        """

        traveller_schema = """
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
        # You can add more tables here as needed
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

    def get_User(self, username):
        self.connection = sqlite3.connect(self.db_name)
        """Retrieve a User record by username."""
        if self.connection:
            cursor = self.connection.cursor()
            cursor.execute("SELECT * FROM User WHERE Username = ?", (username,))
            user = cursor.fetchone()
            if user:
                print(f"Retrieved User: {user}")
                return user
            else:
                print(f"No User found with username: {username}")
                return None
        else:
            print("No database connection. Call connect() first.")
            return None
        


    def insert_scooter(self, scooter):
        if self.connection:
            cursor = self.connection.cursor()
            cursor.execute("""
                INSERT INTO Scooter (
                    Brand, Model, SerialNumber, TopSpeed, BatteryCapacity,
                    StateOfCharge, TargetRangeSocMin, TargetRangeSocMax,
                    LocationLat, LocationLong, OutOfService,
                    Mileage, LastMaintenanceDate
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                scooter.brand,
                scooter.model,
                scooter.serial_number,
                scooter.top_speed,
                scooter.battery_capacity,
                scooter.state_of_charge,
                scooter.target_range_soc[0],
                scooter.target_range_soc[1],
                scooter.location[0],
                scooter.location[1],
                int(scooter.out_of_service),
                scooter.mileage,
                scooter.last_maintenance_date
            ))
            self.connection.commit()
            print("Scooter added successfully.")
        else:
            print("No database connection. Call connect() first.")

    def get_all_scooters(self):
        if self.connection:
            cursor = self.connection.cursor()
            cursor.execute("SELECT * FROM Scooter")
            return cursor.fetchall()
        else:
            print("No connection.")
            return []

    def update_scooter_state(self, serial_number, new_soc):
        if self.connection:
            cursor = self.connection.cursor()
            cursor.execute(
                "UPDATE Scooter SET StateOfCharge = ? WHERE SerialNumber = ?",
                (new_soc, serial_number)
            )
            self.connection.commit()
            print("Scooter updated.")
        else:
            print("No connection.")

    def delete_scooter(self, serial_number):
        if self.connection:
            cursor = self.connection.cursor()
            cursor.execute("DELETE FROM Scooter WHERE SerialNumber = ?", (serial_number,))
            self.connection.commit()
            print("Scooter deleted.")
        else:
            print("No connection.")




    def insert_scooter(self, scooter):
        if self.connection:
            cursor = self.connection.cursor()
            cursor.execute("""
                INSERT INTO Scooter (
                    Brand, Model, SerialNumber, TopSpeed, BatteryCapacity,
                    StateOfCharge, TargetRangeSocMin, TargetRangeSocMax,
                    LocationLat, LocationLong, OutOfService,
                    Mileage, LastMaintenanceDate
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                scooter.brand,
                scooter.model,
                scooter.serial_number,
                scooter.top_speed,
                scooter.battery_capacity,
                scooter.state_of_charge,
                scooter.target_range_soc[0],
                scooter.target_range_soc[1],
                scooter.location[0],
                scooter.location[1],
                int(scooter.out_of_service),
                scooter.mileage,
                scooter.last_maintenance_date
            ))
            self.connection.commit()
            print("Scooter added successfully.")
        else:
            print("No database connection. Call connect() first.")

    def get_all_scooters(self):
        if self.connection:
            cursor = self.connection.cursor()
            cursor.execute("SELECT * FROM Scooter")
            return cursor.fetchall()
        else:
            print("No connection.")
            return []

    def update_scooter_state(self, serial_number, new_soc):
        if self.connection:
            cursor = self.connection.cursor()
            cursor.execute(
                "UPDATE Scooter SET StateOfCharge = ? WHERE SerialNumber = ?",
                (new_soc, serial_number)
            )
            self.connection.commit()
            print("Scooter updated.")
        else:
            print("No connection.")

    def delete_scooter(self, serial_number):
        if self.connection:
            cursor = self.connection.cursor()
            cursor.execute("DELETE FROM Scooter WHERE SerialNumber = ?", (serial_number,))
            self.connection.commit()
            print("Scooter deleted.")
        else:
            print("No connection.")

    def close(self):
        """Close the database connection."""
        if self.connection:
            self.connection.close()
            print(f"Connection to {self.db_name} closed.")
