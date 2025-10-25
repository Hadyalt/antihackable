import sqlite3
import os
import uuid
from DbContext.crypto_utils import encrypt, decrypt
from DbContext.encrypted_logger import EncryptedLogger
from DbContext.backup_utils import create_backup, list_backups, restore_backup, delete_backup
import random, string

DB_PATH = "data.db"
def generate_restore_code(length=12):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))
def add_restore_code(backup_name, system_admin, db_path=DB_PATH):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT backup_name, system_admin, used FROM backup_recovery_list")
    rows = cursor.fetchall()
    for enc_backup_name, enc_system_admin, used in rows:
        try:
            dec_backup_name = decrypt(enc_backup_name)
            dec_system_admin = decrypt(enc_system_admin)
            dec_used = decrypt(used)
        except Exception:
            continue
        if dec_backup_name == backup_name and dec_system_admin == system_admin and dec_used == "0":
            conn.close()
            print(f"System Admin '{system_admin}' already has an active recovery code for backup '{backup_name}'.")
            return None
    
    code = generate_restore_code()
    id = encrypt(generate_backup_id())
    enc_backup_name = encrypt(backup_name)
    enc_system_admin = encrypt(system_admin)
    enc_code = encrypt(code)
    enc_used = encrypt("0")
    cursor.execute("""
        INSERT INTO backup_recovery_list (id, backup_name, system_admin, recovery_code, used)
        VALUES (?, ?, ?, ?, ?)
    """, (id, enc_backup_name, enc_system_admin, enc_code, enc_used))
    conn.commit()
    conn.close()
    return code

def revoke_restore_code(backup_name, system_admin, db_path=DB_PATH):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT id, backup_name, system_admin, used FROM backup_recovery_list")
    rows = cursor.fetchall()
    for row in rows:
        row_id, enc_backup_name, enc_system_admin, used = row
        if used == 0 and decrypt(enc_backup_name) == backup_name and decrypt(enc_system_admin) == system_admin:
            cursor.execute("""
                UPDATE backup_recovery_list
                SET used = 1, used_at = datetime('now')
                WHERE id = ?
            """, (row_id,))
            conn.commit()
            conn.close()
            return True
    conn.close()
    return False

def validate_restore_code(backup_name, system_admin, code, db_path=DB_PATH):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT id, backup_name, system_admin, recovery_code, used FROM backup_recovery_list")
    rows = cursor.fetchall()
    for row in rows:
        row_id, enc_backup_name, enc_system_admin, enc_code, used = row
        if (used == 0 and decrypt(enc_backup_name) == backup_name and
            decrypt(enc_system_admin) == system_admin and decrypt(enc_code) == code):
            cursor.execute("""
                UPDATE backup_recovery_list
                SET used = 1, used_at = datetime('now')
                WHERE id = ?
            """, (row_id,))
            conn.commit()
            conn.close()
            return True
    conn.close()
    return False

def get_system_admins(db_path=DB_PATH):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM User ")
    rows = cursor.fetchall()
    admins = []
    for row in rows:
        username_enc = row[0]  
        role = row[6]
        is_active_enc = row[7]
        try:
            username = decrypt(username_enc)
            # role = decrypt(role)
            # is_active = decrypt(is_active_enc)
            
        except Exception:
            continue
        # this needs to change after steph finishes the user role en is active will be encrypted
        if role == "systemadmin" and is_active_enc == 1:
            admins.append(username)
    conn.close()
    return admins

def get_decrypted_backups():
    from DbContext.backup_utils import list_backups
    backups = list_backups()
    return backups

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