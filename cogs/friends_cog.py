"""Friends-related commands and data handling cog."""

import json
import logging
import sys
import os
from typing import List, Dict, Any, Optional

# Ensure proper imports
current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from core.client import PSNClient
from models import UserProfile

logger = logging.getLogger(__name__)


class FriendsCog:
    """Handles friends-related data operations."""

    def __init__(self, client: PSNClient):
        self.client = client

    def get_friends_list(self, limit: int = 50) -> List[str]:
        """Get current user's friends list."""
        try:
            friends = self.client.get_friends_list(limit=limit)
            return friends if friends else []
        except Exception as e:
            logger.error(f"Error getting friends list: {e}")
            return []

    def get_user_friends_list(self, user_id: str, limit: int = 100) -> List[str]:
        """Get another user's friends list."""
        try:
            friends = self.client.get_user_friends_list(user_id, limit=limit)
            return friends if friends else []
        except Exception as e:
            logger.error(f"Error getting user friends list for {user_id}: {e}")
            return []

    def search_friend_profile(self, friend_name: str) -> Optional[UserProfile]:
        """Search for a friend's profile."""
        try:
            profile = self.client.search_user(friend_name.strip())
            return profile
        except Exception as e:
            logger.error(f"Error searching for friend {friend_name}: {e}")
            return None

    def export_friends(self, friends: List[str], filename: str) -> None:
        """Export friends list to JSON file."""
        data = {"friends": friends, "count": len(friends)}
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        logger.info(f"Friends exported to {filename}")
