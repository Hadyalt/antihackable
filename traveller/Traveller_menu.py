from traveller.Traveller import Traveller


def display_cities(cities):
    print("\nAvailable Cities:")
    for i, city in enumerate(cities, 1):
        print(f"[{i}] {city}")


def traveller_menu():
    db = Traveller()
    db.connect()

    while True:
        print("\nTraveller Menu")
        print("[1] Add Traveller")
        print("[2] View Travellers")
        print("[3] Update Traveller")
        print("[4] Delete Traveller")
        print("[5] Exit")
        choice = input("Choose an option: ")

        if choice == "1":
            print("\nAdd New Traveller")
            first_name = input("First Name: ").strip()
            last_name = input("Last Name: ").strip()
            birthday = input("Birthday (YYYY-MM-DD): ").strip()

            print("\nGender:")
            print("[1] Male")
            print("[2] Female")
            gender_choice = input("Select gender: ").strip()
            gender = "Male" if gender_choice == "1" else "Female"

            street_name = input("Street Name: ").strip()
            house_number = input("House Number: ").strip()

            zip_code = input("Zip Code (DDDDXX format): ").strip().upper()

            display_cities(db.cities)
            city_choice = input("Select city (1-10): ").strip()
            try:
                city_idx = int(city_choice) - 1
                city = db.cities[city_idx]
            except (ValueError, IndexError):
                print("Invalid city selection")
                continue

            email = input("Email: ").strip()

            phone = input("Phone (8 digits only): ").strip()

            driving_license = (
                input("Driving License (XXDDDDDDD or XDDDDDDDD format): ")
                .strip()
                .upper()
            )

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

        elif choice == "2":
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

        elif choice == "3":
            tid = input("Traveller ID to update: ").strip()
            traveller = db.get_traveller_by_id(tid)
            if not traveller:
                print("Traveller not found.")
                continue

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
                city_choice = input("Select city (1-10): ").strip()
                try:
                    city_idx = int(city_choice) - 1
                    new_val = db.cities[city_idx]
                except (ValueError, IndexError):
                    print("Invalid city selection")
                    continue

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
                continue

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

        elif choice == "4":
            tid = input("Traveller ID to delete: ").strip()
            db.delete_traveller(tid)

        elif choice == "5":
            db.close()
            print("Exiting.")
            break

        else:
            print("Invalid choice.")
