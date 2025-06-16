from datetime import datetime
from scooter.Scooter_data import Scooter_data


def Scooter_Menu_SerEng(choice):
    db = Scooter_data()
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
                        break
                    print(
                        f"Error: Must be within Rotterdam (Lat: 51.85-52.00, Lon: 4.30-4.60)"
                    )
                except ValueError:
                    print("Error: Invalid coordinate format")
            db.update_scooter_fields(sn, LocationLat=lat, LocationLong=lon)

        elif field_choice == "4":
            # Validate Out-of-Service status (y/n)
            while True:
                oos_input = input("Out of Service? (y/n): ").lower().strip()
                if oos_input in ("y", "n"):
                    oos = oos_input == "y"
                    break
                print("Error: Enter 'y' or 'n'")
            db.update_scooter_fields(sn, OutOfService=int(oos))

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

        elif field_choice == "6":
            # Validate Last Maintenance Date (ISO 8601)
            while True:
                date = input("Last Maintenance Date (YYYY-MM-DD): ").strip()
                try:
                    datetime.strptime(date, "%Y-%m-%d")
                    break
                except ValueError:
                    print("Error: Use YYYY-MM-DD format")
            db.update_scooter_fields(sn, LastMaintenanceDate=date)
        elif choice == "3":
            return
        else:
            print("Invalid choice.")