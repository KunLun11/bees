import hashlib
import secrets
import base64
import logging

logger = logging.getLogger(__name__)


def hash_password(password: str) -> str:
    try:
        if not password:
            raise ValueError("Password cannot be empty")
        salt = secrets.token_hex(16)
        hashed = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            salt.encode("utf-8"),
            100000,  
        )
        hashed_b64 = base64.b64encode(hashed).decode("utf-8")
        return f"{salt}${hashed_b64}"

    except Exception as e:
        logger.error(f"Error in hash_password: {str(e)}")
        raise ValueError(f"Password hashing error: {str(e)}")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        if not hashed_password or "$" not in hashed_password:
            return False
        salt, stored_hash = hashed_password.split("$", 1)
        hashed = hashlib.pbkdf2_hmac(
            "sha256", plain_password.encode("utf-8"), salt.encode("utf-8"), 100000
        )
        hashed_b64 = base64.b64encode(hashed).decode("utf-8")
        return secrets.compare_digest(hashed_b64, stored_hash)

    except Exception as e:
        logger.error(f"Error in verify_password: {str(e)}")
        return False
