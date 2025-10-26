import os
import zipfile
from datetime import datetime
from DbContext.crypto_utils import decrypt, encrypt
from DbContext.encrypted_logger import EncryptedLogger
import sqlite3


BACKUP_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "backups")
DB_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data.db")

os.makedirs(BACKUP_DIR, exist_ok=True)

def create_backup(username=None):
    """Create a zip backup of the database file. Returns the backup file path."""
    logger = EncryptedLogger()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_name = f"backup_{timestamp}.zip"
    backup_path = os.path.join(BACKUP_DIR, backup_name)
    try:
        with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            zipf.write(DB_FILE, arcname="data.db")
        logger.log_entry(username or "system", "Create Backup", f"Backup created: {backup_name}", "No")

    except (FileNotFoundError, PermissionError, zipfile.BadZipFile) as e:
        logger.log_entry(username or "system", "Create Backup Failed", f"File/Zip Error: {str(e)}", "Yes")
        raise
    except Exception as e:
        logger.log_entry(username or "system", "Create Backup Failed", str(e), "Yes")
        raise

    return backup_path

def list_backups(username=None, option=""):
    """List all backup zip files."""
    logger = EncryptedLogger()
    conn = None
    cursor = None

    try:
        if username:
            # Fetch user specific backups if needed
            logger.log_entry(username, "List Backups", "Fetched user-specific backups", "No")
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            cursor.execute("SELECT backup_name, system_admin, used FROM backup_recovery_list")
            user_backups = cursor.fetchall()
            result = []
            for b in user_backups:
                if decrypt(b[1]) == username and decrypt(b[2]) == "0":  # used == 0
                    result.append(b[0])
            conn.close()
            return result

        if option == "revoke":
            logger.log_entry(username or "system", "List Backups for Revoke", "Fetched backups for revoke", "No")
            # Return only backups that have active recovery codes
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            cursor.execute("SELECT backup_name, system_admin FROM backup_recovery_list WHERE used_at IS NULL")
            active_backups = cursor.fetchall()
            conn.close()
            return active_backups
        # Return encrypted backup filenames

        backups = [f for f in os.listdir(BACKUP_DIR) if f.endswith('.zip')]
        return [encrypt(f) for f in backups]

    except (sqlite3.DatabaseError, sqlite3.OperationalError) as e:
        logger.log_entry(username or "system", "List Backups Failed", f"Database Error: {str(e)}", "Yes")
        raise
    except OSError as e:
        logger.log_entry(username or "system", "List Backups Failed", f"Filesystem Error: {str(e)}", "Yes")
        raise
    except Exception as e:
        logger.log_entry(username or "system", "List Backups Failed", f"Unexpected Error: {str(e)}", "Yes")
        raise
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


