from datetime import datetime
import sqlite3
import os
import uuid
from DbContext.crypto_utils import encrypt, decrypt
from DbContext.encrypted_logger import EncryptedLogger
from DbContext.backup_utils import create_backup, list_backups, restore_backup, delete_backup
import random, string


DB_PATH = "data.db"

def generate_restore_code(length=12):
    """Generate a random alphanumeric restore code."""
    try:
        return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))
    except Exception as e:
        EncryptedLogger().log_entry("system", "Generate Restore Code Failed", str(e), "Yes")
        raise

def add_restore_code(backup_name, system_admin, db_path=DB_PATH, option=""):
    conn = None
    cursor = None
    try:
        if option == "create":
            try:
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                cursor.execute("SELECT backup_name, system_admin, used FROM backup_recovery_list")
                rows = cursor.fetchall()
            except sqlite3.OperationalError as e:
                EncryptedLogger().error(f"Database operation failed while fetching backups: {e}")
                print("Error: Could not access the backup recovery list table.")
                return None
            except sqlite3.Error as e:
                EncryptedLogger().error(f"SQLite error occurred: {e}")
                print("A database error occurred.")
                return None

            for enc_backup_name, enc_system_admin, used in rows:
                try:
                    dec_backup_name = decrypt(enc_backup_name)
                    dec_system_admin = decrypt(enc_system_admin)
                    dec_used = decrypt(used)
                except ValueError as e:
                    EncryptedLogger().warning(f"Decryption failed for a record: {e}")
                    continue
                except Exception as e:
                    EncryptedLogger().error(f"Unexpected decryption error: {e}")
                    continue

                if dec_backup_name == backup_name and dec_system_admin == system_admin and dec_used == "0":
                    conn.close()
                    print(f"System Admin '{system_admin}' already has an active recovery code for backup '{backup_name}'.")
                    return None

            try:
                enc_backup_name = encrypt(backup_name)
                code = generate_restore_code()
                id = encrypt(generate_backup_id())
                enc_system_admin = encrypt(system_admin)
                enc_code = encrypt(code)
                enc_used = encrypt("0")
                enc_created_at = encrypt(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            except Exception as e:
                EncryptedLogger().error(f"Encryption failed while generating new restore code: {e}")
                print("Error: Could not encrypt restore code data.")
                return None

            try:
                cursor.execute("""
                    INSERT INTO backup_recovery_list (id, backup_name, system_admin, recovery_code, used, created_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (id, enc_backup_name, enc_system_admin, enc_code, enc_used, enc_created_at))
                conn.commit()
                conn.close()
            except sqlite3.IntegrityError as e:
                EncryptedLogger().error(f"Integrity error while inserting new restore code: {e}")
                print("Error: Duplicate or invalid data detected.")
                return None
            except sqlite3.Error as e:
                EncryptedLogger().error(f"Database insertion failed: {e}")
                print("Error: Could not save restore code to the database.")
                return None

            return code

        elif option == "adding":
            try:
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                cursor.execute("SELECT backup_name, system_admin, used FROM backup_recovery_list")
                rows = cursor.fetchall()
            except sqlite3.OperationalError as e:
                EncryptedLogger().error(f"Database operation failed while fetching backups: {e}")
                print("Error: Could not access the backup recovery list table.")
                return None
            except sqlite3.Error as e:
                EncryptedLogger().error(f"SQLite error occurred: {e}")
                print("A database error occurred.")
                return None

            for enc_backup_name, enc_system_admin, used in rows:
                try:
                    dec_backup_name = decrypt(enc_backup_name)
                    dec_system_admin = decrypt(enc_system_admin)
                    dec_used = decrypt(used)
                except ValueError as e:
                    EncryptedLogger().warning(f"Decryption failed for a record: {e}")
                    continue
                except Exception as e:
                    EncryptedLogger().error(f"Unexpected decryption error: {e}")
                    continue

                if dec_backup_name == backup_name and dec_system_admin == system_admin and dec_used == "0":
                    conn.close()
                    print(f"System Admin '{system_admin}' already has an active recovery code for backup '{backup_name}'.")
                    return None

            try:
                code = generate_restore_code()
                id = encrypt(generate_backup_id())
                enc_system_admin = encrypt(system_admin)
                enc_code = encrypt(code)
                enc_used = encrypt("0")
                enc_created_at = encrypt(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            except Exception as e:
                EncryptedLogger().error(f"Encryption failed while generating restore code: {e}")
                print("Error: Could not encrypt restore code data.")
                return None

            try:
                cursor.execute("""
                    INSERT INTO backup_recovery_list (id, backup_name, system_admin, recovery_code, used, created_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (id, backup_name, enc_system_admin, enc_code, enc_used, enc_created_at))
                conn.commit()
                conn.close()
            except sqlite3.IntegrityError as e:
                EncryptedLogger().error(f"Integrity error while inserting restore code: {e}")
                print("Error: Duplicate or invalid data detected.")
                return None
            except sqlite3.Error as e:
                EncryptedLogger().error(f"Database insertion failed: {e}")
                print("Error: Could not save restore code to the database.")
                return None

            return code

        else:
            print("Invalid option provided. Use 'create' or 'adding'.")
            EncryptedLogger().warning(f"Invalid option passed: {option}")
            return None

    except Exception as e:
        EncryptedLogger().critical(f"Unexpected error in add_restore_code: {e}")
        print("An unexpected error occurred while adding restore code.")
        return None

    finally:
        if cursor:
            try:
                cursor.close()
            except Exception as e:
                EncryptedLogger().warning(f"Failed to close cursor: {e}")
        if conn:
            try:
                conn.close()
            except Exception as e:
                EncryptedLogger().warning(f"Failed to close database connection: {e}")

def revoke_restore_code(backup_name, system_admin, db_path=DB_PATH):
    conn = None
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT id, backup_name, system_admin, used FROM backup_recovery_list")
        rows = cursor.fetchall()

        for row in rows:
            try:
                row_id, enc_backup_name, enc_system_admin, used = row
                if decrypt(used) == "0" and decrypt(enc_backup_name) == decrypt(backup_name) and decrypt(enc_system_admin) == decrypt(system_admin):
                    cursor.execute("""
                        UPDATE backup_recovery_list
                        SET used = ?, used_at = datetime('now')
                        WHERE id = ?
                    """, (encrypt("1"), row_id))
                    conn.commit()
                    EncryptedLogger().log_entry(system_admin, "Revoke Restore Code", f"Revoked code for {backup_name}", "No")
                    return True
            except Exception as inner_e:
                EncryptedLogger().log_entry(system_admin, "Decryption Error in revoke_restore_code", str(inner_e), "Yes")
                continue

        EncryptedLogger().log_entry(system_admin, "Revoke Restore Code Failed", "No matching active restore code found", "No")
        return False

    except (sqlite3.DatabaseError, sqlite3.OperationalError) as e:
        EncryptedLogger().log_entry(system_admin, "Revoke Restore Code Failed", f"Database Error: {str(e)}", "Yes")
        raise
    except Exception as e:
        EncryptedLogger().log_entry(system_admin, "Revoke Restore Code Failed", f"Unexpected Error: {str(e)}", "Yes")
        raise
    finally:
        if conn:
            conn.close()
            

def validate_restore_code(backup_name, system_admin, code, db_path=DB_PATH):
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT id, backup_name, system_admin, recovery_code, used FROM backup_recovery_list")
        rows = cursor.fetchall()
        for row in rows:
            try:
                row_id, enc_backup_name, enc_system_admin, enc_code, used = row
                decryptedused = decrypt(used)
                decrypted_code = decrypt(enc_code)
                decrypted_system_admin = decrypt(enc_system_admin)
                if (decryptedused == "0" and enc_backup_name == backup_name and
                    decrypted_system_admin == system_admin and decrypted_code == code):
                    # cursor.execute("""
                    #     UPDATE backup_recovery_list
                    #     SET used = ?, used_at = datetime('now')
                    #     WHERE id = ?
                    # """, (encrypt("1"), row_id))
                    # conn.commit()
                    conn.close()
                    return True
            except Exception as inner_e:
                EncryptedLogger().log_entry(system_admin, "Decryption Error in validate_restore_code", str(inner_e), "Yes")
                continue
    except (sqlite3.DatabaseError, sqlite3.OperationalError) as e:
        EncryptedLogger().log_entry(system_admin, "Validate Restore Code Failed", f"Database Error: {str(e)}", "Yes")
        raise
    except Exception as e:
        EncryptedLogger().log_entry(system_admin, "Validate Restore Code Failed", f"Unexpected Error: {str(e)}", "Yes")
        raise
    finally:
        if conn:
            conn.close()
    conn.close()
    return False

def get_system_admins(db_path=DB_PATH):
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM User ")
        rows = cursor.fetchall()
        admins = []
        for row in rows:
            try:
                username_enc = row[0]  
                role = row[6]
                is_active_enc = row[7]
                try:
                    username = decrypt(username_enc)
                    role = decrypt(role)
                    is_active = decrypt(is_active_enc)
                    
                except Exception:
                    continue
                # this needs to change after steph finishes the user role en is active will be encrypted
                if role == "systemadmin" and is_active == "1":
                    admins.append(username)
            except Exception as inner_e:
                    EncryptedLogger().log_entry("system", "Decryption Error in get_system_admins", str(inner_e), "Yes")
                    continue
    except (sqlite3.DatabaseError, sqlite3.OperationalError) as e:
        EncryptedLogger().log_entry("system", "Get System Admins Failed", f"Database Error: {str(e)}", "Yes")
        raise
    except Exception as e:
        EncryptedLogger().log_entry("system", "Get System Admins Failed", f"Unexpected Error: {str(e)}", "Yes")
        raise
    finally:
        if conn:
            conn.close()
    conn.close()
    return admins

def get_decrypted_backups():
    from DbContext.backup_utils import list_backups
    try:
        backups = list_backups()
        return backups
    except Exception as e:
        EncryptedLogger().log_entry("system", "Get Decrypted Backups Failed", str(e), "Yes")
        raise

def generate_backup_id():
        """Generate a random backup ID and ensure it does not collide."""
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            while True:
                candidate = uuid.uuid4().hex[:12].upper()
                cursor.execute(
                    "SELECT 1 FROM backup_recovery_list WHERE id = ?",
                    (candidate,),
                )
                if cursor.fetchone() is None:
                    return encrypt(candidate)
        except sqlite3.OperationalError as e:
            print(f"Operational Error: database or SQL issue. Contact Administrator.")
            logger = EncryptedLogger()
            logger.log_entry("System", "Operational Error on generating backup ID", f"{e}", "Yes")
            return None
        except sqlite3.ProgrammingError as e:
            print(f"Programming Error: database programming issue. Contact Administrator.")
            logger = EncryptedLogger()
            logger.log_entry("System", "Programming Error on generating backup ID", f"{e}", "Yes")
            return None
        except sqlite3.DatabaseError as e:
            print(f"Database Error: possible corruption or I/O issue. Contact Administrator.")
            logger = EncryptedLogger()
            logger.log_entry("System", "Database Error on generating backup ID", f"{e}", "Yes")
            return None
        except ValueError as e:
            print(f"Validation Error: {e}")
            logger = EncryptedLogger()
            logger.log_entry("System", "Validation Error on generating backup ID", f"{e}", "Yes")
            return None
        except Exception as e:
            print(f"Unexpected Exception occurred.")
            logger = EncryptedLogger()
            logger.log_entry("System", "Unexpected Error on generating backup ID", f"{e}", "Yes")
            return None