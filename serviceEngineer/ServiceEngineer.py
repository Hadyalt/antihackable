from DbContext.DbContext import DbContext
from DbContext.crypto_utils import encrypt, decrypt, hash_password, verify_password
import sqlite3
from DbContext.encrypted_logger import EncryptedLogger
from systemAdmin.system_admin import systemAdmin

class ServiceEngineer:
    def __init__(self):
        self.db_context = DbContext()
        self.sysAd = systemAdmin()

    def reset_password(self, username, password):
        try:
            user = self.sysAd.get_username(username)
            connection = self.db_context.connect()
            if connection:
                cursor = connection.cursor()
                hashed = hash_password(password)
                enc_username = user
                cursor.execute(
                    "UPDATE User SET Password = ? WHERE Username = ?",
                    (hashed, enc_username)
                )
                connection.commit()
            else:
                print("Failed to connect to the database.")

        ## --- Specific exceptions ---
        except sqlite3.OperationalError as e:
            print("Operational Error: database or SQL issue.")
            logger = EncryptedLogger()
            logger.log_entry("System", "Operational Error in reset_password_function", f"{e}", "Yes")
        except sqlite3.DatabaseError as e:
            print("Database Error: possible corruption or I/O issue.")
            logger = EncryptedLogger()
            logger.log_entry("System", "Database Error in reset_password_function", f"{e}", "Yes")
        except sqlite3.InterfaceError as e:
            print("Interface Error: invalid SQL parameters.")
            logger = EncryptedLogger()
            logger.log_entry("System", "Interface Error in reset_password_function", f"{e}", "Yes")
        except Exception as e:
            print("Unexpected error occurred while resetting password.")
            logger = EncryptedLogger()
            logger.log_entry("System", "Unexpected Error in reset_password_function7", f"{e}", "Yes")
    
    def check_reset_password(self, username):
        try:
            connection = self.db_context.connect()
            if connection:
                cursor = connection.cursor()
                enc_username = encrypt(username)
                cursor.execute(
                    "SELECT ResettedPasswordCheck FROM User WHERE Username = ?",
                    (enc_username, )
                )
                result = cursor.fetchone()
                if result:
                    return decrypt(result[0]) == "1"
                else:
                    print("No user found with the given username.")
                    return False
            else:
                print("Failed to connect to the database.")
                return False
        ## --- Specific exceptions ---
        except sqlite3.OperationalError as e:
            print("Operational Error: database or SQL issue.")
            logger = EncryptedLogger()
            logger.log_entry("System", "Operational Error in reset_password_function", f"{e}", "Yes")
        except sqlite3.DatabaseError as e:
            print("Database Error: possible corruption or I/O issue.")
            logger = EncryptedLogger()
            logger.log_entry("System", "Database Error in reset_password_function", f"{e}", "Yes")
        except sqlite3.InterfaceError as e:
            print("Interface Error: invalid SQL parameters.")
            logger = EncryptedLogger()
            logger.log_entry("System", "Interface Error in reset_password_function", f"{e}", "Yes")
        except Exception as e:
            print("Unexpected error occurred while resetting password.")
            logger = EncryptedLogger()
            logger.log_entry("System", "Unexpected Error in reset_password_function6", f"{e}", "Yes")
    
    def reset_resetted_password_check(self, username):
        try:
            connection = self.db_context.connect()
            if connection:
                cursor = connection.cursor()
                enc_username = encrypt(username)
                cursor.execute(
                    "UPDATE User SET ResettedPasswordCheck = ? WHERE Username = ?",
                    (encrypt("0"), enc_username)
                )
                connection.commit()
            else:
                print("Failed to connect to the database.")
    
        ## --- Specific exceptions ---
        except sqlite3.OperationalError as e:
            print("Operational Error: database or SQL issue.")
            logger = EncryptedLogger()
            logger.log_entry("System", "Operational Error in reset_password_function", f"{e}", "Yes")
        except sqlite3.DatabaseError as e:
            print("Database Error: possible corruption or I/O issue.")
            logger = EncryptedLogger()
            logger.log_entry("System", "Database Error in reset_password_function", f"{e}", "Yes")
        except sqlite3.InterfaceError as e:
            print("Interface Error: invalid SQL parameters.")
            logger = EncryptedLogger()
            logger.log_entry("System", "Interface Error in reset_password_function", f"{e}", "Yes")
        except Exception as e:
            print("Unexpected error occurred while resetting password.")
            logger = EncryptedLogger()
            logger.log_entry("System", "Unexpected Error in reset_password_function5", f"{e}", "Yes")