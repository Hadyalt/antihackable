import os
import zipfile
from datetime import datetime
from DbContext.encrypted_logger import EncryptedLogger

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
    except Exception as e:
        logger.log_entry(username or "system", "Create Backup Failed", str(e), "Yes")
        raise
    return backup_path

def list_backups():
    """List all backup zip files."""
    return [f for f in os.listdir(BACKUP_DIR) if f.endswith('.zip')]

def restore_backup(backup_filename, username=None):
    """Restore the database from a given backup zip file, preserving backup_recovery_list."""
    import sqlite3
    logger = EncryptedLogger()
    backup_path = os.path.join(BACKUP_DIR, backup_filename)
    if not os.path.exists(backup_path):
        logger.log_entry(username or "system", "Restore Backup Failed", f"Backup file not found: {backup_filename}", "Yes")
        raise FileNotFoundError("Backup file not found.")
    # Step 1: Export backup_recovery_list
    recovery_rows = []
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM backup_recovery_list")
        recovery_rows = cursor.fetchall()
        cursor.execute("PRAGMA table_info(backup_recovery_list)")
        columns = [col[1] for col in cursor.fetchall()]
        conn.close()
    except Exception as e:
        logger.log_entry(username or "system", "Export backup_recovery_list Failed", str(e), "Yes")
        raise
    # Step 2: Restore the backup (overwrite DB)
    try:
        with zipfile.ZipFile(backup_path, 'r') as zipf:
            zipf.extract("data.db", os.path.dirname(DB_FILE))
        logger.log_entry(username or "system", "Restore Backup", f"Restored from: {backup_filename}", "No")
    except Exception as e:
        logger.log_entry(username or "system", "Restore Backup Failed", str(e), "Yes")
        raise
    # Step 3: Re-insert backup_recovery_list rows
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
    except Exception as e:
        logger.log_entry(username or "system", "Re-insert backup_recovery_list Failed", str(e), "Yes")
        raise
    return True

def delete_backup(backup_filename, username=None):
    """Delete a backup zip file."""
    logger = EncryptedLogger()
    backup_path = os.path.join(BACKUP_DIR, backup_filename)
    try:
        if os.path.exists(backup_path):
            os.remove(backup_path)
            logger.log_entry(username or "system", "Delete Backup", f"Deleted: {backup_filename}", "No")
        else:
            logger.log_entry(username or "system", "Delete Backup Failed", f"File not found: {backup_filename}", "Yes")
            raise FileNotFoundError("Backup file not found.")
    except Exception as e:
        logger.log_entry(username or "system", "Delete Backup Failed", str(e), "Yes")
        raise
    return True
