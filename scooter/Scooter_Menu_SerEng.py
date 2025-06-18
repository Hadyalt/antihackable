from datetime import datetime
from DbContext.encrypted_logger import EncryptedLogger
from scooter.Scooter_data import Scooter_data
from input_output_utils import validate_input, sanitize_output


def Scooter_Menu_SerEng(choice, updater):
    db = Scooter_data()
    logger = EncryptedLogger()
    db.connect()
    if choice == "1":  # View Scooters
        search_term = input("Enter search term (leave blank for all): ").strip()
        if search_term:
            scooters = db.search_scooters(search_term)
        else:
            scooters = db.get_all_scooters()

        if scooters:
            for s in scooters:
                print(sanitize_output(str(s)))
        else:
            print(sanitize_output("No matching scooters found"))
    elif choice == "2":
        print(sanitize_output("\nList of Scooters:"))
        scooters = db.get_all_serial_numbers()
        for s in scooters:
            print(sanitize_output(f"- {s[0]}"))
        sn = validate_input(input("Serial Number to update: ").strip(), min_length=1, context="Serial Number to update")

        # Fetch existing scooter data
        scooter = db.get_scooter_by_serial(sn)
        if not scooter:
            print(sanitize_output("Scooter not found!"))
            return

        print(sanitize_output("\n[1] State of Charge"))
        print(sanitize_output("[2] Target Range SoC"))
        print(sanitize_output("[3] Location"))
        print(sanitize_output("[4] Out-of-service Status"))
        print(sanitize_output("[5] Mileage"))
        print(sanitize_output("[6] Last Maintenance Date"))

        field_choice = validate_input(input("\nChoose field to update: ").strip(), pattern=r"^[1-6]$", context="Scooter Field Choice")
        if field_choice == "1":
            # Validate State of Charge (0-100%)
            while True:
                try:
                    new_value = float(validate_input(input("New State of Charge (%): ").strip(), context="State of Charge"))
                    if 0 <= new_value <= 100:
                        break
                    print(sanitize_output("Error: Must be 0-100%"))
                except ValueError:
                    print(sanitize_output("Error: Invalid number format"))
            db.update_scooter_fields(sn, StateOfCharge=new_value)
            logger.log_entry(f"{updater}", f"Updated scooter {sn}", f"Updated the State of Charge to {new_value}", "No")

        elif field_choice == "2":
            # Validate Target Range SOC (min < max, both 0-100%)
            while True:
                try:
                    min_val = float(validate_input(input("New Min SoC (%): ").strip(), context="Min SoC"))
                    max_val = float(validate_input(input("New Max SoC (%): ").strip(), context="Max SoC"))
                    if 0 <= min_val <= max_val <= 100:
                        break
                    print(sanitize_output("Error: Min must be ≤ Max (both 0-100%)"))
                except ValueError:
                    print(sanitize_output("Error: Invalid number format"))
            db.update_scooter_fields(sn, TargetRangeSocMin=min_val, TargetRangeSocMax=max_val)
            logger.log_entry(f"{updater}", f"Updated scooter {sn}", f"Updated the target range SOC to {min_val} - {max_val}", "No")

        elif field_choice == "3":
            # Validate Location (5 decimal places, within Rotterdam)
            ROTTERDAM_BOUNDS = {"min_lat": 51.85, "max_lat": 52.0, "min_lon": 4.3, "max_lon": 4.6}
            while True:
                try:
                    lat = round(float(validate_input(input("New Latitude: ").strip(), context="Latitude")), 5)
                    lon = round(float(validate_input(input("New Longitude: ").strip(), context="Longitude")), 5)
                    if (ROTERDAM_BOUNDS["min_lat"] <= lat <= ROTTERDAM_BOUNDS["max_lat"] and ROTTERDAM_BOUNDS["min_lon"] <= lon <= ROTTERDAM_BOUNDS["max_lon"]):
                        break
                    print(sanitize_output("Error: Must be within Rotterdam (Lat: 51.85-52.00, Lon: 4.30-4.60)"))
                except ValueError:
                    print(sanitize_output("Error: Invalid coordinate format"))
            db.update_scooter_fields(sn, LocationLat=lat, LocationLong=lon)
            logger.log_entry(f"{updater}", f"Updated scooter {sn}", f"Updated the location to ({lat}, {lon})", "No")

        elif field_choice == "4":
            # Validate Out-of-Service status (y/n)
            while True:
                oos_input = validate_input(input("Out of Service? (y/n): ").lower().strip(), pattern=r"^[yn]$", context="Out of Service")
                if oos_input in ("y", "n"):
                    oos = oos_input == "y"
                    break
                print(sanitize_output("Error: Enter 'y' or 'n'"))

            db.update_scooter_fields(sn, OutOfService=int(oos))
            logger.log_entry(f"{updater}", f"Updated scooter {sn}", f"Updated out of service to {oos_input}", "No")

        elif field_choice == "5":
            # Validate Mileage (non-negative)
            while True:
                try:
                    mileage = float(validate_input(input("New Mileage (km): ").strip(), context="Mileage"))
                    if mileage >= 0:
                        break
                    print(sanitize_output("Error: Cannot be negative"))
                except ValueError:
                    print(sanitize_output("Error: Invalid number format"))
            db.update_scooter_fields(sn, Mileage=mileage)
            logger.log_entry(f"{updater}", f"Updated scooter {sn}", f"Updated the mileage to {mileage}", "No")

        elif field_choice == "6":
            # Validate Last Maintenance Date (ISO 8601)
            while True:
                date = input("Last Maintenance Date (YYYY-MM-DD): ").strip()
                try:
                    date = validate_input(date, pattern=r"^\d{4}-\d{2}-\d{2}$", context="Last Maintenance Date")
                    datetime.strptime(date, "%Y-%m-%d")
                    break
                except ValueError:
                    print(sanitize_output("Error: Use YYYY-MM-DD format"))
            db.update_scooter_fields(sn, LastMaintenanceDate=date)
            logger.log_entry(f"{updater}", f"Updated scooter {sn}", f"Updated the last maintenance date to {date}", "No")
        elif choice == "3":
            return
        else:
            print(sanitize_output("Invalid choice."))