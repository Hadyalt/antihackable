from DbContext.encrypted_logger import EncryptedLogger
from models.Scooter import Scooter
from scooter.Scooter_Menu_SerEng import Scooter_Menu_SerEng
from scooter.Scooter_data import Scooter_data
from datetime import datetime

def show_menu(role):
    if role in ["superadmin", "systemadmin"]:
        print("""
[1] Add Scooter
[2] View Scooters
[3] Update Scooter
[4] Delete Scooter
[5] Exit
""")
    elif role == "serviceengineer":
        print("""
[1] View Scooters
[2] Update Scooter
[3] Exit
""")


def main(role, username):
    db = Scooter_data()
    db.connect()

    while True:
        show_menu(role)
        choice = input("Choose an option: ")

        # ADMIN MENU
        if role in ["superadmin", "systemadmin"]:
            if choice == "1":
                add_scooter(username)
            elif choice == "2":
                search_term = input("Enter search term (leave blank for all): ").strip()
                if search_term:
                    scooters = db.search_scooters(search_term)
                else:
                    scooters = db.get_all_scooters()
                if scooters:
                    for s in scooters:
                        print(s)
                else:
                    print("No matching scooters found")
            elif choice == "3":
                update_scooter(username)
            elif choice == "4":
                print("\nList of Scooters:")
                scooters = db.get_all_serial_numbers()
                for s in scooters:
                    print(f"- {s[0]}")
                sn = input("\nSerial Number to delete: ")
                db.delete_scooter(sn, username)

            elif choice == "5":
                print("Exiting.")
                break

            else:
                print("Invalid choice.")

        # SERVICE ENGINEER MENU
        elif role == "serviceengineer":
            Scooter_Menu_SerEng(choice)

        # INVALID ROLE
        else:
            print("Invalid role.")
            break
    db.close()

def add_scooter(creator):
    db = Scooter_data()
    db.connect()
    # Define Rotterdam geographic bounds
    ROTTERDAM_BOUNDS = {
        "min_lat": 51.85,
        "max_lat": 52.0,
        "min_lon": 4.3,
        "max_lon": 4.6,
    }

    brand = input("Brand: ")
    model = input("Model: ")

    # Validate Serial Number (10-17 alphanumeric characters)
    while True:
        serial_number = input(
            "Serial Number (10-17 alphanumeric chars): "
        ).strip()
        if 10 <= len(serial_number) <= 17 and serial_number.isalnum():
            break
        print("Error: Must be 10-17 alphanumeric characters")

    # Validate Top Speed (positive number)
    while True:
        try:
            top_speed = float(input("Top Speed (km/h): "))
            if top_speed > 0:
                break
            print("Error: Must be a positive number")
        except ValueError:
            print("Error: Invalid number format")

    # Validate Battery Capacity (positive number)
    while True:
        try:
            battery_capacity = float(input("Battery Capacity (Wh): "))
            if battery_capacity > 0:
                break
            print("Error: Must be a positive number")
        except ValueError:
            print("Error: Invalid number format")

    # Validate State of Charge (0-100%)
    while True:
        try:
            state_of_charge = float(input("State of Charge (%): "))
            if 0 <= state_of_charge <= 100:
                break
            print("Error: Must be 0-100%")
        except ValueError:
            print("Error: Invalid number format")

    # Validate Target Range SOC (min < max, both 0-100%)
    while True:
        try:
            min_soc = float(input("Target Range Min (%): "))
            max_soc = float(input("Target Range Max (%): "))
            if 0 <= min_soc <= max_soc <= 100:
                target_range_soc = (min_soc, max_soc)
                break
            print("Error: Min must be ≤ Max (both 0-100%)")
        except ValueError:
            print("Error: Invalid number format")

    # Validate Location (5 decimal places, within Rotterdam)
    while True:
        try:
            lat = round(float(input("Latitude: ")), 5)
            lon = round(float(input("Longitude: ")), 5)
            if (
                ROTTERDAM_BOUNDS["min_lat"]
                <= lat
                <= ROTTERDAM_BOUNDS["max_lat"]
                and ROTTERDAM_BOUNDS["min_lon"]
                <= lon
                <= ROTTERDAM_BOUNDS["max_lon"]
            ):
                location = (lat, lon)
                break
            print(
                f"Error: Must be within Rotterdam (Lat: 51.85-52.00, Lon: 4.30-4.60)"
            )
        except ValueError:
            print("Error: Invalid coordinate format")

    # Validate Out-of-Service status (y/n)
    while True:
        oos_input = input("Out of Service? (y/n): ").lower().strip()
        if oos_input in ("y", "n"):
            out_of_service = oos_input == "y"
            break
        print("Error: Enter 'y' or 'n'")

    # Validate Mileage (non-negative)
    while True:
        try:
            mileage = float(input("Mileage (km): "))
            if mileage >= 0:
                break
            print("Error: Cannot be negative")
        except ValueError:
            print("Error: Invalid number format")

    # Validate Last Maintenance Date (ISO 8601)
    while True:
        last_maintenance_date = input(
            "Last Maintenance Date (YYYY-MM-DD): "
        ).strip()
        try:
            datetime.strptime(last_maintenance_date, "%Y-%m-%d")
            break
        except ValueError:
            print("Error: Use YYYY-MM-DD format")

    # Create Scooter object and insert into DB
    scooter = Scooter(
        brand=brand,
        model=model,
        serial_number=serial_number,
        top_speed=top_speed,
        battery_capacity=battery_capacity,
        state_of_charge=state_of_charge,
        target_range_soc=target_range_soc,
        location=location,
        out_of_service=out_of_service,
        mileage=mileage,
        last_maintenance_date=last_maintenance_date,
    )
    db.insert_scooter(scooter)
    logger = EncryptedLogger()
    logger.log_entry(f"{creator}", "Added a scooter", f"Added scooter with serial number {serial_number}", "No")

