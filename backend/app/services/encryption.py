from cryptography.fernet import Fernet, InvalidToken

from app.core.config import settings


def _get_cipher() -> Fernet:
    try:
        key = settings.ENCRYPTION_KEY.encode("utf-8")
        if len(key) != 44:
            raise ValueError("Encryption key must be 44 characters (base64-encoded 32 bytes)")
        return Fernet(key)
    except Exception as e:
        raise RuntimeError(f"Invalid encryption key: {type(e).__name__}: {str(e)}")


def encrypt_token(plaintext: str) -> str:
    cipher = _get_cipher()
    ciphertext = cipher.encrypt(plaintext.encode("utf-8"))
    return ciphertext.decode("utf-8")


def decrypt_token(ciphertext: str) -> str:
    cipher = _get_cipher()
    try:
        plaintext = cipher.decrypt(ciphertext.encode("utf-8"))
        return plaintext.decode("utf-8")
    except InvalidToken:
        raise ValueError("Failed to decrypt token")
