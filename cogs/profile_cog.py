"""Profile-related commands and data handling cog."""

import logging
import sys
import os
from typing import Optional

# Ensure proper imports
current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from core.client import PSNClient
from models import UserProfile

logger = logging.getLogger(__name__)


class ProfileCog:
    """Handles profile-related data operations."""

    def __init__(self, client: PSNClient):
        self.client = client

    def get_my_profile(self, include_trophies: bool = True, skip_avatars: bool = False) -> Optional[UserProfile]:
        """Get current user's profile."""
        try:
            profile = self.client.get_my_profile(include_trophies=include_trophies, skip_avatars=skip_avatars)
            return profile
        except Exception as e:
            logger.error(f"Error getting profile: {e}")
            return None

    def export_profile(self, profile: UserProfile, filename: str) -> None:
        """Export profile to JSON file."""
        import json
        from dataclasses import asdict

        data = asdict(profile)
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2, default=str)
        logger.info(f"Profile exported to {filename}")
