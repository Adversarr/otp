import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

def derive_key(password: str, salt: bytes) -> bytes:
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=480000,
    )
    return base64.urlsafe_b64encode(kdf.derive(password.encode()))

def encrypt_data(data: str, password: str) -> str:
    salt = b'salt_'  # 实际项目中应使用随机salt
    key = derive_key(password, salt)
    f = Fernet(key)
    return f.encrypt(data.encode()).decode()

def decrypt_data(token: str, password: str) -> str:
    salt = b'salt_'
    key = derive_key(password, salt)
    f = Fernet(key)
    return f.decrypt(token.encode()).decode()
