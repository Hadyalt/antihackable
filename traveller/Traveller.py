import sqlite3
import os


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
        self.create_table_if_not_exists()

    def create_table_if_not_exists(self):
        cursor = self.connection.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Traveller (
                TravellerID INTEGER PRIMARY KEY AUTOINCREMENT,
                FirstName TEXT NOT NULL,
                LastName TEXT NOT NULL,
                Birthday TEXT NOT NULL,
                Gender TEXT NOT NULL,
                StreetName TEXT NOT NULL,
                HouseNumber TEXT NOT NULL,
                ZipCode TEXT NOT NULL,
                City TEXT NOT NULL,
                Email TEXT UNIQUE NOT NULL,
                Phone TEXT NOT NULL,
                DrivingLicenseNumber TEXT NOT NULL,
                RegisteredDate TEXT NOT NULL
            )
        """)
        self.connection.commit()

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
            # Validate inputs
            if not self.validate_zip_code(zip_code):
                raise ValueError("Invalid Zip Code format. Must be DDDDXX")

            if not self.validate_driving_license(driving_license):
                raise ValueError("Invalid Driving License format")

            formatted_phone = self.format_phone(phone)

            if city not in self.cities:
                raise ValueError("Invalid city selection")

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
                    formatted_phone,
                    driving_license,
                ),
            )
            self.connection.commit()
            print("Traveller added successfully.")
            return True
        except sqlite3.IntegrityError:
            print("Error: Email already exists.")
            return False
        except ValueError as e:
            print(f"Validation Error: {e}")
            return False
        except Exception as e:
            print(f"Error: {e}")
            return False

    def get_all_travellers(self):
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM Traveller")
        return cursor.fetchall()

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
                if k == "ZipCode" and not self.validate_zip_code(v):
                    print("Invalid Zip Code format. Must be DDDDXX")
                    return
                if k == "DrivingLicenseNumber" and not self.validate_driving_license(v):
                    print("Invalid Driving License format")
                    return
                if k == "City" and v not in self.cities:
                    print("Invalid city selection")
                    return
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

    def delete_traveller(self, traveller_id):
        cursor = self.connection.cursor()
        cursor.execute("DELETE FROM Traveller WHERE TravellerID = ?", (traveller_id,))
        self.connection.commit()
        print("Traveller deleted.")

    def close(self):
        if self.connection:
            self.connection.close()