def update_scooter(updater):
    db = Scooter_data()
    logger = EncryptedLogger()
    db.connect()
    print("\nList of Scooters:")
    scooters = db.get_all_serial_numbers()
    for s in scooters:
        print(f"- {s[0]}")
    sn = input("\nSerial Number to update: ")
    # Fetch existing scooter data
    scooter = db.get_scooter_by_serial(sn)
    if not scooter:
        print("Scooter not found!")
        return

    print("\n[1] Brand")
    print("[2] Model")
    print("[3] Serial number")
    print("[4] Top speed (km/h)")
    print("[5] Battery capacity (Wh)")
    print("[6] State of Charge")
    print("[7] Target Range SoC")
    print("[8] Location")
    print("[9] Out-of-service Status")
    print("[10] Mileage")
    print("[11] Last Maintenance Date")

    field_choice = input("\nChoose field to update: ")

    if field_choice == "1":  # Brand
        new_brand = input("New Brand: ").strip()
        if new_brand:
            db.update_scooter_fields(sn, Brand=new_brand)
            logger.log_entry(f"{updater}", f"Updated scooter {sn}", f"Updated the brand to {new_brand}", "No")
        else:
            print("Error: Brand cannot be empty")

    elif field_choice == "2":  # Model
        new_model = input("New Model: ").strip()
        if new_model:
            db.update_scooter_fields(sn, Model=new_model)
            logger.log_entry(f"{updater}", f"Updated scooter {sn}", f"Updated the model to {new_model}", "No")
        else:
            print("Error: Model cannot be empty")

    elif field_choice == "3":  # Serial Number
        while True:
            new_serial = input(
                "New Serial Number (10-17 alphanumeric chars): "
            ).strip()
            if 10 <= len(new_serial) <= 17 and new_serial.isalnum():
                # Check if serial number exists
                if (
                    db.get_scooter_by_serial(new_serial)
                    and new_serial != sn
                ):
                    print("Error: Serial number already exists")
                else:
                    db.update_scooter_fields(sn, SerialNumber=new_serial)
                    logger.log_entry(f"{updater}", f"Updated scooter {sn}", f"Updated the serial number to {new_serial}", "No")
                    return
            else:
                print("Error: Must be 10-17 alphanumeric characters")

    elif field_choice == "4":  # Top Speed
        while True:
            try:
                new_top_speed = float(input("New Top Speed (km/h): "))
                if new_top_speed > 0:
                    db.update_scooter_fields(sn, TopSpeed=new_top_speed)
                    logger.log_entry(f"{updater}", f"Updated scooter {sn}", f"Updated the top speed to {new_top_speed}", "No")
                    return
                print("Error: Must be a positive number")
            except ValueError:
                print("Error: Invalid number format")

    elif field_choice == "5":  # Battery Capacity
        while True:
            try:
                new_battery_capacity = float(
                    input("New Battery Capacity (Wh): ")
                )
                if new_battery_capacity > 0:
                    db.update_scooter_fields(
                        sn, BatteryCapacity=new_battery_capacity
                    )
                    logger.log_entry(f"{updater}", f"Updated scooter {sn}", f"Updated the battery capacity to {new_battery_capacity}", "No")
                    return
                print("Error: Must be a positive number")
            except ValueError:
                print("Error: Invalid number format")

    elif field_choice == "6":  # State of Charge
        while True:
            try:
                new_value = float(input("New State of Charge (%): "))
                if 0 <= new_value <= 100:
                    db.update_scooter_fields(sn, StateOfCharge=new_value)
                    logger.log_entry(f"{updater}", f"Updated scooter {sn}", f"Updated the State of Charge to {new_value}", "No")
                    return
                print("Error: Must be 0-100%")
            except ValueError:
                print("Error: Invalid number format")

    elif field_choice == "7":  # Target Range SOC
        while True:
            try:
                min_val = float(input("New Min SoC (%): "))
                max_val = float(input("New Max SoC (%): "))
                if 0 <= min_val <= max_val <= 100:
                    db.update_scooter_fields(
                        sn,
                        TargetRangeSocMin=min_val,
                        TargetRangeSocMax=max_val,
                    )
                    logger.log_entry(f"{updater}", f"Updated scooter {sn}", f"Updated the target range SOC to {min_val} - {max_val}", "No")
                    return
                print("Error: Min must be ≤ Max (both 0-100%)")
            except ValueError:
                print("Error: Invalid number format")

    elif field_choice == "8":  # Location
        ROTTERDAM_BOUNDS = {
            "min_lat": 51.85,
            "max_lat": 52.0,
            "min_lon": 4.3,
            "max_lon": 4.6,
        }
        while True:
            try:
                lat = round(float(input("New Latitude: ")), 5)
                lon = round(float(input("New Longitude: ")), 5)
                if (
                    ROTTERDAM_BOUNDS["min_lat"]
                    <= lat
                    <= ROTTERDAM_BOUNDS["max_lat"]
                    and ROTTERDAM_BOUNDS["min_lon"]
                    <= lon
                    <= ROTTERDAM_BOUNDS["max_lon"]
                ):
                    db.update_scooter_fields(
                        sn, LocationLat=lat, LocationLong=lon
                    )
                    logger.log_entry(f"{updater}", f"Updated scooter {sn}", f"Updated the location to ({lat}, {lon})", "No")
                    return 
                print(
                    f"Error: Must be within Rotterdam (Lat: 51.85-52.00, Lon: 4.30-4.60)"
                )
            except ValueError:
                print("Error: Invalid coordinate format")

    elif field_choice == "9":  # Out-of-Service
        while True:
            oos_input = input("Out of Service? (y/n): ").lower().strip()
            if oos_input in ("y", "n"):
                oos = oos_input == "y"
                db.update_scooter_fields(sn, OutOfService=int(oos))
                logger.log_entry(f"{updater}", f"Updated scooter {sn}", f"Updated out of service to {oos_input}", "No")
                return
            print("Error: Enter 'y' or 'n'")

    elif field_choice == "10":  # Mileage
        while True:
            try:
                mileage = float(input("New Mileage (km): "))
                if mileage >= 0:
                    db.update_scooter_fields(sn, Mileage=mileage)
                    logger.log_entry(f"{updater}", f"Updated scooter {sn}", f"Updated the mileage to {mileage}", "No")
                    return 
                print("Error: Cannot be negative")
            except ValueError:
                print("Error: Invalid number format")

    elif field_choice == "11":  # Last Maintenance Date
        while True:
            date = input("Last Maintenance Date (YYYY-MM-DD): ").strip()
            try:
                datetime.strptime(date, "%Y-%m-%d")
                db.update_scooter_fields(sn, LastMaintenanceDate=date)
                logger.log_entry(f"{updater}", f"Updated scooter {sn}", f"Updated the last maintenance date to {date}", "No")
                return
            except ValueError:
                print("Error: Use YYYY-MM-DD format")
    else:
        print("Invalid field selection")


if __name__ == "__main__":
    main()
