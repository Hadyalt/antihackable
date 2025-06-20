import sqlite3
import os

from DbContext.crypto_utils import decrypt
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
        self.connection = sqlite3.connect(self.db_name)    

    def validate_zip_code(self, zip_code):
        # Format: 4 digits + 2 uppercase letters
        return (
            len(zip_code) == 6
            and zip_code[:4].isdigit()
            and zip_code[4:].isalpha()
            and zip_code[4:].isupper()
        )

    def validate_driving_license(self, license):
        # XXDDDDDDD or XDDDDDDDD
        if len(license) == 9:
            if (
                license[:2].isalpha()
                and license[:2].isupper()
                and license[2:].isdigit()
            ):
                return True
            if license[0].isalpha() and license[0].isupper() and license[1:].isdigit():
                return True
        return False

    def format_phone(self, phone):
        # Remove non-digit characters
        digits = "".join(c for c in phone if c.isdigit())
        if len(digits) != 8:
            raise ValueError("Phone number must contain exactly 8 digits")
        return f"+31-6-{digits}"

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
        try:
            # Only format phone (not validate other fields, as they are already validated and encrypted)
            cursor = self.connection.cursor()
            cursor.execute(
                """
                INSERT INTO Traveller (
                    FirstName, LastName, Birthday, Gender, StreetName,
                    HouseNumber, ZipCode, City, Email, Phone,
                    DrivingLicenseNumber, RegisteredDate
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))
            """,
                (
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
                ),
            )
            self.connection.commit()
            print("Traveller added successfully.")
            return True
        except sqlite3.IntegrityError as e:
            print(f"Error: Email already exists. [DEBUG] {e}")
            return False
        except ValueError as e:
            print(f"Validation Error: {e}")
            return False
        except Exception as e:
            print(f"[DEBUG] Exception occurred: {e}")
            return False

    def get_all_travellers(self):
        cursor = self.connection.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        cursor.execute("SELECT * FROM Traveller")
        return cursor.fetchall()
    
    def search_travellers(self, search_term):
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
                decrypt(t[10]), # Phone
                decrypt(t[11])  # DrivingLicenseNumber
            ]
            # If search term is in any field, add to results
            if any(search_term_lower in (str(field).lower()) for field in decrypted_fields):
                results.append(t)
        return results

    def get_traveller_by_id(self, traveller_id):
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM Traveller WHERE TravellerID = ?", (traveller_id,))
        return cursor.fetchone()

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
        updates = []
        values = []
        for k, v in fields.items():
            if k in allowed:
                # Special validation for certain fields
                if k == "Phone":
                    v = self.format_phone(v)

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

    def delete_traveller(self, traveller_id, deletor):
        cursor = self.connection.cursor()
        cursor.execute("SELECT 1 FROM Traveller WHERE TravellerID = ?", (traveller_id,))
        if cursor.fetchone() is None:
            print("Traveller not found. Deletion aborted.")
            logger = EncryptedLogger()
            logger.log_entry(f"{deletor}", f"Attempted to delete non-existent Traveller ID: {traveller_id}","No action taken","No")
            return 
        cursor.execute("DELETE FROM Traveller WHERE TravellerID = ?", (traveller_id,))
        self.connection.commit()
        print("Traveller deleted.")
        logger = EncryptedLogger()
        logger.log_entry(f"{deletor}", f"Deleted Traveller with Traveller ID: {traveller_id}", " ", "No")

    def close(self):
        if self.connection:
            self.connection.close()
