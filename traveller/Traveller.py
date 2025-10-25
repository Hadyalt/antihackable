from datetime import datetime
import sqlite3
import os
import uuid

from DbContext.crypto_utils import decrypt, encrypt
from DbContext.encrypted_logger import EncryptedLogger


class Traveller:
    def __init__(self, db_name="data.db"):
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.db_name = os.path.join(base_dir, db_name)
        self.connection = None
        self.cities = [
            "Amsterdam",
            "Rotterdam",
            "The Hague",
            "Utrecht",
            "Eindhoven",
            "Tilburg",
            "Groningen",
            "Almere",
            "Breda",
            "Nijmegen",
        ]

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

    def _generate_traveller_id(self):
        """Generate a random traveller ID and ensure it does not collide."""
        try:
            cursor = self.connection.cursor()
            while True:
                candidate = uuid.uuid4().hex[:12].upper()
                cursor.execute(
                    "SELECT 1 FROM Traveller WHERE TravellerID = ?",
                    (candidate,),
                )
                if cursor.fetchone() is None:
                    return encrypt(candidate)
        except sqlite3.OperationalError as e:
            print(f"Operational Error: database or SQL issue. Contact Administrator.")
            logger = EncryptedLogger()
            logger.log_entry("System", "Operational Error on generating traveller ID", f"{e}", "Yes")
            return None
        except sqlite3.ProgrammingError as e:
            print(f"Programming Error: database programming issue. Contact Administrator.")
            logger = EncryptedLogger()
            logger.log_entry("System", "Programming Error on generating traveller ID", f"{e}", "Yes")
            return None
        except sqlite3.DatabaseError as e:
            print(f"Database Error: possible corruption or I/O issue. Contact Administrator.")
            logger = EncryptedLogger()
            logger.log_entry("System", "Database Error on generating traveller ID", f"{e}", "Yes")
            return None
        except ValueError as e:
            print(f"Validation Error: {e}")
            logger = EncryptedLogger()
            logger.log_entry("System", "Validation Error on generating traveller ID", f"{e}", "Yes")
            return None
        except Exception as e:
            print(f"Unexpected Exception occurred.")
            logger = EncryptedLogger()
            logger.log_entry("System", "Unexpected Error on generating traveller ID", f"{e}", "Yes")
            return None


    def insert_traveller(
        self,
        first_name,
        last_name,
        birthday,
        gender,
        street_name,
        house_number,
        zip_code,
        city,
        email,
        phone,
        driving_license,
    ):
        logger = EncryptedLogger()
        cursor = None
        try:
            if self.connection:
                # Only format phone (not validate other fields, as they are already validated and encrypted)
                cursor = self.connection.cursor()
                traveller_id = self._generate_traveller_id()
                registered_date = encrypt(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                cursor.execute(
                    """
                    INSERT INTO Traveller (
                        TravellerID, FirstName, LastName, Birthday, Gender, StreetName,
                    HouseNumber, ZipCode, City, Email, Phone,
                    DrivingLicenseNumber, RegisteredDate
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    traveller_id,
                    first_name,
                    last_name,
                    birthday,
                    gender,
                    street_name,
                    house_number,
                    zip_code,
                    city,
                    email,
                    phone,
                    driving_license,
                    registered_date
                ),
            )
            self.connection.commit()
            print("Traveller added successfully.")
            return traveller_id
         # --- Specific exceptions ---
        except sqlite3.IntegrityError as e:
            # Typically happens on UNIQUE constraint violations (e.g., duplicate email)
            print(f"Integrity Error: There was a data integrity issue. Contact Administrator.")
            logger.log_entry("System", "Integrity Error on Traveller Insertion", f"{e}", "Yes")
            self.connection.rollback()
            return False

        except sqlite3.OperationalError as e:
            # Happens if table doesn't exist, DB is locked, or SQL syntax is wrong
            print(f"Operational Error: database or SQL issue. Contact Administrator.")
            logger.log_entry("System", "Operational Error on Traveller Insertion", f"{e}", "Yes")
            self.connection.rollback()
            return False

        except sqlite3.InterfaceError as e:
            # Raised if wrong data types or bindings are passed to SQL placeholders
            print(f"Interface Error: invalid parameter binding. Contact Administrator.")
            logger.log_entry("System", "Interface Error on Traveller Insertion", f"{e}", "Yes")
            self.connection.rollback()
            return False

        except sqlite3.DatabaseError as e:
            # Base class for all database-related errors (corrupted DB, etc.)
            print(f"Database Error: possible corruption or I/O issue. Contact Administrator.")
            logger.log_entry("System", "Database Error on Traveller Insertion", f"{e}", "Yes")
            self.connection.rollback()
            return False

        except ValueError as e:
            # Custom validation issues (e.g. from earlier preprocessing)
            print(f"Validation Error: {e}")
            logger.log_entry("System", "Validation Error on Traveller Insertion", f"{e}", "Yes")
            self.connection.rollback()
            return False

        except TypeError as e:
            # When unexpected types are passed (e.g., None where a string is expected)
            print(f"Type Error: invalid argument type. [DEBUG] {e}")
            logger.log_entry("System", "Type Error on Traveller Insertion", f"{e}", "Yes")
            self.connection.rollback()
            return False

        except Exception as e:
            # Catch-all for anything unexpected
            print(f"Unexpected Exception occurred.")
            logger.log_entry("System", "Unexpected Error on Traveller Insertion", f"{e}", "Yes")
            self.connection.rollback()
            return False
    
        

    def get_all_travellers(self):
        logger = EncryptedLogger()
        cursor = None
        if self.connection:
            try:
                if self.connection:
                    cursor = self.connection.cursor()
                    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
                    tables = cursor.fetchall()
                    cursor.execute("SELECT * FROM Traveller")
                    return cursor.fetchall()
                
            except sqlite3.OperationalError as e:
                # Happens if table doesn't exist, DB is locked, or SQL syntax is wrong
                print(f"Operational Error: database or SQL issue. Contact Administrator.")
                logger.log_entry("System", "Operational Error on getting all travellers", f"{e}", "Yes")
                return None
            except sqlite3.DatabaseError as e:
                # Base class for all database-related errors (corrupted DB, etc.)
                print(f"Database Error: possible corruption or I/O issue. Contact Administrator.")
                logger.log_entry("System", "Database Error on getting all travellers", f"{e}", "Yes")
                return None
            except sqlite3.InterfaceError as e:
                # Raised if wrong data types or bindings are passed to SQL placeholders
                print(f"Interface Error: invalid parameter binding. Contact Administrator.")
                logger.log_entry("System", "Interface Error on getting all travellers", f"{e}", "Yes")
                return None
            except Exception as e:
                # Catch-all for anything unexpected
                print(f"Unexpected Exception occurred.")
                logger.log_entry("System", "Unexpected Error on getting all travellers", f"{e}", "Yes")
                return None

    def search_travellers(self, search_term=""):
        try:
            if not self.connection:
                print("No connection.")
                return []

            # Fetch all travellers
            cursor = self.connection.cursor()
            cursor.execute("SELECT * FROM Traveller")
            all_travellers = cursor.fetchall()
            results = []
            search_term_lower = search_term.lower()
            for t in all_travellers:
                # Decrypt all relevant fields
                decrypted_fields = [
                    decrypt(t[1]),  # FirstName
                    decrypt(t[2]),  # LastName
                    decrypt(t[9]),  # Email
                    decrypt(t[8]),  # City
                    decrypt(t[10]),  # Phone
                    decrypt(t[11])  # DrivingLicenseNumber
                ]
                # If search term is in any field, add to results
                if any(
                    search_term_lower in (str(field).lower()) for field in decrypted_fields
                ):
                    results.append(t)
            return results
        
        ## --- Specific exceptions ---
        except sqlite3.OperationalError as e:
            print(f"Operational Error: database or SQL issue. Contact Administrator.")
            logger = EncryptedLogger()
            logger.log_entry("System", "Operational Error on searching travellers", f"{e}", "Yes")
            return []
        except sqlite3.ProgrammingError as e:
            print(f"Programming Error: database programming issue. Contact Administrator.")
            logger = EncryptedLogger()
            logger.log_entry("System", "Programming Error on searching travellers", f"{e}", "Yes")
            return []
        except sqlite3.DatabaseError as e:
            print(f"Database Error: possible corruption or I/O issue. Contact Administrator.")
            logger = EncryptedLogger()
            logger.log_entry("System", "Database Error on searching travellers", f"{e}", "Yes")
            return []
        except TypeError as e:
            print(f"Type Error: invalid argument type.")
            logger = EncryptedLogger()
            logger.log_entry("System", "Type Error on searching travellers", f"{e}", "Yes")
            return []
        except ValueError as e:
            print(f"Value Error: {e}")
            logger = EncryptedLogger()
            logger.log_entry("System", "Value Error on searching travellers", f"{e}", "Yes")
            return []
        except Exception as e:
            print(f"Unexpected Exception occurred.")
            logger = EncryptedLogger()
            logger.log_entry("System", "Unexpected Error on searching travellers", f"{e}", "Yes")
            return []
        

    def get_traveller_by_id(self, traveller_id):
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT * FROM Traveller WHERE TravellerID = ?", (traveller_id,))
            return cursor.fetchone()
        
        ## --- Specific exceptions ---
        except sqlite3.OperationalError as e:
            print(f"Operational Error: database or SQL issue. Contact Administrator.")
            logger = EncryptedLogger()
            logger.log_entry("System", "Operational Error on getting traveller by ID", f"{e}", "Yes")
            return None
        except sqlite3.ProgrammingError as e:
            print(f"Programming Error: database programming issue. Contact Administrator.")
            logger = EncryptedLogger()
            logger.log_entry("System", "Programming Error on getting traveller by ID", f"{e}", "Yes")
            return None
        except sqlite3.DatabaseError as e:
            print(f"Database Error: possible corruption or I/O issue. Contact Administrator.")
            logger = EncryptedLogger()
            logger.log_entry("System", "Database Error on getting traveller by ID", f"{e}", "Yes")
            return None
        except Exception as e:
            print(f"Unexpected Exception occurred.")
            logger = EncryptedLogger()
            logger.log_entry("System", "Unexpected Error on getting traveller by ID", f"{e}", "Yes")
            return None
        

    def update_traveller(self, traveller_id, **fields):
        allowed = {
            "FirstName",
            "LastName",
            "Birthday",
            "Gender",
            "StreetName",
            "HouseNumber",
            "ZipCode",
            "City",
            "Email",
            "Phone",
            "DrivingLicenseNumber",
            "RegisteredDate",
        }

        try:
            updates = []
            values = []
            for k, v in fields.items():
                if k in allowed:
                    updates.append(f"{k} = ?")
                    values.append(v)

            if not updates:
                print("No valid fields to update.")
                return
        

            values.append(traveller_id)
            cursor = self.connection.cursor()
            cursor.execute(
                f"UPDATE Traveller SET {', '.join(updates)} WHERE TravellerID = ?", values
            )
            self.connection.commit()
            print("Traveller updated.")

        ## --- Specific exceptions ---
        except sqlite3.OperationalError as e:
            print(f"Operational Error: database or SQL issue. Contact Administrator.")
            logger = EncryptedLogger()
            logger.log_entry("System", "Operational Error on updating traveller", f"{e}", "Yes")
            return
        except sqlite3.InterfaceError as e:
            print(f"Interface Error: invalid parameter binding. Contact Administrator.")
            logger = EncryptedLogger()
            logger.log_entry("System", "Interface Error on updating traveller", f"{e}", "Yes")
            return
        except sqlite3.IntegrityError as e:
            print(f"Integrity Error: There was a data integrity issue. Contact Administrator.")
            logger = EncryptedLogger()
            logger.log_entry("System", "Integrity Error on updating traveller", f"{e}", "Yes")
            return
        except sqlite3.DatabaseError as e:
            print(f"Database Error: possible corruption or I/O issue. Contact Administrator.")
            logger = EncryptedLogger()
            logger.log_entry("System", "Database Error on updating traveller", f"{e}", "Yes")
            return
        except TypeError as e:
            print(f"Type Error: invalid argument type.")
            logger = EncryptedLogger()
            logger.log_entry("System", "Type Error on updating traveller", f"{e}", "Yes")
            return
        except Exception as e:
            print(f"Unexpected Exception occurred.")
            logger = EncryptedLogger()
            logger.log_entry("System", "Unexpected Error on updating traveller", f"{e}", "Yes")
            return
        

    def delete_traveller(self, deletor, traveller_id):
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT 1 FROM Traveller WHERE TravellerID = ?", (traveller_id,))
            if cursor.fetchone() is None:
                print("Traveller not found. Deletion aborted.")
                logger = EncryptedLogger()
                logger.log_entry(f"{deletor}", f"Attempted to delete non-existent Traveller ID: {decrypt(traveller_id)}","No action taken","No")
                return 
            cursor.execute("DELETE FROM Traveller WHERE TravellerID = ?", (traveller_id,))
            self.connection.commit()
            print("Traveller deleted.")
            logger = EncryptedLogger()
            logger.log_entry(f"{deletor}", f"Deleted Traveller with Traveller ID: {decrypt(traveller_id)}", " ", "No")
        
        ## --- Specific exceptions ---
        except sqlite3.OperationalError as e:
            print(f"Operational Error: database or SQL issue. Contact Administrator.")
            logger = EncryptedLogger()
            logger.log_entry("System", "Operational Error on deleting traveller", f"{e}", "Yes")
            return
        except sqlite3.DatabaseError as e:
            print(f"Database Error: possible corruption or I/O issue. Contact Administrator.")
            logger = EncryptedLogger()
            logger.log_entry("System", "Database Error on deleting traveller", f"{e}", "Yes")
            return
        except sqlite3.IntegrityError as e:
            print(f"Integrity Error: There was a data integrity issue. Contact Administrator.")
            logger = EncryptedLogger()
            logger.log_entry("System", "Integrity Error on deleting traveller", f"{e}", "Yes")
            return
        except TypeError as e:
            print(f"Type Error: invalid argument type.")
            logger = EncryptedLogger()
            logger.log_entry("System", "Type Error on deleting traveller", f"{e}", "Yes")
            return
        except ValueError as e:
            print(f"Value Error: {e}")
            logger = EncryptedLogger()
            logger.log_entry("System", "Value Error on deleting traveller", f"{e}", "Yes")
            return
        except Exception as e:
            print(f"Unexpected Exception occurred.")
            logger = EncryptedLogger()
            logger.log_entry("System", "Unexpected Error on deleting traveller", f"{e}", "Yes")
            return

    def close(self):
        if self.connection:
            self.connection.close()
