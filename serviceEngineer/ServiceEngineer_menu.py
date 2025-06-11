from serviceEngineer.ServiceEngineer import ServiceEngineer
import getpass

def display_menu():
    print("\n==== Service Engineer Menu ====")
    print("1. Update Scooter Info")
    print("2. Manage Travellers")
    print("3. Change My Password")
    print("4. Exit")
    return input("Enter your choice (1-4): ").strip()

def main(username):
    # Get logged-in service engineer's username (from session/auth system)
    current_user = username # Replace with actual logged-in username
    
    engineer = ServiceEngineer()
    
    while True:
        choice = display_menu()
        
        if choice == '1':
            print("\n** Password Reset **")
            new_password = getpass.getpass("Enter new password: ")
            confirm_password = getpass.getpass("Confirm new password: ")
            
            if new_password != confirm_password:
                print("Error: Passwords do not match!")
                continue
                
            engineer.reset_password(current_user, new_password)
            print("Password reset completed. Check system messages for status.")
            
        elif choice == '2':
            print("Exiting Service Engineer Portal. Goodbye!")
            break
            
        else:
            print("Invalid selection. Please choose 1 or 2.")

if __name__ == "__main__":
    main()