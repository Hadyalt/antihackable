from DbContext.DbContext import DbContext
from Login.verification import Verification


class systemAdmin:
    def __init__(self):
        self.db_context = DbContext()
    
    def create_service_engineer(self):
        verified_username = False
        while not verified_username:
            user_name = input("Enter username: ")
            verified_username = Verification.verify_username(user_name)
        verified_password = False
        while not verified_password:
            password = input("Enter password: ")
            verified_password = Verification.verify_Password(password)
        hashed_password = Verification.hash_password(password)
        system_data = {
            "Username": user_name,
            "Password": hashed_password,
            "Role": "serviceengineer",
            "IsActive": 1
        }
        self.db_context.insert_User(system_data)
        return user_name
    
    def view_all_users(self):
        connection = self.db_context.connect()
        if connection:
            cursor = connection.cursor()
            cursor.execute("SELECT Username, Role FROM User WHERE IsActive = 1")
            users = cursor.fetchall()
            if users:
                print("\nAll User Accounts:")
                for user in users:
                    print(f"Username: {user[0]}, Role: {user[1]}")
            else:
                print("No user accounts found.")
            connection.close()
        else:
            print("No database connection.")
        return
    
    def view_all_service_engineers(self):
        connection = self.db_context.connect()
        if connection:
            cursor = connection.cursor()
            cursor.execute("SELECT Username FROM User WHERE Role = ? AND IsActive = 1", ("serviceengineer",))
            users = cursor.fetchall()
            
            if users:
                print(f"Retrieved {len(users)} service engineer(s):")
                for user in users:
                    print(f"- {user[0]}")
                return users
            else:
                print("No service engineer accounts found.")
                return []
        else:
            print("No database connection.")
            return "Error"
        
    def update_service_engineer(self):
        servEng = self.view_all_service_engineers()
        if not servEng:
            print("No service engineers available to update.")
            return
        username_to_update = input("Enter the username of the service engineer you want to update: ").strip()

        # Check if the username exists in the servEng list
        matching_users = [user for user in servEng if user[0].lower() == username_to_update.lower()]
        if not matching_users:
            print(f"No service engineer found with username '{username_to_update}'.")
            return
        print ("What do you want to update?")
        print(f"1. Username: ({username_to_update})")
        print(f"2. Password")
        choice = input("Enter your choice (1 or 2): ").strip()
        if choice == "1":
            new_username = input("Enter the new username: ").strip()
            if Verification.verify_username(new_username):
                self.set_new_username(username_to_update, new_username)
                print(f"Service Engineer {username_to_update} updated to {new_username}.")
            else:
                print("Invalid username format. Please try again.")
        elif choice == "2":
            new_password = input("Enter the new password: ").strip()
            if Verification.verify_Password(new_password):
                hashed_password = Verification.hash_password(new_password)
                self.reset_password(username_to_update, hashed_password)
                print(f"Password for service engineer {username_to_update} has been updated to {new_password}.")
            else:
                print("Invalid password format. Please try again.")
        else:
            print("Invalid choice. Please try again.")
    
    def delete_service_engineer(self): #Delete by setting IsActive to 0
        servEng = self.view_all_service_engineers()
        if not servEng:
            print("No service engineers available to delete.")
            return
        username_to_delete = input("Enter the username of the service engineer you want to delete: ").strip()

        # Check if the username exists in the servEng list
        matching_users = [user for user in servEng if user[0].lower() == username_to_delete.lower()]  # assumes username is in column 0

        if not matching_users:
            print(f"No service engineer found with username '{username_to_delete}'.")
            return

        connection = self.db_context.connect()
        if connection:
            cursor = connection.cursor()
            cursor.execute("UPDATE User SET IsActive = 0 WHERE LOWER(Username) = LOWER(?) AND Role = ?", (username_to_delete, "serviceengineer"))
            connection.commit()
            print(f"service engineer '{username_to_delete}' has been deleted.")
        else:
            print("Failed to connect to the database.")
    
    # def delete_service_engineer(self): #Delete by removing the record
    #     servEng = self.view_all_service_engineers()
    #     if not servEng:
    #         print("No service engineers available to delete.")
    #         return
    #     username_to_delete = input("Enter the username of the service engineer you want to delete: ").strip()

    #     # Check if the username exists in the servEng list
    #     matching_users = [user for user in servEng if user[0].lower() == username_to_delete.lower()]  # assumes username is in column 0

    #     if not matching_users:
    #         print(f"No service engineer found with username '{username_to_delete}'.")
    #         return

    #     connection = self.db_context.connect()
    #     if connection:
    #         cursor = connection.cursor()
    #         cursor.execute("UPDATE User SET IsActive = 0 WHERE LOWER(Username) = LOWER(?) AND Role = ?", (username_to_delete, "serviceengineer"))
    #         connection.commit()
    #         print(f"service engineer '{username_to_delete}' has been deleted.")
    #     else:
    #         print("Failed to connect to the database.")
    
    def delete_account(self, username): #Delete by setting IsActive to 0
        connection = self.db_context.connect()
        if connection:
            cursor = connection.cursor()
            cursor.execute("UPDATE User SET IsActive = 0 WHERE LOWER(Username) = LOWER(?) AND Role = ?", (username, "systemadmin"))
            connection.commit()
            return True
        else:
            print("Failed to connect to the database.")
            return False
    
    # def delete_account(self, username): #Delete by removing the record
    #     connection = self.db_context.connect()
    #     if connection:
    #         cursor = connection.cursor()
    #         cursor.execute("DELETE User WHERE LOWER(Username) = LOWER(?) AND Role = ?", (username, "systemadmin"))
    #         connection.commit()
    #         return True
    #     else:
    #         print("Failed to connect to the database.")
    #         return False

    def set_new_username(self, old_username, new_username):
        connection = self.db_context.connect()
        if connection:
            cursor = connection.cursor()
            cursor.execute("UPDATE User SET Username = ? WHERE LOWER(Username) = LOWER(?) AND Role = ?", (new_username, old_username, "serviceengineer"))
            connection.commit()
            return True
        else:
            print("Failed to connect to the database.")
            return False
    
    def set_new_username_system(self, old_username, new_username):
        connection = self.db_context.connect()
        if connection:
            cursor = connection.cursor()
            cursor.execute("UPDATE User SET Username = ? WHERE LOWER(Username) = LOWER(?) AND Role = ?", (new_username, old_username, "systemadmin"))
            connection.commit()
            return True
        else:
            print("Failed to connect to the database.")
            return False
    
    def reset_password(self, username, new_password):
        connection = self.db_context.connect()
        if connection:
            cursor = connection.cursor()
            cursor.execute("UPDATE User SET Password = ? WHERE LOWER(Username) = LOWER(?) AND Role = ?", (new_password, username, "serviceengineer"))
            connection.commit()
            return True
        else:
            print("Failed to connect to the database.")
            return False
    
    def reset_password_system(self, username, new_password):
        connection = self.db_context.connect()
        if connection:
            cursor = connection.cursor()
            cursor.execute("UPDATE User SET Password = ? WHERE LOWER(Username) = LOWER(?) AND Role = ?", (new_password, username, "systemadmin"))
            connection.commit()
            return True
        else:
            print("Failed to connect to the database.")
            return False