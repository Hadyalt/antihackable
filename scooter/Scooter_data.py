from datetime import datetime
import sqlite3
import os
from DbContext.crypto_utils import decrypt, encrypt
from DbContext.encrypted_logger import EncryptedLogger


class Scooter_data:
    def __init__(self, db_name="data.db"):
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.db_name = os.path.join(base_dir, db_name)
        self.connection = None

    def connect(self):
        try:
            self.connection = sqlite3.connect(self.db_name)
        except sqlite3.OperationalError as e:
            print(f"SQLite operational error: {e}")
        except sqlite3.DatabaseError as e:
            print(f"SQLite database error: {e}")
        except FileNotFoundError as e:
            print(f"Database file not found: {e}")
        except Exception as e:
            print(f"Unexpected error while connecting to the database: {e}")

    def insert_scooter(self, scooter):
        logger = EncryptedLogger()
        if self.connection:
            cursor = self.connection.cursor()
            InServiceDate = encrypt(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            try:
                cursor.execute(
                    """
                    INSERT INTO Scooter (
                        Brand, Model, SerialNumber, TopSpeed, BatteryCapacity,
                        StateOfCharge, TargetRangeSocMin, TargetRangeSocMax,
                        LocationLat, LocationLong, OutOfService,
                        Mileage, LastMaintenanceDate, InServiceDate
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
                        scooter.out_of_service,
                        scooter.mileage,
                        scooter.last_maintenance_date,
                        InServiceDate, 
                    ),
                )
                self.connection.commit()
                print("Scooter added successfully.")
            except sqlite3.IntegrityError as e:
                # Typically happens on UNIQUE constraint violations (e.g., duplicate email)
                print(f"Integrity Error: There was a data integrity issue. Contact Administrator.")
                logger.log_entry("System", "Integrity Error on Scooter Insertion", f"{e}", "Yes")
                self.connection.rollback()

            except sqlite3.OperationalError as e:
                # Happens if table doesn't exist, DB is locked, or SQL syntax is wrong
                print(f"Operational Error: database or SQL issue. Contact Administrator.")
                logger.log_entry("System", "Operational Error on Scooter Insertion", f"{e}", "Yes")
                self.connection.rollback()

            except sqlite3.InterfaceError as e:
                # Raised if wrong data types or bindings are passed to SQL placeholders
                print(f"Interface Error: invalid parameter binding. Contact Administrator.")
                logger.log_entry("System", "Interface Error on Scooter Insertion", f"{e}", "Yes")
                self.connection.rollback()

            except sqlite3.DatabaseError as e:
                # Base class for all database-related errors (corrupted DB, etc.)
                print(f"Database Error: possible corruption or I/O issue. Contact Administrator.")
                logger.log_entry("System", "Database Error on Scooter Insertion", f"{e}", "Yes")
                self.connection.rollback()

            except ValueError as e:
                # Custom validation issues (e.g. from earlier preprocessing)
                print(f"Validation Error: {e}")
                logger.log_entry("System", "Validation Error on Scooter Insertion", f"{e}", "Yes")
                self.connection.rollback()

            except TypeError as e:
                # When unexpected types are passed (e.g., None where a string is expected)
                print(f"Type Error: invalid argument type. [DEBUG] {e}")
                logger.log_entry("System", "Type Error on Scooter Insertion", f"{e}", "Yes")
                self.connection.rollback()

            except Exception as e:
                # Catch-all for anything unexpected
                print(f"Unexpected Exception occurred.")
                logger.log_entry("System", "Unexpected Error on Scooter Insertion", f"{e}", "Yes")
                self.connection.rollback()  
        else:
            print("No database connection. Call connect() first.")

    def get_all_scooters(self):
        logger = EncryptedLogger()
        try:
            if self.connection:
                cursor = self.connection.cursor()
                cursor.execute("SELECT * FROM Scooter")
                return cursor.fetchall()
            else:
                print("No connection.")
                return []
        except sqlite3.OperationalError as e:
            # Happens if table doesn't exist, DB is locked, or SQL syntax is wrong
            print(f"Operational Error: database or SQL issue. Contact Administrator.")
            logger.log_entry("System", "Operational Error on viewing all scooters", f"{e}", "Yes")
            return []
        except sqlite3.DatabaseError as e:
            # Base class for all database-related errors (corrupted DB, etc.)
            print(f"Database Error: possible corruption or I/O issue. Contact Administrator.")
            logger.log_entry("System", "Database Error on viewing all scooters", f"{e}", "Yes")
            return []
        except sqlite3.InterfaceError as e:
            # Raised if wrong data types or bindings are passed to SQL placeholders
            print(f"Interface Error: invalid parameter binding. Contact Administrator.")
            logger.log_entry("System", "Interface Error on viewing all scooters", f"{e}", "Yes")
            return []
        except Exception as e:
            # Catch-all for anything unexpected
            print(f"Unexpected Exception occurred.")
            logger.log_entry("System", "Unexpected Error on viewing all scooters", f"{e}", "Yes")
            return []
    
    def get_all_serial_numbers(self):
        logger = EncryptedLogger()
        try:
            if self.connection:
                cursor = self.connection.cursor()
                cursor.execute("SELECT SerialNumber FROM Scooter")
                return cursor.fetchall()
            else:
                print("No connection.")
                return []
        except sqlite3.OperationalError as e:
            # Happens if table doesn't exist, DB is locked, or SQL syntax is wrong
            print(f"Operational Error: database or SQL issue. Contact Administrator.")
            logger.log_entry("System", "Operational Error on viewing all serial numbers", f"{e}", "Yes")
            return []
        except sqlite3.DatabaseError as e:
            # Base class for all database-related errors (corrupted DB, etc.)
            print(f"Database Error: possible corruption or I/O issue. Contact Administrator.")
            logger.log_entry("System", "Database Error on viewing all serial numbers", f"{e}", "Yes")
            return []
        except sqlite3.InterfaceError as e:
            # Raised if wrong data types or bindings are passed to SQL placeholders
            print(f"Interface Error: invalid parameter binding. Contact Administrator.")
            logger.log_entry("System", "Interface Error on viewing all serial numbers", f"{e}", "Yes")
            return []
        except Exception as e:
            # Catch-all for anything unexpected
            print(f"Unexpected Exception occurred.")
            logger.log_entry("System", "Unexpected Error on viewing all serial numbers", f"{e}", "Yes")
            return []

    def get_scooter_by_serial(self, serial_number):
        all_scooters = self.get_all_scooters()
        for s in all_scooters:
            if decrypt(s[0]) == serial_number:
                return s

    def update_scooter_fields(self, serial_number, **fields):
        if not self.connection:
            print("No connection.")
            return False

        if not fields:
            print("No fields provided to update.")
            return False

        # Valid column check
        allowed_columns = {
            "Brand",
            "Model",
            "SerialNumber",
            "TopSpeed",
            "BatteryCapacity",
            "StateOfCharge",
            "TargetRangeSocMin",
            "TargetRangeSocMax",
            "LocationLat",
            "LocationLong",
            "OutOfService",
            "Mileage",
            "LastMaintenanceDate",
        }

        invalid_fields = [f for f in fields if f not in allowed_columns]
        if invalid_fields:
            print(f"Invalid fields: {', '.join(invalid_fields)}")
            return False

        # Locate the row using the stored encrypted serial number so we can keep
        # working with decrypted identifiers in the UI.
        current_record = self.get_scooter_by_serial(serial_number)
        if not current_record:
            print("Error: Scooter not found")
            return False
        stored_serial = current_record[0]

        encrypted_fields = {}
        for column, value in fields.items():
            if value is None:
                encrypted_fields[column] = None
                continue

            if column == "OutOfService":
                try:
                    normalized = int(value)
                except (TypeError, ValueError):
                    print("Invalid value for OutOfService: expected 0 or 1")
                    return False
                encrypted_fields[column] = encrypt(str(normalized))
            else:
                encrypted_fields[column] = encrypt(str(value))

        if not encrypted_fields:
            print("No valid fields to update.")
            return False

        set_clause = ", ".join([f"{key} = ?" for key in encrypted_fields])
        values = list(encrypted_fields.values())
        values.append(stored_serial)

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
        except sqlite3.OperationalError as e:
            print(f"Operational Error: database or SQL issue. Contact Administrator.")
            logger = EncryptedLogger()
            logger.log_entry("System", "Operational Error on updating scooter", f"{e}", "Yes")
            return False
        except sqlite3.InterfaceError as e:
            print(f"Interface Error: invalid parameter binding. Contact Administrator.")
            logger = EncryptedLogger()
            logger.log_entry("System", "Interface Error on updating scooter", f"{e}", "Yes")
            return False
        except sqlite3.IntegrityError as e:
            print(f"Integrity Error: There was a data integrity issue. Contact Administrator.")
            logger = EncryptedLogger()
            logger.log_entry("System", "Integrity Error on updating scooter", f"{e}", "Yes")
            return False
        except sqlite3.DatabaseError as e:
            print(f"Database Error: possible corruption or I/O issue. Contact Administrator.")
            logger = EncryptedLogger()
            logger.log_entry("System", "Database Error on updating scooter", f"{e}", "Yes")
            return False
        except TypeError as e:
            print(f"Type Error: invalid argument type.")
            logger = EncryptedLogger()
            logger.log_entry("System", "Type Error on updating scooter", f"{e}", "Yes")
            return False
        except Exception as e:
            print(f"Unexpected Exception occurred.")
            logger = EncryptedLogger()
            logger.log_entry("System", "Unexpected Error on updating scooter", f"{e}", "Yes")
            return False

    def delete_scooter(self, serial_number, deletor):
        logger = EncryptedLogger()
        try:
            if not self.connection:
                print("No connection.")
                return False
            current_record = self.get_scooter_by_serial(serial_number)
            if not current_record:
                print("Error: Scooter not found")
                return False
        
            cursor = self.connection.cursor()
            cursor.execute(
                "DELETE FROM Scooter WHERE SerialNumber = ?", (current_record[0],)
            )
            if cursor.rowcount == 0:
                print("Error: Scooter not found")
                return False
            self.connection.commit()
            print("Scooter deleted.")
            logger.log_entry(f"{deletor}", f"Deleted scooter {serial_number}", " ", "No")
        except sqlite3.OperationalError as e:
            print(f"Operational Error: database or SQL issue. Contact Administrator.")
            logger = EncryptedLogger()
            logger.log_entry("System", "Operational Error on deleting own account", f"{e}", "Yes")
            return False
        except sqlite3.DatabaseError as e:
            print(f"Database Error: possible corruption or I/O issue. Contact Administrator.")
            logger = EncryptedLogger()
            logger.log_entry("System", "Database Error on deleting own account", f"{e}", "Yes")
            return False
        except sqlite3.IntegrityError as e:
            print(f"Integrity Error: There was a data integrity issue. Contact Administrator.")
            logger = EncryptedLogger()
            logger.log_entry("System", "Integrity Error on deleting own account", f"{e}", "Yes")
            return False
        except TypeError as e:
            print(f"Type Error: invalid argument type.")
            logger = EncryptedLogger()
            logger.log_entry("System", "Type Error on deleting own account", f"{e}", "Yes")
            return False
        except ValueError as e:
            print(f"Value Error: {e}")
            logger = EncryptedLogger()
            logger.log_entry("System", "Value Error on deleting own account", f"{e}", "Yes")
            return False
        except Exception as e:
            print(f"Unexpected Exception occurred.")
            logger = EncryptedLogger()
            logger.log_entry("System", "Unexpected Error on deleting own account", f"{e}", "Yes")
            return False


    def search_scooters(self, search_term=""):
        logger = EncryptedLogger()
        try:
            if not self.connection:
                print("No connection.")
                return []
                # fetch all the scooters
            cursor = self.connection.cursor()
            cursor.execute("SELECT * FROM Scooter")
            all_scooters = cursor.fetchall()
            results = []
            search_lower = str(search_term).lower()
            for s in all_scooters:
                decrypted_fields = [
                decrypt(s[0]),  # serialNumber
                decrypt(s[1]),  # Brand
                decrypt(s[2]),  # Model
                decrypt(s[5]),  # stateOfCharge
                decrypt(s[8]),  # LocationLat
                decrypt(s[9]),  # LocationLong
                decrypt(s[10])  # outOfService
                ]
                if any(
                    search_lower in str(field).lower() for field in decrypted_fields
                ):
                    results.append(s)
            return results
        except sqlite3.OperationalError as e:
            # Happens if table doesn't exist, DB is locked, or SQL syntax is wrong
            print(f"Operational Error: database or SQL issue. Contact Administrator.")
            logger.log_entry("System", "Operational Error on viewing all scooters", f"{e}", "Yes")
            return []
        except sqlite3.DatabaseError as e:
            # Base class for all database-related errors (corrupted DB, etc.)
            print(f"Database Error: possible corruption or I/O issue. Contact Administrator.")
            logger.log_entry("System", "Database Error on viewing all scooters", f"{e}", "Yes")
            return []
        except sqlite3.InterfaceError as e:
            # Raised if wrong data types or bindings are passed to SQL placeholders
            print(f"Interface Error: invalid parameter binding. Contact Administrator.")
            logger.log_entry("System", "Interface Error on viewing all scooters", f"{e}", "Yes")
            return []
        except Exception as e:
            # Catch-all for anything unexpected
            print(f"Unexpected Exception occurred.")
            logger.log_entry("System", "Unexpected Error on viewing all scooters", f"{e}", "Yes")
            return []


    def close(self):
        if self.connection:
            self.connection.close()
            #print("Database connection closed.")
            return
        else:
            #print("No connection to close.")
            return
