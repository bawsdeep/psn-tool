"""Games-related commands and data handling cog."""

import json
import logging
import sys
import os
from typing import List, Optional

# Ensure proper imports
current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from core.client import PSNClient
from models import GameData

logger = logging.getLogger(__name__)


class GamesCog:
    """Handles games-related data operations."""

    def __init__(self, client: PSNClient):
        self.client = client

    def get_games_list(self, limit: int = 20) -> List[GameData]:
        """Get current user's games list."""
        try:
            games = self.client.get_games_list(limit=limit)
            return games if games else []
        except Exception as e:
            logger.error(f"Error getting games list: {e}")
            return []

    def export_games(self, games: List[GameData], filename: str) -> None:
        """Export games list to JSON file."""
        from dataclasses import asdict
        data = [asdict(game) for game in games]
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2, default=str)
        logger.info(f"Games exported to {filename}")
