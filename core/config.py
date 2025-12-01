"""Configuration management for PSN Tool."""

import logging
import sys
import os
from typing import Dict, Any, Optional

# Ensure proper imports
current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

logger = logging.getLogger(__name__)


def initialize_config():
    """Initialize the configuration system."""
    import utils.database
    utils.database.initialize_database()


def load_settings() -> Dict[str, Any]:
    """Load all settings from database."""
    try:
        import utils.database
        return utils.database.get_all_settings()
    except Exception as e:
        logger.warning(f"Could not load settings from database: {e}")
        return {}


def save_settings(settings: Dict[str, Any]) -> None:
    """Save settings to database."""
    try:
        import utils.database
        for key, value in settings.items():
            utils.database.set_setting(key, str(value))
    except Exception as e:
        logger.error(f"Could not save settings to database: {e}")


def get_npsso_token() -> Optional[str]:
    """Get the stored NPSSO token (decrypted)."""
    try:
        import utils.database
        # Try to get encrypted token first (new format)
        token = utils.database.get_setting("npsso", encrypted=True)
        if token:
            return token
        
        # Fallback: try unencrypted token (for migration)
        token = utils.database.get_setting("npsso", encrypted=False)
        if token:
            # Migrate to encrypted format
            logger.info("Migrating NPSSO token to encrypted storage")
            set_npsso_token(token)  # This will encrypt it
            return token
        
        return None
    except Exception as e:
        logger.error(f"Could not retrieve NPSSO token: {e}")
        return None


def set_npsso_token(token: str) -> None:
    """Set the NPSSO token (encrypted)."""
    try:
        import utils.database
        utils.database.set_setting("npsso", token, encrypt=True)
        logger.info("NPSSO token saved (encrypted)")
    except Exception as e:
        logger.error(f"Could not save NPSSO token: {e}")
        raise


# Legacy compatibility functions
def ensure_settings_dir():
    """Legacy function for compatibility."""
    pass
