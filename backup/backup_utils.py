import sqlite3
import os
from DbContext.crypto_utils import encrypt, decrypt
from DbContext.encrypted_logger import EncryptedLogger
from DbContext.backup_utils import create_backup, list_backups, restore_backup, delete_backup

DB_PATH = "data.db"

def add_restore_code(backup_name, system_admin, db_path=DB_PATH):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT backup_name, system_admin, used FROM backup_recovery_list")
    rows = cursor.fetchall()
    for enc_backup_name, enc_system_admin, used in rows:
        try:
            dec_backup_name = decrypt(enc_backup_name)
            dec_system_admin = decrypt(enc_system_admin)
        except Exception:
            continue
        if dec_backup_name == backup_name and dec_system_admin == system_admin and used == 0:
            conn.close()
            print(f"System Admin '{system_admin}' already has an active recovery code for backup '{backup_name}'.")
            return None
    import random, string
    def generate_restore_code(length=12):
        return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))
    code = generate_restore_code()
    enc_backup_name = encrypt(backup_name)
    enc_system_admin = encrypt(system_admin)
    enc_code = encrypt(code)
    cursor.execute("""
        INSERT INTO backup_recovery_list (backup_name, system_admin, recovery_code, used)
        VALUES (?, ?, ?, 0)
    """, (enc_backup_name, enc_system_admin, enc_code))
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
    cursor.execute("SELECT Username FROM User WHERE Role = 'systemadmin' AND IsActive = 1")
    admins = [decrypt(row[0]) for row in cursor.fetchall()]
    conn.close()
    return admins

def get_decrypted_backups():
    from DbContext.backup_utils import list_backups
    backups = list_backups()
    return backups
