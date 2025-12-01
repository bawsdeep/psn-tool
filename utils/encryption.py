"""Encryption utilities for sensitive data like NPSSO tokens."""

import base64
import hashlib
import logging
import os
import platform
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from pathlib import Path

logger = logging.getLogger(__name__)


def get_encryption_key_path() -> Path:
    """Get the path to store the encryption key."""
    from utils.database import get_app_data_dir
    return get_app_data_dir() / ".encryption_key"


def derive_key_from_system() -> bytes:
    """Derive an encryption key from system-specific information.
    
    This creates a key that's unique to the user's system but doesn't
    require a password. The key is stored locally and reused.
    """
    key_path = get_encryption_key_path()
    
    # If key exists, load it
    if key_path.exists():
        try:
            with open(key_path, 'rb') as f:
                return f.read()
        except Exception as e:
            logger.warning(f"Failed to load encryption key: {e}, generating new one")
    
    # Generate a new key based on system information
    # Combine multiple system identifiers for uniqueness
    system_info = []
    
    # Username
    system_info.append(os.getenv('USER', os.getenv('USERNAME', 'default')))
    
    # Home directory path
    system_info.append(str(Path.home()))
    
    # Platform info
    system_info.append(platform.system())
    system_info.append(platform.machine())
    
    # Combine and hash
    combined = '|'.join(system_info).encode('utf-8')
    salt = hashlib.sha256(combined).digest()[:16]
    
    # Use PBKDF2 to derive a key
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
    )
    key_material = combined
    key = base64.urlsafe_b64encode(kdf.derive(key_material))
    
    # Store the key for future use
    try:
        key_path.parent.mkdir(parents=True, exist_ok=True)
        # Set restrictive permissions (owner read/write only)
        with open(key_path, 'wb') as f:
            f.write(key)
        if platform.system() != 'Windows':
            os.chmod(key_path, 0o600)  # rw------- on Unix
    except Exception as e:
        logger.warning(f"Failed to save encryption key: {e}")
    
    return key


def get_cipher() -> Fernet:
    """Get a Fernet cipher instance for encryption/decryption."""
    key = derive_key_from_system()
    return Fernet(key)


def encrypt_token(token: str) -> str:
    """Encrypt a token for storage.
    
    Args:
        token: Plain text token to encrypt
        
    Returns:
        Base64-encoded encrypted token
    """
    try:
        cipher = get_cipher()
        encrypted = cipher.encrypt(token.encode('utf-8'))
        return base64.urlsafe_b64encode(encrypted).decode('utf-8')
    except Exception as e:
        logger.error(f"Encryption failed: {e}")
        raise


def decrypt_token(encrypted_token: str) -> str:
    """Decrypt a token from storage.
    
    Args:
        encrypted_token: Base64-encoded encrypted token
        
    Returns:
        Decrypted plain text token
        
    Raises:
        ValueError: If decryption fails (corrupted data or wrong key)
    """
    try:
        cipher = get_cipher()
        encrypted_bytes = base64.urlsafe_b64decode(encrypted_token.encode('utf-8'))
        decrypted = cipher.decrypt(encrypted_bytes)
        return decrypted.decode('utf-8')
    except Exception as e:
        logger.error(f"Decryption failed: {e}")
        raise ValueError(f"Failed to decrypt token: {e}")

