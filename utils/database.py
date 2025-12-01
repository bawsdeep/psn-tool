"""Database utilities for PSN Tool."""

import sqlite3
import os
import logging
import platform
from pathlib import Path
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

# Cross-platform application data directory
def get_app_data_dir() -> Path:
    """Get the appropriate application data directory for the current platform."""
    system = platform.system()

    if system == "Windows":
        # Windows: %APPDATA%\PSNTool
        appdata = os.environ.get("APPDATA")
        if appdata:
            return Path(appdata) / "PSNTool"
        else:
            return Path.home() / "AppData" / "Roaming" / "PSNTool"

    elif system == "Darwin":  # macOS
        # macOS: ~/Library/Application Support/PSNTool
        return Path.home() / "Library" / "Application Support" / "PSNTool"

    else:  # Linux and other Unix-like systems
        # Linux: ~/.local/share/psntool (XDG Base Directory spec)
        # Fallback to ~/.psntool for compatibility
        xdg_data = os.environ.get("XDG_DATA_HOME")
        if xdg_data:
            return Path(xdg_data) / "psntool"
        else:
            return Path.home() / ".local" / "share" / "psntool"

DB_PATH = get_app_data_dir() / "psntool.db"


def migrate_old_database():
    """Migrate database and settings from old location to new cross-platform location."""
    old_dir = Path.home() / ".psntool"
    new_dir = get_app_data_dir()

    if old_dir.exists() and old_dir != new_dir:
        logger.info(f"Migrating PSN Tool data from {old_dir} to {new_dir}")

        try:
            # Ensure new directory exists
            new_dir.mkdir(parents=True, exist_ok=True)

            # Migrate database
            old_db = old_dir / "psntool.db"
            new_db = new_dir / "psntool.db"
            if old_db.exists() and not new_db.exists():
                old_db.replace(new_db)
                logger.info("Database migrated successfully")

            # Migrate settings (if it exists)
            old_settings = old_dir / "settings.json"
            new_settings = new_dir / "settings.json"
            if old_settings.exists() and not new_settings.exists():
                old_settings.replace(new_settings)
                logger.info("Settings migrated successfully")

            # Try to remove old directory if empty
            try:
                old_dir.rmdir()
                logger.info("Cleaned up old directory")
            except OSError:
                # Directory not empty, leave it
                pass

        except Exception as e:
            logger.error(f"Migration failed: {e}")
            # If migration fails, keep using old paths
            global DB_PATH
            DB_PATH = old_dir / "psntool.db"


def ensure_db_dir():
    """Ensure the database directory exists."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)


def get_db_connection():
    """Get a database connection."""
    # Migrate from old location if needed (one-time operation)
    migrate_old_database()
    ensure_db_dir()
    return sqlite3.connect(str(DB_PATH))


def initialize_database():
    """Initialize the database with required tables."""
    with get_db_connection() as conn:
        cursor = conn.cursor()

        # Create settings table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Create tokens table for better token management
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tokens (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                token_type TEXT NOT NULL,  -- 'npsso', 'access_token', etc.
                token_value TEXT NOT NULL,
                is_active BOOLEAN DEFAULT 1,
                expires_at TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Create indexes
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_settings_key ON settings(key)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_tokens_type_active ON tokens(token_type, is_active)')

        conn.commit()
        logger.info("Database initialized successfully")


def get_setting(key: str, encrypted: bool = False) -> Optional[str]:
    """Get a setting value from the database.
    
    Args:
        key: Setting key to retrieve
        encrypted: If True, decrypt the value before returning
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT value FROM settings WHERE key = ?', (key,))
        result = cursor.fetchone()
        if not result:
            return None
        
        value = result[0]
        
        # Decrypt if needed
        if encrypted:
            try:
                from utils.encryption import decrypt_token
                value = decrypt_token(value)
            except Exception as e:
                logger.error(f"Failed to decrypt setting {key}: {e}")
                return None
        
        return value


def set_setting(key: str, value: str, encrypt: bool = False):
    """Set a setting value in the database.
    
    Args:
        key: Setting key
        value: Setting value to store
        encrypt: If True, encrypt the value before storing
    """
    # Encrypt if needed
    if encrypt:
        try:
            from utils.encryption import encrypt_token
            value = encrypt_token(value)
        except Exception as e:
            logger.error(f"Failed to encrypt setting {key}: {e}")
            raise
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO settings (key, value, updated_at)
            VALUES (?, ?, CURRENT_TIMESTAMP)
        ''', (key, value))
        conn.commit()


def save_token(token_type: str, token_value: str, expires_at: Optional[str] = None):
    """Save a token to the database."""
    with get_db_connection() as conn:
        cursor = conn.cursor()

        # First, deactivate any existing tokens of this type
        cursor.execute('''
            UPDATE tokens SET is_active = 0, updated_at = CURRENT_TIMESTAMP
            WHERE token_type = ? AND is_active = 1
        ''', (token_type,))

        # Insert the new token
        cursor.execute('''
            INSERT INTO tokens (token_type, token_value, expires_at, is_active)
            VALUES (?, ?, ?, 1)
        ''', (token_type, token_value, expires_at))

        conn.commit()
        logger.info(f"Token saved: {token_type}")


def get_active_token(token_type: str) -> Optional[str]:
    """Get the active token of a specific type."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT token_value FROM tokens
            WHERE token_type = ? AND is_active = 1
            ORDER BY created_at DESC LIMIT 1
        ''', (token_type,))
        result = cursor.fetchone()
        return result[0] if result else None


def get_all_settings() -> Dict[str, str]:
    """Get all settings as a dictionary."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT key, value FROM settings')
        return {row[0]: row[1] for row in cursor.fetchall()}


def clear_all_data():
    """Clear all data from the database (for testing/reset)."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('DELETE FROM settings')
        cursor.execute('DELETE FROM tokens')
        cursor.execute('DELETE FROM sqlite_sequence WHERE name IN ("settings", "tokens")')
        conn.commit()
        logger.info("All database data cleared")
