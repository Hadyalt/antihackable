import re
from datetime import datetime
from DbContext.crypto_utils import decrypt, encrypt
from DbContext.encrypted_logger import EncryptedLogger
from traveller.Traveller import Traveller
from valid_in_out_put import is_valid_email



def display_cities(cities):
    print("\nAvailable Cities:")
    for i, city in enumerate(cities, 1):
        print(f"[{i}] {city}")


def traveller_menu(username):
    while True:
        logger = EncryptedLogger()
        print("\nTraveller Menu")
        print("[1] Add Traveller")
        print("[2] View Travellers")
        print("[3] Update Traveller")
        print("[4] Delete Traveller")
        print("[5] Go Back")
        print("[6] Logout")
        print("[7] Exit")
        choice = input("Enter your choice: ")
        if choice == "1":
            add_traveller(username)
        elif choice == "2":
            view_travellers(username)
        elif choice == "3":
            view_travellers()
            update_traveller(username)
        elif choice == "4":
            db = Traveller()
            db.connect()
            tid = input("Traveller ID to delete: ").strip()
            enc_tid = encrypt(tid)
            db.delete_traveller(enc_tid, username)

        elif choice == "5":
            return
        elif choice == "6":
            # Handle logout
            print("Logging out...")
            logger.log_entry(f"{username}", "Logged out", "", "No")
            return
        elif choice == "7":
            # Handle exit
            print("Exiting the application...")
            logger.log_entry(f"{username}", "Exited the application", "", "No")
            exit(0)
        else:
            print("Invalid choice.")


