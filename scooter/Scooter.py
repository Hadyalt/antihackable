from models.Scooter import Scooter
from scooter.Scooter_data import Scooter_data
from datetime import datetime


def show_menu():
    print("""
[1] Add Scooter
[2] View Scooters
[3] Update Scooter State of Charge
[4] Delete Scooter
[5] Exit
""")


def main():
    db = Scooter_data()
    db.connect()

    while True:
        show_menu()
        choice = input("Choose an option: ")

        if choice == "1":
            # Define Rotterdam geographic bounds
            ROTTERDAM_BOUNDS = {
                'min_lat': 51.85, 'max_lat': 52.0,
                'min_lon': 4.3, 'max_lon': 4.6
            }

            brand = input("Brand: ")
            model = input("Model: ")

            # Validate Serial Number (10-17 alphanumeric characters)
            while True:
                serial_number = input("Serial Number (10-17 alphanumeric chars): ").strip()
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
                    if (ROTTERDAM_BOUNDS['min_lat'] <= lat <= ROTTERDAM_BOUNDS['max_lat'] and 
                        ROTTERDAM_BOUNDS['min_lon'] <= lon <= ROTTERDAM_BOUNDS['max_lon']):
                        location = (lat, lon)
                        break
                    print(f"Error: Must be within Rotterdam (Lat: 51.85-52.00, Lon: 4.30-4.60)")
                except ValueError:
                    print("Error: Invalid coordinate format")

            # Validate Out-of-Service status (y/n)
            while True:
                oos_input = input("Out of Service? (y/n): ").lower().strip()
                if oos_input in ('y', 'n'):
                    out_of_service = (oos_input == 'y')
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
                last_maintenance_date = input("Last Maintenance Date (YYYY-MM-DD): ").strip()
                try:
                    datetime.strptime(last_maintenance_date, '%Y-%m-%d')
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

        elif choice == "2":
            scooters = db.get_all_scooters()
            for s in scooters:
                print(s)

        elif choice == "3":
            sn = input("Serial Number to update: ")

            # Fetch existing scooter data
            scooter = db.get_scooter_by_serial(sn)
            if not scooter:
                print("Scooter not found!")
                continue

            print("\n[1] State of Charge")
            print("[2] Target Range SoC")
            print("[3] Location")
            print("[4] Out-of-service Status")
            print("[5] Mileage")
            print("[6] Last Maintenance Date")

            field_choice = input("\nChoose field to update: ")

            if field_choice == "1":
                new_value = float(input("New State of Charge (%): "))
                db.update_scooter_fields(sn, StateOfCharge=new_value)

            elif field_choice == "2":
                min_val = float(input("New Min SoC (%): "))
                max_val = float(input("New Max SoC (%): "))
                db.update_scooter_fields(
                    sn, TargetRangeSocMin=min_val, TargetRangeSocMax=max_val
                )

            elif field_choice == "3":
                lat = float(input("New Latitude: "))
                lon = float(input("New Longitude: "))
                db.update_scooter_fields(sn, LocationLat=lat, LocationLong=lon)

            elif field_choice == "4":
                oos = input("Out of Service? (y/n): ").lower() == "y"
                db.update_scooter_fields(sn, OutOfService=int(oos))

            elif field_choice == "5":
                mileage = float(input("New Mileage (km): "))
                db.update_scooter_fields(sn, Mileage=mileage)

            elif field_choice == "6":
                date = input("Last Maintenance Date (YYYY-MM-DD): ")
                db.update_scooter_fields(sn, LastMaintenanceDate=date)

            else:
                print("Invalid field selection")

        elif choice == "4":
            sn = input("Serial Number to delete: ")
            db.delete_scooter(sn)

        elif choice == "5":
            print("Exiting.")
            break

        else:
            print("Invalid choice.")

    db.close()


if __name__ == "__main__":
    main()
