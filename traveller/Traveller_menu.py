import re
from datetime import datetime
from DbContext.crypto_utils import decrypt, encrypt
from DbContext.encrypted_logger import EncryptedLogger

from traveller.Traveller import Traveller
from validation.isValidBirthday import is_valid_birthday
from validation.isValidDrivingLicense import is_valid_driving_license
from validation.isValidEmail import is_valid_email
from validation.isValidHouseNumber import is_valid_house_number
from validation.isValidName import is_valid_name
from validation.isValidPhone import is_valid_phone, validate_phone
from validation.isValidStreetName import is_valid_street_name
from validation.isValidZipCode import is_valid_zip_code


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
            shown = show_travellers(method="update")
            if not shown:
                continue
            else:
                update_traveller(username, shown)
        
        elif choice == "4":
            db = Traveller()
            db.connect()
            shown = show_travellers(method="delete")
            if not shown:
                continue
            else:
                db.delete_traveller(username, shown)

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
    logger = EncryptedLogger()
    db.connect()
    
    MAX_TRIES = 3

    print("\nAdd New Traveller")
    
    # First name validation
    first_name = input("First Name: ")
    tries = 0
    while not is_valid_name(first_name):
        tries += 1
        print(f"You have {MAX_TRIES - tries} attempts left")
        if tries < MAX_TRIES:
            print("First name must only contain letters and cannot be empty. Please try again.")
            first_name = input("First Name: ")
        else:
            print("Too many invalid attempts. Exiting add traveller.")
            logger.log_entry(f"{creator}", "Add traveller cancelled", "Too many invalid first name attempts", "Yes")
            return
    logger.log_entry(f"{creator}", "Input accepted", f"First Name: {first_name}", "No")

    # Last name validation
    last_name = input("Last Name: ")
    tries = 0
    while not is_valid_name(last_name):
        tries += 1
        print(f"You have {MAX_TRIES - tries} attempts left")
        if tries < MAX_TRIES:
            print("Last name must only contain letters and cannot be empty. Please try again.")
            last_name = input("Last Name: ")
        else:
            print("Too many invalid attempts. Exiting add traveller.")
            logger.log_entry(f"{creator}", "Add traveller cancelled", "Too many invalid last name attempts", "Yes")
            return
    logger.log_entry(f"{creator}", "Input accepted", f"Last Name: {last_name}", "No")

    # Birthday validation
    while True:
        birthday = input("Birthday (YYYY-MM-DD): ")
        if is_valid_birthday(birthday):
            logger.log_entry(f"{creator}", "Input accepted", f"Birthday: {birthday}", "No")
            break
        print("Invalid birthday. Please use format YYYY-MM-DD and a realistic date.")
        logger.log_entry(f"{creator}", "Input failed", "Invalid Birthday entry", "No")
    
    # Gender selection
    print("\nGender:")
    print("[1] Male")
    print("[2] Female")
    while True:
        gender_choice = input("Select gender (1 or 2): ")
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
    street_name = input("Street Name: ")
    tries = 0
    while not is_valid_street_name(street_name):
        tries += 1
        print(f"You have {MAX_TRIES - tries} attempts left")
        if tries < MAX_TRIES:
            print("Invalid street name. Must include letters and only allowed characters.")
            street_name = input("Street Name: ")
        else:
            print("Too many invalid attempts. Exiting add traveller.")
            logger.log_entry(f"{creator}", "Add traveller cancelled", "Too many invalid street name attempts", "Yes")
            return
    logger.log_entry(f"{creator}", "Input accepted", f"Street Name: {street_name}", "No")

    # House number validation
    while True:
        house_number = input("House Number: ")
        if is_valid_house_number(house_number):
            logger.log_entry(f"{creator}", "Input accepted", f"House Number: {house_number}", "No")
            break
        print("House number must be digits only and no longer than 4 digits. Please try again.")
        logger.log_entry(f"{creator}", "Input failed", "Invalid House Number entry", "No")

    # Zip code validation loop
    while True:
        zip_code = input("Zip Code (DDDDXX format): ")
        if is_valid_zip_code(zip_code):
            logger.log_entry(f"{creator}", "Input accepted", f"Zip Code: {zip_code}", "No")
            break
        print("Invalid Zip Code format. Must be 4 digits followed by 2 uppercase letters (e.g., 1234AB). Please try again.")
        logger.log_entry(f"{creator}", "Input failed", "Invalid Zip Code entry", "No")

    # City selection
    if not db.cities:
        print("No cities available. Contact administrator.")
        return
    
    display_cities(db.cities)
    city = None
    while city is None:
        try:
            city_choice = input(f"Select city (1-{len(db.cities)}): ")
            if not city_choice.isdigit():
                raise ValueError
            if int(city_choice) < 1 or int(city_choice) > len(db.cities):
                raise IndexError
            city_idx = int(city_choice) - 1
            city = db.cities[city_idx]
            logger.log_entry(f"{creator}", "Input accepted", f"City: {city}", "No")
        except (ValueError, IndexError):
            print("Invalid city selection")
            display_cities(db.cities)
            logger.log_entry(f"{creator}", "Input failed", "Invalid City entry", "No")

    # Email validation
    email = input("Email: ")
    tries = 0
    while not is_valid_email(email):
        tries += 1
        print(f"You have {MAX_TRIES - tries} attempts left")
        if tries < MAX_TRIES:
            print("Invalid email format. Please try again.")
            email = input("Email: ")
        else:
            print("Too many invalid attempts. Exiting add traveller.")
            logger.log_entry(f"{creator}", "Add traveller cancelled", "Too many invalid email attempts", "Yes")
            return
    logger.log_entry(f"{creator}", "Input accepted", f"Email: {email}", "No")

    # Phone validation loop
    phone = input("Phone (8 digits only): ")
    tries = 0
    while not is_valid_phone(phone):
        tries += 1
        print(f"You have {MAX_TRIES - tries} attempts left")
        if tries < MAX_TRIES:
            print("Phone number must contain exactly 8 digits. Please try again.")
            phone = input("Phone (8 digits only): ")
        else:
            print("Too many invalid attempts. Exiting add traveller.")
            logger.log_entry(f"{creator}", "Add traveller cancelled", "Too many invalid phone attempts", "Yes")
            return
    phone, is_valid = validate_phone(phone)
    logger.log_entry(f"{creator}", "Input accepted", f"Phone: {phone}", "No")

    # Driving license validation loop
    while True:
        driving_license = input("Driving License (XXDDDDDDD or XDDDDDDDD format): ")
        if is_valid_driving_license(driving_license):
            logger.log_entry(f"{creator}","Input accepted",f"Driving License: {driving_license}","No")
            break
        else:
            print("Invalid Driving License format. Please try again.")
            logger.log_entry(f"{creator}", "Input failed", "Invalid Driving License entry", "No")

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
    traveller_id = db.insert_traveller(
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
    if traveller_id:
        logger.log_entry(
            f"{creator}",
            "Created a new Traveller",
            f"Traveller: {first_name} is created",
            "No",
        )
        print(f"Traveller created with ID: {decrypt(traveller_id)}")
    else:
        print("Failed to add traveller. Please check your input and try again.")

def update_traveller(updater,tid):
    db = Traveller()
    logger = EncryptedLogger()
    db.connect()
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
    print("[12] Cancel Update")
    
    field = input("Field to update: ")

    new_val = None
    fail_count = 0
    MAX_TRIES = 3

    def log_suspicious(field_name):
        if not log_suspicious.logged:
            logger.log_entry(
                f"{updater}",
                "Suspicious behavior detected",
                f"Failed {field_name} verification while updating traveller {tid}",
                "Yes",
            )
            log_suspicious.logged = True

    log_suspicious.logged = False

    if field == "1":  # first Name
        while True:
            new_val = input("New first Name: ")
            if new_val and is_valid_name(new_val):
                break

            print("Invalid First Name. Please use only letters.")
            fail_count += 1
            print(f"You have {MAX_TRIES - fail_count} attempts left")
            if fail_count >= MAX_TRIES:
                log_suspicious("First Name")
                print("Too many failed attempts. Suspicious behavior logged.")
                return

    elif field == "2":  # Last Name
        while True:
            new_val = input("New Last Name: ")
            if new_val and is_valid_name(new_val):
                break

            print("Invalid Last Name. Please use only letters.")
            fail_count += 1
            print(f"You have {MAX_TRIES - fail_count} attempts left")
            if fail_count >= MAX_TRIES:
                log_suspicious("Last Name")
                print("Too many failed attempts. Suspicious behavior logged.")
                return

    elif field == "3":  # Birthday
        while True:
            new_val = input("New Birthday (YYYY-MM-DD): ")
            if new_val and is_valid_birthday(new_val):
                break

            print("Invalid birthday. Please use format YYYY-MM-DD and a realistic date.")
            fail_count += 1
            print(f"You have {MAX_TRIES - fail_count} attempts left")
            if fail_count >= MAX_TRIES:
                log_suspicious("Birthday")
                print("Too many failed attempts. Suspicious behavior logged.")
                return

    elif field == "4":  # Gender
        while True:
            print("[1] Male")
            print("[2] Female")
            gender_choice = input("Select gender (1 or 2): ")
            if gender_choice == "1":
                new_val = "Male"
                break
            elif gender_choice == "2":
                new_val = "Female"
                break
            else:
                print("Invalid input. Please select 1 for Male or 2 for Female.")
                fail_count += 1
                print(f"You have {MAX_TRIES - fail_count} attempts left")
                if fail_count >= MAX_TRIES:
                    log_suspicious("Gender")
                    print("Too many failed attempts. Suspicious behavior logged.")
                    return

    elif field == "5":  # Street Name
        while True:
            new_val = input("New Street Name: ")
            if new_val and is_valid_street_name(new_val):
                break

            print("Invalid street name. Must include letters and only allowed characters.")
            fail_count += 1
            print(f"You have {MAX_TRIES - fail_count} attempts left")
            if fail_count >= MAX_TRIES:
                log_suspicious("Street Name")
                print("Too many failed attempts. Suspicious behavior logged.")
                return

    elif field == "6":  # House Number
        while True:
            new_val = input("New House Number: ")
            if new_val and is_valid_house_number(new_val):
                break

            print("House number must be digits only and maximum 4 digits. Please try again.")
            fail_count += 1
            print(f"You have {MAX_TRIES - fail_count} attempts left")
            if fail_count >= MAX_TRIES:
                log_suspicious("House Number")
                print("Too many failed attempts. Suspicious behavior logged.")
                return

    elif field == "7":  # Zip Code
        while True:
            new_val = input("New Zip Code (DDDDXX format): ")
            if new_val and is_valid_zip_code(new_val):
                break

            print("Invalid Zip Code format. Must be 4 digits followed by 2 uppercase letters (e.g., 1234AB). Please try again.")
            fail_count += 1
            print(f"You have {MAX_TRIES - fail_count} attempts left")
            if fail_count >= MAX_TRIES:
                log_suspicious("Zip Code")
                print("Too many failed attempts. Suspicious behavior logged.")
                return

    elif field == "8":  # City
        display_cities(db.cities)
        while True:
            try:
                city_choice = input("Select city (1-10): ")
                city_idx = int(city_choice) - 1
                new_val = db.cities[city_idx]
                break
            except (ValueError, IndexError):
                print("Invalid city selection")
                fail_count += 1
                print(f"You have {MAX_TRIES - fail_count} attempts left")
                if fail_count >= MAX_TRIES:
                    log_suspicious("City")
                    print("Too many failed attempts. Suspicious behavior logged.")
                    return

    elif field == "9":  # Email
        while True:
            new_val = input("New Email: ")
            if new_val and is_valid_email(new_val):
                break

            print("Invalid email format. Please try again.")
            fail_count += 1
            print(f"You have {MAX_TRIES - fail_count} attempts left")
            if fail_count >= MAX_TRIES:
                log_suspicious("Email")
                print("Too many failed attempts. Suspicious behavior logged.")
                return

    elif field == "10":  # Phone
        while True:
            new_val = input("New Phone (8 digits only): ")
            if new_val and is_valid_phone(new_val):
                new_val, valid_phone = validate_phone(new_val)
                break

            print("Phone number must contain exactly 8 digits. Please try again.")
            fail_count += 1
            print(f"You have {MAX_TRIES - fail_count} attempts left")
            if fail_count >= MAX_TRIES:
                log_suspicious("Phone")
                print("Too many failed attempts. Suspicious behavior logged.")
                return

    elif field == "11":  # Driving License
        while True:
            new_val = input("New Driving License (XXDDDDDDD or XDDDDDDDD format): ")
            if new_val and is_valid_driving_license(new_val):
                break

            print("Invalid Driving License format. Must be XXDDDDDDD or XDDDDDDDD (e.g., AB1234567 or A12345678). Please try again.")
            fail_count += 1
            print(f"You have {MAX_TRIES - fail_count} attempts left")
            if fail_count >= MAX_TRIES:
                log_suspicious("Driving License")
                print("Too many failed attempts. Suspicious behavior logged.")
                return

    elif field == "12":  # Cancel Update
        print("Update cancelled.")
        return

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
    logger.log_entry(f"{updater}", "Updated a Traveller", f"Traveller {decrypt(tid)}: {field_map[field]} is updated to {new_val}", "No")

def show_travellers(method):
    db = Traveller()
    db.connect()
    travellers = db.get_all_travellers()
    if travellers:
        print("\nTraveller List:")
        print("-" * 100)
        # "TravellerID","FirstName","LastName","Birthday","Gender","StreetName","HouseNumber","ZipCode","City","Email","Phone","DrivingLicenseNumber","RegisteredDate"
        print(
            "ID  | First Name   | Last Name    | Birthday    | Gender   | Street Name        | House No | Zip Code | City         | Email                | Phone         | Driving License | Registered Date"
        )
        print("-" * 100)
        for t in travellers:
            # Decrypt all relevant fields before displaying
            idx = travellers.index(t) + 1
            first_name = decrypt(t[1])
            last_name = decrypt(t[2])
            birthday = decrypt(t[3])
            gender = decrypt(t[4])
            street_name = decrypt(t[5])
            house_number = decrypt(t[6])
            zip_code = decrypt(t[7])
            city = decrypt(t[8])
            email = decrypt(t[9])
            phone = decrypt(t[10])
            driving_license = decrypt(t[11])
            registered_date = decrypt(t[12])
            print(
                f"{idx:<4}| {first_name:<12}| {last_name:<12}| {birthday:<12}| {gender:<12}| {street_name:<12}| {house_number:<12}| {zip_code:<12}| {city:<12}| {email:<20}| {phone:<14}| {driving_license:<12}| {registered_date:<12}"
            )
        print("-" * 100)
        if method == "update":
            idxchosen = input("Traveller ID to update: ")
        if method == "delete":
            idxchosen = input("Traveller ID to delete: ")
        # Validate selection
        while not idxchosen.isdigit() or int(idxchosen) < 1 or int(idxchosen) > len(travellers):
            print("Invalid selection. Please choose a valid Traveller ID from the list.")
            idxchosen = input("Traveller ID to update: ")
        encrypted_id = travellers[int(idxchosen)-1][0]

        return encrypted_id
    else:
        print("No travellers found.")
        return None

def view_travellers(username):
    db = Traveller()
    db.connect()
    logger = EncryptedLogger()
    search_term = input("Enter search term (leave blank for all): ")
    if search_term:
        travellers = db.search_travellers(search_term)
        logger.log_entry(
            f"{username}", "Searched Travellers", f"Search term: {search_term}", "No"
        )
    else:
        travellers = db.search_travellers()
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
            tid = decrypt(t[0])
            first_name = decrypt(t[1])
            last_name = decrypt(t[2])
            email = decrypt(t[9])
            phone = decrypt(t[10])
            city = decrypt(t[8])
            registered_date = decrypt(t[12])
            print(
                f"{tid:<4}| {first_name:<12}| {last_name:<12}| {email:<20}| {phone:<14}| {city:<12}| {registered_date}"
            )
        print("-" * 100)
    else:
        print("No matching travellers found.")
