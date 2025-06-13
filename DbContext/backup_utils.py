import os
import zipfile
from datetime import datetime

BACKUP_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "backups")
DB_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data.db")

os.makedirs(BACKUP_DIR, exist_ok=True)

def create_backup():
    """Create a zip backup of the database file. Returns the backup file path."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_name = f"backup_{timestamp}.zip"
    backup_path = os.path.join(BACKUP_DIR, backup_name)
    with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        zipf.write(DB_FILE, arcname="data.db")
    return backup_path

def list_backups():
    """List all backup zip files."""
    return [f for f in os.listdir(BACKUP_DIR) if f.endswith('.zip')]

def restore_backup(backup_filename):
    """Restore the database from a given backup zip file."""
    backup_path = os.path.join(BACKUP_DIR, backup_filename)
    if not os.path.exists(backup_path):
        raise FileNotFoundError("Backup file not found.")
    with zipfile.ZipFile(backup_path, 'r') as zipf:
        zipf.extract("data.db", os.path.dirname(DB_FILE))
    return True