def add_traveller(creator):
    db = Traveller()
    db.connect()
    logger = EncryptedLogger()

    print("\nAdd New Traveller")
    # First name validation
    while True:
        first_name = input("First Name: ").strip()
        if first_name and first_name.isalpha():
            logger.log_entry(
                f"{creator}", "Input accepted", f"First Name: {first_name}", "No"
            )
            break
        else:
            print(
                "First name must only contain letters and cannot be empty. Please try again."
            )
            logger.log_entry(
                f"{creator}", "Input failed", "Invalid First Name entry", "No"
            )

    # Last name validation
    while True:
        last_name = input("Last Name: ").strip()
        if last_name and last_name.isalpha():
            logger.log_entry(
                f"{creator}", "Input accepted", f"Last Name: {last_name}", "No"
            )
            break
        else:
            print(
                "Last name must only contain letters and cannot be empty. Please try again."
            )
            logger.log_entry(
                f"{creator}", "Input failed", "Invalid Last Name entry", "No"
            )

    # Birthday validation
    while True:
        birthday = input("Birthday (YYYY-MM-DD): ").strip()
        try:
            datetime.strptime(birthday, "%Y-%m-%d")
            logger.log_entry(
                f"{creator}", "Input accepted", f"Birthday: {birthday}", "No"
            )
            break
        except ValueError:
            print("Invalid date format. Please use YYYY-MM-DD.")
            logger.log_entry(
                f"{creator}", "Input failed", "Invalid Birthday entry", "No"
            )

    print("\nGender:")
    print("[1] Male")
    print("[2] Female")
    while True:
        gender_choice = input("Select gender (1 or 2): ").strip()
        if gender_choice == "1":
            gender = "Male"
            logger.log_entry(f"{creator}", "Input accepted", "Gender: Male", "No")
            break
        elif gender_choice == "2":
            gender = "Female"
            logger.log_entry(f"{creator}", "Input accepted", "Gender: Female", "No")
            break
        else:
            print("Invalid input. Please select 1 for Male or 2 for Female.")
            logger.log_entry(f"{creator}", "Input failed", "Invalid Gender entry", "No")

    # Street name validation
    while True:
        street_name = input("Street Name: ").strip()
        if street_name:
            logger.log_entry(
                f"{creator}", "Input accepted", f"Street Name: {street_name}", "No"
            )
            break
        else:
            print("Street name cannot be empty. Please try again.")
            logger.log_entry(
                f"{creator}", "Input failed", "Invalid Street Name entry", "No"
            )

    # House number validation
    while True:
        house_number = input("House Number: ").strip()
        if house_number.isdigit():
            logger.log_entry(
                f"{creator}", "Input accepted", f"House Number: {house_number}", "No"
            )
            break
        else:
            print("House number must be digits only. Please try again.")
            logger.log_entry(
                f"{creator}", "Input failed", "Invalid House Number entry", "No"
            )

    # Zip code validation loop
    while True:
        zip_code = input("Zip Code (DDDDXX format): ").strip().upper()
        if db.validate_zip_code(zip_code):
            logger.log_entry(
                f"{creator}", "Input accepted", f"Zip Code: {zip_code}", "No"
            )
            break
        else:
            print(
                "Invalid Zip Code format. Must be 4 digits followed by 2 uppercase letters (e.g., 1234AB). Please try again."
            )
            logger.log_entry(
                f"{creator}", "Input failed", "Invalid Zip Code entry", "No"
            )

    display_cities(db.cities)
    city = None
    while city is None:
        try:
            city_choice = input("Select city (1-10): ").strip()
            city_idx = int(city_choice) - 1
            city = db.cities[city_idx]
            logger.log_entry(f"{creator}", "Input accepted", f"City: {city}", "No")
        except (ValueError, IndexError):
            print("Invalid city selection")
            display_cities(db.cities)
            logger.log_entry(f"{creator}", "Input failed", "Invalid City entry", "No")

    # Email validation
    email_regex = r"^[\w\.-]+@[\w\.-]+\.\w+$"
    while True:
        email = is_valid_email(input("Email: ").strip())
        if re.match(email_regex, email):
            logger.log_entry(f"{creator}", "Input accepted", f"Email: {email}", "No")
            break
        else:
            print("Invalid email format. Please try again.")
            logger.log_entry(f"{creator}", "Input failed", "Invalid Email entry", "No")

    # Phone validation loop
    while True:
        phone = input("Phone (8 digits only): ").strip()
        try:
            db.format_phone(phone)
            logger.log_entry(f"{creator}", "Input accepted", f"Phone: {phone}", "No")
            break
        except ValueError as e:
            print(f"{e} Please try again.")
            logger.log_entry(f"{creator}", "Input failed", "Invalid Phone entry", "No")

    # Driving license validation loop
    while True:
        driving_license = (
            input("Driving License (XXDDDDDDD or XDDDDDDDD format): ").strip().upper()
        )
        if db.validate_driving_license(driving_license):
            logger.log_entry(
                f"{creator}",
                "Input accepted",
                f"Driving License: {driving_license}",
                "No",
            )
            break
        else:
            print("Invalid Driving License format. Please try again.")
            logger.log_entry(
                f"{creator}", "Input failed", "Invalid Driving License entry", "No"
            )

    # Encrypt all fields before inserting traveller
    enc_first_name = encrypt(first_name)
    enc_last_name = encrypt(last_name)
    enc_birthday = encrypt(birthday)
    enc_gender = encrypt(gender)
    enc_street_name = encrypt(street_name)
    enc_house_number = encrypt(house_number)
    enc_zip_code = encrypt(zip_code)
    enc_city = encrypt(city)
    enc_email = encrypt(email)
    enc_phone = encrypt(phone)
    enc_driving_license = encrypt(driving_license)

    # Attempt to add traveller
    success = db.insert_traveller(
        enc_first_name,
        enc_last_name,
        enc_birthday,
        enc_gender,
        enc_street_name,
        enc_house_number,
        enc_zip_code,
        enc_city,
        enc_email,
        enc_phone,
        enc_driving_license,
    )
    if success:
        logger.log_entry(
            f"{creator}",
            "Created a new Traveller",
            f"Traveller: {first_name} is created",
            "No",
        )
    else:
        print("Failed to add traveller. Please check your input and try again.")


def view_travellers(username):
    db = Traveller()
    db.connect()
    logger = EncryptedLogger()
    search_term = input("Enter search term (leave blank for all): ").strip()
    if search_term:
        travellers = db.search_travellers(search_term)
        logger.log_entry(
            f"{username}", "Searched Travellers", f"Search term: {search_term}", "No"
        )
    else:
        travellers = db.get_all_travellers()
        logger.log_entry(f"{username}", "Viewed All Travellers", "", "No")
    if travellers:
        print("\nTraveller List:")
        print("-" * 100)
        print(
            "ID  | First Name   | Last Name    | Email                | Phone         | City"
        )
        print("-" * 100)
        for t in travellers:
            # Decrypt all relevant fields before displaying
            tid = t[0]
            first_name = decrypt(t[1])
            last_name = decrypt(t[2])
            email = decrypt(t[9])
            phone = decrypt(t[10])
            city = decrypt(t[8])
            print(
                f"{tid:<4}| {first_name:<12}| {last_name:<12}| {email:<20}| {phone:<14}| {city}"
            )
        print("-" * 100)
    else:
        print("No matching travellers found.")


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

    enc_val = encrypt(new_val)

    db.update_traveller(tid, **{field_map[field]: enc_val})
    logger.log_entry(
        f"{updater}",
        "Updated a Traveller",
        f"Traveller {tid}: {field_map[field]} is updated to {new_val}",
        "No",
    )
