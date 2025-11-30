"""Token management data handling cog."""

import logging
import sys
import os

# Ensure proper imports
current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from core.client import PSNClient

logger = logging.getLogger(__name__)


class TokenCog:
    """Handles token management data operations."""

    def __init__(self, client: PSNClient):
        self.client = client

    def set_npsso_token(self, token: str) -> bool:
        """Set NPSSO token and validate it."""
        try:
            return self.client.set_npsso(token)
        except Exception as e:
            logger.error(f"Error setting NPSSO token: {e}")
            return False

    def is_authenticated(self) -> bool:
        """Check if client is authenticated."""
        try:
            return self.client.is_authenticated()
        except Exception as e:
            logger.error(f"Error checking authentication: {e}")
            return False

    def clear_cache(self):
        """Clear client cache."""
        try:
            self.client.clear_cache()
        except Exception as e:
            logger.error(f"Error clearing cache: {e}")

    def delete_token(self) -> bool:
        """Delete the stored NPSSO token."""
        try:
            # Clear the token from database
            from utils.database import set_setting
            set_setting("npsso", "")
            # Clear in-memory caches
            self.clear_cache()
            return True
        except Exception as e:
            logger.error(f"Error deleting token: {e}")
            return False

    def get_token_status(self) -> dict:
        """Get current token status information."""
        try:
            import core.config
            token = core.config.get_npsso_token()

            status = {
                "has_token": bool(token),
                "token_length": len(token) if token else 0,
                "is_authenticated": self.is_authenticated()
            }

            if token:
                # Mask the token for security
                status["masked_token"] = token[:10] + "..." + token[-10:] if len(token) > 20 else "***masked***"

            return status
        except Exception as e:
            logger.error(f"Error getting token status: {e}")
            return {"has_token": False, "is_authenticated": False}