def restore_backup(backup_filename, username=None, system_admin=None):
    """Restore the database from a given backup zip file, preserving backup_recovery_list.
    If restore_code and system_admin are provided, mark the code as used before restoring."""
    logger = EncryptedLogger()

    try:
        decrypted_backup_name = decrypt(backup_filename)
    except Exception as e:
        logger.log_entry(username or "system", "Restore Backup Failed", f"Decryption failed: {str(e)}", "Yes")
        raise

    backup_path = os.path.join(BACKUP_DIR, decrypted_backup_name)
    if not os.path.exists(backup_path):
        logger.log_entry(username or "system", "Restore Backup Failed", f"Backup file not found: {decrypted_backup_name}", "Yes")
        raise FileNotFoundError("Backup file not found.")

    # Step 0: If restore_code and system_admin are provided, mark the code as used before restoring
    if system_admin:
        conn = None
        try:
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            cursor.execute("SELECT id, backup_name, system_admin, recovery_code, used FROM backup_recovery_list")
            rows = cursor.fetchall()

            for row in rows:
                if decrypt(row[1]) == decrypted_backup_name and decrypt(row[2]) == system_admin and decrypt(row[4]) == "0":
                    row_id = row[0]
                    cursor.execute("""
                        UPDATE backup_recovery_list
                        SET used = ?, used_at = datetime('now')
                        WHERE id = ?
                    """, (encrypt("1"), row_id))
                    conn.commit()
            conn.close()
            logger.log_entry(username or "system", "Mark restore code as used", f"Marked code as used for backup: {decrypted_backup_name}", "No")

        except (sqlite3.DatabaseError, sqlite3.OperationalError) as e:
            logger.log_entry(username or "system", "Mark restore code as used Failed", f"Database Error: {str(e)}", "Yes")
            raise
        except Exception as e:
            logger.log_entry(username or "system", "Mark restore code as used Failed", str(e), "Yes")
            raise
        finally:
            if conn:
                conn.close()

    # Step 1: Export backup_recovery_list
    recovery_rows = []
    conn = None
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM backup_recovery_list")
        recovery_rows = cursor.fetchall()
        cursor.execute("PRAGMA table_info(backup_recovery_list)")
        columns = [col[1] for col in cursor.fetchall()]
        conn.close()
    except (sqlite3.DatabaseError, sqlite3.OperationalError) as e:
        logger.log_entry(username or "system", "Export backup_recovery_list Failed", f"Database Error: {str(e)}", "Yes")
        raise
    except Exception as e:
        logger.log_entry(username or "system", "Export backup_recovery_list Failed", str(e), "Yes")
        raise
    finally:
        if conn:
            conn.close()

    # Step 2: Restore the backup (overwrite DB)
    try:
        with zipfile.ZipFile(backup_path, 'r') as zipf:
            zipf.extract("data.db", os.path.dirname(DB_FILE))
        logger.log_entry(username or "system", "Restore Backup", f"Restored from: {decrypted_backup_name}", "No")
    except (zipfile.BadZipFile, KeyError, PermissionError) as e:
        logger.log_entry(username or "system", "Restore Backup Failed", f"Zip/File Error: {str(e)}", "Yes")
        raise
    except Exception as e:
        logger.log_entry(username or "system", "Restore Backup Failed", str(e), "Yes")
        raise

    # Step 3: Re-insert backup_recovery_list rows
    conn = None
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        # Remove all rows in backup_recovery_list in the restored DB
        cursor.execute("DELETE FROM backup_recovery_list")
        # Insert the saved rows
        if recovery_rows:
            placeholders = ','.join(['?'] * len(columns))
            cursor.executemany(f"INSERT INTO backup_recovery_list ({', '.join(columns)}) VALUES ({placeholders})", recovery_rows)
        conn.commit()
        conn.close()
    except (sqlite3.DatabaseError, sqlite3.OperationalError) as e:
        logger.log_entry(username or "system", "Re-insert backup_recovery_list Failed", f"Database Error: {str(e)}", "Yes")
        raise
    except Exception as e:
        logger.log_entry(username or "system", "Re-insert backup_recovery_list Failed", str(e), "Yes")
        raise
    finally:
        if conn:
            conn.close()

    return True

def delete_backup(backup_filename, username=None):
    """Delete a backup zip file."""
    logger = EncryptedLogger()
    try:
        decrypted_backup_name = decrypt(backup_filename)
    except Exception as e:
        logger.log_entry(username or "system", "Delete Backup Failed", f"Decryption failed: {str(e)}", "Yes")
        raise

    backup_path = os.path.join(BACKUP_DIR, decrypted_backup_name)
    try:
        if os.path.exists(backup_path):
            delete_from_recovery_list(decrypted_backup_name)
            logger.log_entry(username or "system", "Delete from recovery list", f"Deleted recovery entry for every backup of: {decrypted_backup_name}", "No")
            os.remove(backup_path)
            logger.log_entry(username or "system", "Delete Backup", f"Deleted: {decrypted_backup_name}", "No")
        else:
            logger.log_entry(username or "system", "Delete Backup Failed", f"File not found: {decrypted_backup_name}", "Yes")
            raise FileNotFoundError("Backup file not found.")
    except (PermissionError, OSError) as e:
        logger.log_entry(username or "system", "Delete Backup Failed", f"Filesystem Error: {str(e)}", "Yes")
        raise
    except Exception as e:
        logger.log_entry(username or "system", "Delete Backup Failed", str(e), "Yes")
        raise


def delete_from_recovery_list(backup_name, db_path=DB_FILE):
    """Remove backup entries from recovery list table matching given name."""
    conn = None
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT id, backup_name FROM backup_recovery_list")
        rows = cursor.fetchall()
        for row in rows:
            try:
                row_id, enc_backup_name = row
                decrypted_backup_name = decrypt(enc_backup_name)
                if decrypted_backup_name == backup_name :
                        cursor.execute("DELETE FROM backup_recovery_list WHERE id = ?", (row_id,))
                        conn.commit()
            except Exception as inner_e:
                # Continue deleting other rows even if one fails
                EncryptedLogger().log_entry("system", "Delete From Recovery List Partial Fail", str(inner_e), "Yes")
    except (sqlite3.DatabaseError, sqlite3.OperationalError) as e:
        EncryptedLogger().log_entry("system", "Delete From Recovery List Failed", f"Database Error: {str(e)}", "Yes")
        raise
    except Exception as e:
        EncryptedLogger().log_entry("system", "Delete From Recovery List Failed", f"Unexpected Error: {str(e)}", "Yes")
        raise
    finally:
        if conn:
            conn.close()
