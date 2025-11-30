"""Search-related commands and data handling cog."""

import logging
import sys
import os
from typing import Optional, List, Dict, Any

# Ensure proper imports
current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from core.client import PSNClient
from models import UserProfile

logger = logging.getLogger(__name__)


class SearchCog:
    """Handles search-related data operations."""

    def __init__(self, client: PSNClient):
        self.client = client

    def search_user(self, username: str) -> Optional[UserProfile]:
        """Search for a user by online ID."""
        try:
            profile = self.client.search_user(username.strip())
            return profile
        except Exception as e:
            logger.error(f"Error searching for user {username}: {e}")
            return None

    def search_users_by_name(self, name: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search for users by display name."""
        try:
            users = self.client.search_users_by_name(name, limit=limit)
            return users if users else []
        except Exception as e:
            logger.error(f"Error searching users by name {name}: {e}")
            return []

    def export_profile(self, profile: UserProfile, filename: str) -> None:
        """Export profile to JSON file."""
        import json
        from dataclasses import asdict

        data = asdict(profile)
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2, default=str)
        logger.info(f"Profile exported to {filename}")

    def export_search_results(self, users: List[Dict[str, Any]], filename: str) -> None:
        """Export search results to JSON file."""
        import json

        # Convert dataclasses to dicts for JSON serialization
        data = []
        for user in users:
            user_data = {}
            for key, value in user.items():
                if hasattr(value, '__dict__'):
                    # Handle TrophyData objects
                    user_data[key] = value.__dict__
                else:
                    user_data[key] = value
            data.append(user_data)

        with open(filename, 'w') as f:
            json.dump({"search_results": data, "count": len(data)}, f, indent=2, default=str)
        logger.info(f"Search results exported to {filename}")
