import sqlite3
import os


class Scooter_data:
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

    def insert_scooter(self, scooter):
        if self.connection:
            cursor = self.connection.cursor()
            cursor.execute(
                """
                INSERT INTO Scooter (
                    Brand, Model, SerialNumber, TopSpeed, BatteryCapacity,
                    StateOfCharge, TargetRangeSocMin, TargetRangeSocMax,
                    LocationLat, LocationLong, OutOfService,
                    Mileage, LastMaintenanceDate
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
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
                    scooter.last_maintenance_date,
                ),
            )
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

    def update_scooter_fields(self, serial_number, **fields):
        if not self.connection:
            print("No connection.")
            return False

        set_clause = ", ".join([f"{key} = ?" for key in fields])
        values = list(fields.values())
        values.append(serial_number)

        try:
            cursor = self.connection.cursor()
            cursor.execute(
                f"UPDATE Scooter SET {set_clause} WHERE SerialNumber = ?", values
            )
            if cursor.rowcount == 0:
                print("Error: Scooter not found")
                return False
            self.connection.commit()
            print("Update successful!")
            return True
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return False

    def delete_scooter(self, serial_number):
        if self.connection:
            cursor = self.connection.cursor()
            cursor.execute(
                "DELETE FROM Scooter WHERE SerialNumber = ?", (serial_number,)
            )
            self.connection.commit()
            print("Scooter deleted.")
        else:
            print("No connection.")

    def close(self):
        if self.connection:
            self.connection.close()
            print("Database connection closed.")
        else:
            print("No connection to close.")
