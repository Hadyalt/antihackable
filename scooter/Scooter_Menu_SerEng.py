from datetime import datetime
from DbContext.encrypted_logger import EncryptedLogger
from scooter.Scooter import print_scooter_table
from scooter.Scooter_data import Scooter_data
from validation.isValidMaintenanceDate import is_valid_maintenance_date
from validation.isValidMileage import is_valid_mileage
from validation.isValidSerialNumber import is_valid_serial_number
from validation.isValidStateOfCharge import is_valid_state_of_charge
from validation.isValidTargetRangeSoc import is_valid_target_range_soc


def Scooter_Menu_SerEng(choice, updater):
    db = Scooter_data()
    db.connect()
    if choice == "1":  # View Scooters
        search_term = input("Enter search term (leave blank for all): ")
        if search_term:
            scooters = db.search_scooters(search_term)
        else:
            scooters = db.get_all_scooters()
        if scooters:
            print_scooter_table(scooters)
        else:
            print("No matching scooters found")

    elif choice == "2":
        update_scooter_SerEng(updater)
        
    elif choice == "3":
        return
    
    else:
        print("Invalid choice.")

def update_scooter_SerEng(updater):
    db = Scooter_data()
    logger = EncryptedLogger()
    db.connect()

    print("\nList of Scooters:")
    scooters = db.get_all_serial_numbers()
    if not scooters:
        print("No scooters available to update.")
        return
    for s in scooters:
        print(f"- {s[0]}")
    
    sn = input("\nSerial Number to update: ")
    if is_valid_serial_number(sn):
        # Fetch existing scooter data
        scooter = db.get_scooter_by_serial(sn)
        if not scooter:
            print("Scooter not found!")
            return
    else:
        print("Invalid serial number format")
        return

    print("\n[1] State of Charge")
    print("[2] Target Range SoC")
    print("[3] Location")
    print("[4] Out-of-service Status")
    print("[5] Mileage")
    print("[6] Last Maintenance Date")
    print("[7] Cancel Update")

    field_choice = input("\nChoose field to update: ")
    MAX_TRIES = 3
    
    if field_choice == "1":  # State of Charge
        tries = 0
        while tries < MAX_TRIES:
            new_value = input("New State of Charge (%): ")
            if new_value and is_valid_state_of_charge(new_value):
                db.update_scooter_fields(sn, StateOfCharge=new_value)
                logger.log_entry(f"{updater}", f"Updated scooter {sn}", f"Updated the State of Charge to {new_value}", "No")
                return
            else:
                print("Invalid State of Charge: Must be between 0% and 100%")
            tries += 1
            print(f"You have {MAX_TRIES - tries} attempts left")
        print("Too many invalid attempts. Update cancelled.")
        logger.log_entry(f"{updater}", f"Update cancelled for scooter {sn}", "Too many invalid SoC attempts", "Yes")

    elif field_choice == "2":  # Target Range SOC
        tries = 0
        while tries < MAX_TRIES:
            min_val = float(input("New Min SoC (%): "))
            max_val = float(input("New Max SoC (%): "))
            if is_valid_target_range_soc(min_val, max_val):
                db.update_scooter_fields(sn, TargetRangeSocMin=min_val, TargetRangeSocMax=max_val)
                logger.log_entry(f"{updater}", f"Updated scooter {sn}", f"Updated the target range SOC to {min_val} - {max_val}", "No")
                return
            else:
                print("Invalid Target Range SOC: Min must be ≤ Max (both 0-100%)")
            tries += 1
            print(f"You have {MAX_TRIES - tries} attempts left")
        print("Too many invalid attempts. Update cancelled.")
        logger.log_entry(f"{updater}", f"Update cancelled for scooter {sn}", "Too many invalid target SoC attempts", "Yes")

    elif field_choice == "3":  # Location
        ROTTERDAM_BOUNDS = {
            "min_lat": 51.85,
            "max_lat": 52.0,
            "min_lon": 4.3,
            "max_lon": 4.6,
        }
        tries = 0
        while tries < MAX_TRIES:
            try:
                lat = round(float(input("New Latitude (51.85-52.00): ")), 5)
                lon = round(float(input("New Longitude (4.30-4.60): ")), 5)
                if ROTTERDAM_BOUNDS["min_lat"] <= lat <= ROTTERDAM_BOUNDS["max_lat"] and ROTTERDAM_BOUNDS["min_lon"] <= lon <= ROTTERDAM_BOUNDS["max_lon"]:
                    db.update_scooter_fields(sn, LocationLat=lat, LocationLong=lon)
                    logger.log_entry(f"{updater}", f"Updated scooter {sn}", f"Updated the location to ({lat}, {lon})", "No")
                    return
                print("Error: Must be within Rotterdam (Lat: 51.85–52.00, Lon: 4.30–4.60)")
            except ValueError:
                print("Error: Invalid coordinate format")
            tries += 1
            print(f"You have {MAX_TRIES - tries} attempts left")
        print("Too many invalid attempts. Update cancelled.")
        logger.log_entry(f"{updater}", f"Update cancelled for scooter {sn}", "Too many invalid location attempts", "Yes")

    elif field_choice == "4":  # Out-of-Service
        tries = 0
        while tries < MAX_TRIES:
            oos_input = input("Out of Service? (y/n): ")
            if oos_input in ("y", "n"):
                oos = oos_input == "y"
                db.update_scooter_fields(sn, OutOfService=int(oos))
                logger.log_entry(f"{updater}", f"Updated scooter {sn}", f"Updated out of service to {oos_input}", "No")
                return
            print("Error: Enter 'y' or 'n'")
            tries += 1
            print(f"You have {MAX_TRIES - tries} attempts left")
        print("Too many invalid attempts. Update cancelled.")
        logger.log_entry(f"{updater}", f"Update cancelled for scooter {sn}", "Too many invalid out-of-service attempts", "Yes")

    elif field_choice == "5":  # Mileage
        tries = 0
        while tries < MAX_TRIES:
            new_mileage = input("New Mileage (km): ")
            if new_mileage and is_valid_mileage(new_mileage):
                db.update_scooter_fields(sn, Mileage=new_mileage)
                logger.log_entry(f"{updater}", f"Updated scooter {sn}", f"Updated the mileage to {new_mileage}", "No")
                return
            else:
                print("Invalid Mileage: Cannot be negative")
            tries += 1
            print(f"You have {MAX_TRIES - tries} attempts left")
        print("Too many invalid attempts. Update cancelled.")
        logger.log_entry(f"{updater}", f"Update cancelled for scooter {sn}", "Too many invalid mileage attempts", "Yes")

    elif field_choice == "6":  # Last Maintenance Date
        tries = 0
        while tries < MAX_TRIES:
            new_maintenance_date = input("New Last Maintenance Date (YYYY-MM-DD): ")
            if new_maintenance_date and is_valid_maintenance_date(new_maintenance_date):
                db.update_scooter_fields(sn, LastMaintenanceDate=new_maintenance_date)
                logger.log_entry(f"{updater}", f"Updated scooter {sn}", f"Updated the last maintenance date to {new_maintenance_date}", "No")
                return
            else:
                print("Invalid Date: Use YYYY-MM-DD format, not older than 1980, not in the future")
            tries += 1
            print(f"You have {MAX_TRIES - tries} attempts left")
        print("Too many invalid attempts. Update cancelled.")
        logger.log_entry(f"{updater}", f"Update cancelled for scooter {sn}", "Too many invalid maintenance date attempts", "Yes")
    
    elif field_choice == "7":
        print("Update cancelled")
        return

    else:
        print("Invalid choice.")