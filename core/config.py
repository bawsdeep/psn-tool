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
    """Get the stored NPSSO token."""
    try:
        import utils.database
        return utils.database.get_setting("npsso")
    except Exception:
        return None


def set_npsso_token(token: str) -> None:
    """Set the NPSSO token."""
    try:
        import utils.database
        utils.database.set_setting("npsso", token)
    except Exception as e:
        logger.error(f"Could not save NPSSO token: {e}")


# Legacy compatibility functions
def ensure_settings_dir():
    """Legacy function for compatibility."""
    pass
