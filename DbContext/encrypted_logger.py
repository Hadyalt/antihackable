from cryptography.fernet import Fernet
from datetime import datetime
import os

# Use the same key file as in crypto_utils.py for consistency
KEY_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'secret.key')


def load_key():
    if not os.path.exists(KEY_FILE):
        raise FileNotFoundError("Encryption key file not found. Please generate it using crypto_utils.py.")
    with open(KEY_FILE, 'rb') as key_file:
        return key_file.read()

fernet = Fernet(load_key())

class EncryptedLogger:
    def __init__(self, logfile_path="logs.txt"):
        self.logfile_path = logfile_path

    def _get_next_no(self):
        if not os.path.exists(self.logfile_path):
            return 1
        with open(self.logfile_path, "r") as f:
            return sum(1 for _ in f) + 1

    def log_entry(self, username, activity, additional_info="", suspicious="No", status="new"):
        now = datetime.now()
        no = self._get_next_no()
        entry = f"{no}|{now.strftime('%d-%m-%Y')}|{now.strftime('%H:%M:%S')}|{username}|{activity}|{additional_info}|{suspicious}|{status}"
        encrypted = fernet.encrypt(entry.encode()).decode()
        with open(self.logfile_path, "a") as f:
            f.write(encrypted + "\n")

    def read_logs(self, table_format=True):
        if not os.path.exists(self.logfile_path):
            print("No log file found.")
            return
        rows = []
        with open(self.logfile_path, "r") as f:
            for line in f:
                decrypted = fernet.decrypt(line.strip().encode()).decode()
                parts = decrypted.split("|")
                rows.append(parts)
        if table_format:
            self._print_table(rows)
        else:
            for row in rows:
                print("|".join(row))

    def _print_table(self, rows):
        headers = ["No.", "Date", "Time", "Username", "Description of activity", "Additional Information", "Suspicious", "Status"]
        col_widths = [max(len(str(row[i])) for row in ([headers] + rows)) for i in range(len(headers))]
        def fmt_row(row):
            return " | ".join(str(row[i]).ljust(col_widths[i]) for i in range(len(headers)))
        print(fmt_row(headers))
        print("-+-".join("-" * w for w in col_widths))
        for row in rows:
            print(fmt_row(row))


