from datetime import datetime
from DbContext.encrypted_logger import EncryptedLogger
from scooter.Scooter_data import Scooter_data


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
                print(s)
        else:
            print("No matching scooters found")
    elif choice == "2":
        print("\nList of Scooters:")
        scooters = db.get_all_serial_numbers()
        for s in scooters:
            print(f"- {s[0]}")
        sn = input("Serial Number to update: ")

        # Fetch existing scooter data
        scooter = db.get_scooter_by_serial(sn)
        if not scooter:
            print("Scooter not found!")
            return

        print("\n[1] State of Charge")
        print("[2] Target Range SoC")
        print("[3] Location")
        print("[4] Out-of-service Status")
        print("[5] Mileage")
        print("[6] Last Maintenance Date")

        field_choice = input("\nChoose field to update: ")
        if field_choice == "1":
            # Validate State of Charge (0-100%)
            while True:
                try:
                    new_value = float(input("New State of Charge (%): "))
                    if 0 <= new_value <= 100:
                        break
                    print("Error: Must be 0-100%")
                except ValueError:
                    print("Error: Invalid number format")
            db.update_scooter_fields(sn, StateOfCharge=new_value)
            logger.log_entry(
                f"{updater}",
                f"Updated scooter {sn}",
                f"Updated the State of Charge to {new_value}",
                "No",
            )

        elif field_choice == "2":
            # Validate Target Range SOC (min < max, both 0-100%)
            while True:
                try:
                    min_val = float(input("New Min SoC (%): "))
                    max_val = float(input("New Max SoC (%): "))
                    if 0 <= min_val <= max_val <= 100:
                        break
                    print("Error: Min must be ≤ Max (both 0-100%)")
                except ValueError:
                    print("Error: Invalid number format")
            db.update_scooter_fields(
                sn, TargetRangeSocMin=min_val, TargetRangeSocMax=max_val
            )
            logger.log_entry(
                f"{updater}",
                f"Updated scooter {sn}",
                f"Updated the target range SOC to {min_val} - {max_val}",
                "No",
            )

        elif field_choice == "3":
            # Validate Location (5 decimal places, within Rotterdam)
            ROTTERDAM_BOUNDS = {
                "min_lat": 51.85,
                "max_lat": 52.0,
                "min_lon": 4.3,
                "max_lon": 4.6,
            }
            while True:
                try:
                    lat = round(float(input("New Latitude (51.85-52.00): ")), 5)
                    lon = round(float(input("New Longitude (4.30-4.60): ")), 5)
                    if (
                        ROTTERDAM_BOUNDS["min_lat"]
                        <= lat
                        <= ROTTERDAM_BOUNDS["max_lat"]
                        and ROTTERDAM_BOUNDS["min_lon"]
                        <= lon
                        <= ROTTERDAM_BOUNDS["max_lon"]
                    ):
                        break
                    print(
                        f"Error: Must be within Rotterdam (Lat: 51.85-52.00, Lon: 4.30-4.60)"
                    )
                except ValueError:
                    print("Error: Invalid coordinate format")
            db.update_scooter_fields(sn, LocationLat=lat, LocationLong=lon)
            logger.log_entry(
                f"{updater}",
                f"Updated scooter {sn}",
                f"Updated the location to ({lat}, {lon})",
                "No",
            )

        elif field_choice == "4":
            # Validate Out-of-Service status (y/n)
            while True:
                oos_input = input("Out of Service? (y/n): ").lower().strip()
                if oos_input in ("y", "n"):
                    oos = oos_input == "y"
                    break
                print("Error: Enter 'y' or 'n'")
            db.update_scooter_fields(sn, OutOfService=int(oos))
            logger.log_entry(
                f"{updater}",
                f"Updated scooter {sn}",
                f"Updated out of service to {oos_input}",
                "No",
            )

        elif field_choice == "5":
            # Validate Mileage (non-negative)
            while True:
                try:
                    mileage = float(input("New Mileage (km): "))
                    if mileage >= 0:
                        break
                    print("Error: Cannot be negative")
                except ValueError:
                    print("Error: Invalid number format")
            db.update_scooter_fields(sn, Mileage=mileage)
            logger.log_entry(
                f"{updater}",
                f"Updated scooter {sn}",
                f"Updated the mileage to {mileage}",
                "No",
            )

        elif field_choice == "6":
            tries = 0
            while True:
                if tries >= 3:
                    print("Too many invalid attempts. Update cancelled.")
                    logger.log_entry(
                        f"{updater}",
                        f"Update cancelled for scooter {sn}",
                        "Too many invalid attempts",
                        "Yes",
                    )
                    return
                date = input("Last Maintenance Date (YYYY-MM-DD): ").strip()
                try:
                    date_obj = datetime.strptime(date, "%Y-%m-%d")
                    today = datetime.today()

                    if date_obj > today:
                        print("Error: Maintenance date cannot be in the future.")
                        tries += 1
                        continue
                    if date_obj.year < 1980:
                        tries += 1
                        print("Error: Maintenance date cannot be older than 1980.")
                        continue
                    db.update_scooter_fields(sn, LastMaintenanceDate=date)
                    logger.log_entry(
                        f"{updater}",
                        f"Updated scooter {sn}",
                        f"Updated the last maintenance date to {date}",
                        "No",
                    )
                    return
                except ValueError:
                    print("Error: Use YYYY-MM-DD format")
                    tries += 1
                    print("Error: Maintenance date cannot be older than 1980.")
                    db.update_scooter_fields(sn, LastMaintenanceDate=date)
                    logger.log_entry(
                        f"{updater}",
                        f"Updated scooter {sn}",
                        f"Updated the last maintenance date to {date}",
                        "No",
                    )
        elif choice == "3":
            return
        else:
            print("Invalid choice.")
