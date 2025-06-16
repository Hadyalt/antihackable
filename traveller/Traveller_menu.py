import re
from datetime import datetime
from DbContext.crypto_utils import decrypt
from DbContext.encrypted_logger import EncryptedLogger
from traveller.Traveller import Traveller


def display_cities(cities):
    print("\nAvailable Cities:")
    for i, city in enumerate(cities, 1):
        print(f"[{i}] {city}")


def traveller_menu(username):
    while True:
        print("\nTraveller Menu")
        print("[1] Add Traveller")
        print("[2] View Travellers")
        print("[3] Update Traveller")
        print("[4] Delete Traveller")
        print("[5] Go Back")

        choice = input("Choose an option: ")
        if choice == "1":
            add_traveller(username)
        elif choice == "2":
            view_travellers()
        elif choice == "3":
            view_travellers()
            update_traveller(username)
        elif choice == "4":
            db = Traveller()
            db.connect()
            tid = input("Traveller ID to delete: ").strip()
            db.delete_traveller(tid, username)

        elif choice == "5":
            return
        else:
            print("Invalid choice.")

def add_traveller(creator):
    db = Traveller()
    db.connect()

    print("\nAdd New Traveller")
    # First name validation
    while True:
        first_name = input("First Name: ").strip()
        if first_name and first_name.isalpha():
            break
        else:
            print("First name must only contain letters and cannot be empty. Please try again.")

    # Last name validation
    while True:
        last_name = input("Last Name: ").strip()
        if last_name and last_name.isalpha():
            break
        else:
            print("Last name must only contain letters and cannot be empty. Please try again.")

    # Birthday validation
    while True:
        birthday = input("Birthday (YYYY-MM-DD): ").strip()
        try:
            datetime.strptime(birthday, "%Y-%m-%d")
            break
        except ValueError:
            print("Invalid date format. Please use YYYY-MM-DD.")

    print("\nGender:")
    print("[1] Male")
    print("[2] Female")
    while True:
        gender_choice = input("Select gender (1 or 2): ").strip()
        if gender_choice == "1":
            gender = "Male"
            break
        elif gender_choice == "2":
            gender = "Female"
            break
        else:
            print("Invalid input. Please select 1 for Male or 2 for Female.")

    # Street name validation
    while True:
        street_name = input("Street Name: ").strip()
        if street_name:
            break
        else:
            print("Street name cannot be empty. Please try again.")

    # House number validation
    while True:
        house_number = input("House Number: ").strip()
        if house_number.isdigit():
            break
        else:
            print("House number must be digits only. Please try again.")

    # Zip code validation loop
    while True:
        zip_code = input("Zip Code (DDDDXX format): ").strip().upper()
        if db.validate_zip_code(zip_code):
            break
        else:
            print("Invalid Zip Code format. Must be 4 digits followed by 2 uppercase letters (e.g., 1234AB). Please try again.")

    display_cities(db.cities)
    city = None
    while city is None:
        try:
            city_choice = input("Select city (1-10): ").strip()
            city_idx = int(city_choice) - 1
            city = db.cities[city_idx]
        except (ValueError, IndexError):
            print("Invalid city selection")
            display_cities(db.cities)

    # Email validation
    email_regex = r"^[\w\.-]+@[\w\.-]+\.\w+$"
    while True:
        email = input("Email: ").strip()
        if re.match(email_regex, email):
            break
        else:
            print("Invalid email format. Please try again.")

    # Phone validation loop
    while True:
        phone = input("Phone (8 digits only): ").strip()
        try:
            db.format_phone(phone)
            break
        except ValueError as e:
            print(f"{e} Please try again.")

    # Driving license validation loop
    while True:
        driving_license = (
            input("Driving License (XXDDDDDDD or XDDDDDDDD format): ")
            .strip()
            .upper()
        )
        if db.validate_driving_license(driving_license):
            break
        else:
            print("Invalid Driving License format. Please try again.")

    # Attempt to add traveller
    db.insert_traveller(
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
    )
    logger = EncryptedLogger()
    logger.log_entry(f"{creator}", "Created a new Traveller", f"Traveller: {first_name} is created" , "No")

def view_travellers():
    db = Traveller()
    db.connect()
    travellers = db.get_all_travellers()
    if travellers:
        print("\nTraveller List:")
        print("-" * 100)
        print(
            "ID  | First Name   | Last Name    | Email                | Phone         | City"
        )
        print("-" * 100)
        for t in travellers:
            print(
                f"{t[0]:<4}| {t[1]:<12}| {t[2]:<12}| {t[9]:<20}| {t[10]:<14}| {t[8]}"
            )
        print("-" * 100)
    else:
        print("No travellers found.")

def update_traveller(updater):
    db = Traveller()
    logger = EncryptedLogger()
    db.connect()
    tid = input("Traveller ID to update: ").strip()
    traveller = db.get_traveller_by_id(tid)
    if not traveller:
        print("Traveller not found.")
        return

    print("\nUpdate Traveller")
    print("[1] First Name")
    print("[2] Last Name")
    print("[3] Birthday")
    print("[4] Gender")
    print("[5] Street Name")
    print("[6] House Number")
    print("[7] Zip Code")
    print("[8] City")
    print("[9] Email")
    print("[10] Phone")
    print("[11] Driving License")
    field = input("Field to update: ").strip()

    new_val = None
    if field in ("1", "2", "3", "5", "6", "9"):
        new_val = input(f"New value: ").strip()

    elif field == "4":  # Gender
        print("[1] Male")
        print("[2] Female")
        gender_choice = input("Select gender: ").strip()
        new_val = "Male" if gender_choice == "1" else "Female"

    elif field == "7":  # Zip Code
        new_val = input("New Zip Code (DDDDXX format): ").strip().upper()

    elif field == "8":  # City
        display_cities(db.cities)
        new_val = None
        while new_val is None:
            try:
                city_choice = input("Select city (1-10): ").strip()
                city_idx = int(city_choice) - 1
                new_val = db.cities[city_idx]
            except (ValueError, IndexError):
                print("Invalid city selection")
                

    elif field == "10":  # Phone
        new_val = input("New Phone (8 digits only): ").strip()

    elif field == "11":  # Driving License
        new_val = (
            input("New Driving License (XXDDDDDDD or XDDDDDDDD format): ")
            .strip()
            .upper()
        )
    else:
        print("Invalid field.")
        return

    # Map menu choice to field name
    field_map = {
        "1": "FirstName",
        "2": "LastName",
        "3": "Birthday",
        "4": "Gender",
        "5": "StreetName",
        "6": "HouseNumber",
        "7": "ZipCode",
        "8": "City",
        "9": "Email",
        "10": "Phone",
        "11": "DrivingLicenseNumber",
    }

    # Perform update
    db.update_traveller(tid, **{field_map[field]: new_val})
    logger.log_entry(f"{updater}", "Updated a Traveller", f"Traveller {tid}: {field_map[field]} is updated to {new_val}" , "No")
