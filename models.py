"""Data models for PSN Tool."""

from dataclasses import dataclass
from typing import Optional


@dataclass
class TrophyData:
    bronze: int = 0
    silver: int = 0
    gold: int = 0
    platinum: int = 0
    level: int = 0
    total_count: int = 0


@dataclass
class GameData:
    name: str
    play_count: int = 0
    category: str = ""
    platform: str = ""
    title_id: str = ""
    progress: Optional[int] = None
    play_duration: Optional[str] = None
    first_played: Optional[str] = None
    last_played: Optional[str] = None
    image_url: Optional[str] = None


@dataclass
class UserProfile:
    online_id: str
    account_id: str
    resign_id: str
    region: str
    avatar_url: Optional[str] = None
    trophies: Optional[TrophyData] = None
    last_online: Optional[str] = None
    profile_base64: Optional[str] = None
