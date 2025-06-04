from models.Scooter import Scooter
from scooter.Scooter_data import Scooter_data


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
            scooter = Scooter(
                brand=input("Brand: "),
                model=input("Model: "),
                serial_number=input("Serial Number: "),
                top_speed=float(input("Top Speed (km/h): ")),
                battery_capacity=float(input("Battery Capacity (Wh): ")),
                state_of_charge=float(input("State of Charge (%): ")),
                target_range_soc=(
                    float(input("Target Range Min (%): ")),
                    float(input("Target Range Max (%): ")),
                ),
                location=(float(input("Latitude: ")), float(input("Longitude: "))),
                out_of_service=input("Out of Service? (y/n): ").lower() == "y",
                mileage=float(input("Mileage (km): ")),
                last_maintenance_date=input("Last Maintenance Date (YYYY-MM-DD): "),
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
