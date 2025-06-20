from cryptography.fernet import Fernet
import base64
import os
import hashlib


# You should generate and store this key securely. For demo, we use a static key file.
KEY_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'secret.key')

def generate_key():
    key = Fernet.generate_key()
    with open(KEY_FILE, 'wb') as key_file:
        key_file.write(key)
    return key

def load_key():
    if not os.path.exists(KEY_FILE):
        return generate_key()
    with open(KEY_FILE, 'rb') as key_file:
        return key_file.read()

fernet = Fernet(load_key())

def encrypt(plaintext: str) -> str:
    if plaintext is None:
        return None
    return fernet.encrypt(plaintext.encode()).decode()

def decrypt(ciphertext: str) -> str:
    if ciphertext is None:
        return None
    return fernet.decrypt(ciphertext.encode()).decode()


def hash_password(password: str, salt: bytes = None) -> str:
    if salt is None:
        salt = os.urandom(16)
    pwd_hash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100000)
    return base64.b64encode(salt + pwd_hash).decode()

def verify_password(password: str, hashed: str) -> bool:
    decoded = base64.b64decode(hashed.encode())
    salt = decoded[:16]
    stored_hash = decoded[16:]
    pwd_hash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100000)
    return pwd_hash == stored_hash
