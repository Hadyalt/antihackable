from DbContext.DbContext import DbContext
from models.Scooter import Scooter


def show_menu():
    print("""
[1] Add Scooter
[2] View Scooters
[3] Update Scooter State of Charge
[4] Delete Scooter
[5] Exit
""")


def main():
    db = DbContext()
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
            new_soc = float(input("New State of Charge (%): "))
            db.update_scooter_state(sn, new_soc)

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
