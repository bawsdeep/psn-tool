"""PSN API client core functionality."""

import base64
import json
import logging
import tempfile
import time
import sys
import os
from typing import List, Optional, Dict, Any

from psnawp_api import PSNAWP

# Ensure proper imports by adding parent directory to path if needed
current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from core.config import initialize_config, load_settings, save_settings, get_npsso_token, set_npsso_token
from utils.cache import get_cached_region, get_cached_profile, clear_cache
from models import TrophyData, GameData, UserProfile

logger = logging.getLogger(__name__)

# Performance monitoring
_request_times: Dict[str, float] = {}

def _time_operation(operation_name: str):
    """Decorator to time operations for performance monitoring."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            start_time = time.time()
            result = func(*args, **kwargs)
            elapsed = time.time() - start_time
            logger.debug(f"{operation_name} completed in {elapsed:.2f} seconds")
            return result
        return wrapper
    return decorator


class PSNClient:
    """Command-line PSN API client."""

    def __init__(self, npsso: Optional[str] = None):
        # Initialize database configuration
        initialize_config()

        self.psnawp: Optional[PSNAWP] = None
        self.temp_dir = tempfile.mkdtemp(prefix="psntool_")

        if npsso:
            set_npsso_token(npsso)

        stored_npsso = get_npsso_token()
        if stored_npsso or npsso:
            token_to_use = npsso or stored_npsso
            # Let PSNAWP handle its own rate limiting (20 req/min = 300 per 15 min)
            self.authenticate(token_to_use)
        else:
            logger.info("No NPSSO token found. Use --setup or set_npsso() to configure.")

    def clear_cache(self):
        """Clear all cached data."""
        clear_cache()
        logger.info("Cache cleared")

    def __del__(self):
        """Cleanup temporary files."""
        try:
            import shutil
            shutil.rmtree(self.temp_dir, ignore_errors=True)
        except:
            pass

    def authenticate(self, npsso: str) -> bool:
        """Authenticate with PSN using NPSSO token."""
        try:
            logger.info("Authenticating with PSN...")
            self.psnawp = PSNAWP(npsso)

            # Test authentication
            me = self.psnawp.me()
            online_id = me.online_id
            logger.info(f"Successfully authenticated as: {online_id}")

            # Save token to database
            set_npsso_token(npsso)

            return True

        except Exception as e:
            logger.error(f"Authentication failed: {e}")
            self.psnawp = None
            return False

    def set_npsso(self, npsso: str) -> bool:
        """Set and validate NPSSO token."""
        if not npsso or not npsso.strip():
            logger.error("NPSSO token cannot be empty")
            return False

        return self.authenticate(npsso.strip())

    def is_authenticated(self) -> bool:
        """Check if client is authenticated."""
        return self.psnawp is not None

    def get_my_profile(self, include_trophies: bool = True, skip_avatars: bool = False) -> Optional[UserProfile]:
        """Get current user's profile information (always fresh - no caching)."""
        if not self.is_authenticated():
            logger.error("Not authenticated. Please set NPSSO token first.")
            return None

        start_time = time.time()
        logger.debug("Starting profile fetch...")

        # Always fetch fresh data (no caching)
        profile = self._fetch_profile(include_trophies, skip_avatars)

        elapsed = time.time() - start_time
        logger.debug(f"Profile fetch completed in {elapsed:.2f} seconds")
        return profile

    def _fetch_profile(self, include_trophies: bool, skip_avatars: bool) -> Optional[UserProfile]:
        """Internal method to fetch profile data."""
        try:
            logger.info("Fetching profile information...")
            me = self.psnawp.me()

            # Basic info
            online_id = me.online_id
            account_id = me.account_id

            # Convert account ID to resign ID
            try:
                account_id_int = int(account_id)
                resign_id = f"{account_id_int:x}"
            except Exception:
                resign_id = "N/A"

            # Region (cached for speed)
            region_display = "Unknown"
            try:
                region = me.get_region()
                if hasattr(region, 'alpha_2'):
                    region_display = get_cached_region(region.alpha_2, self._get_region_display)
                elif hasattr(region, 'alpha_2_code'):
                    region_display = get_cached_region(region.alpha_2_code, self._get_region_display)
            except Exception:
                pass

            # Avatar and full profile data
            avatar_url = None
            profile_base64 = None
            try:
                legacy_profile = me.get_profile_legacy()
                # Base64 encode the full profile JSON
                profile_base64 = base64.b64encode(
                    json.dumps(legacy_profile).encode()
                ).decode()
                if not skip_avatars:
                    avatar_info = legacy_profile['profile']['avatarUrls']
                    if avatar_info:
                        avatar_url = avatar_info[0]['avatarUrl']
            except Exception:
                pass

            # Trophies (optional for speed)
            trophies = None
            if include_trophies:
                try:
                    trophy_summary = me.trophy_summary()
                    trophies = TrophyData(
                        bronze=trophy_summary.earned_trophies.bronze,
                        silver=trophy_summary.earned_trophies.silver,
                        gold=trophy_summary.earned_trophies.gold,
                        platinum=trophy_summary.earned_trophies.platinum,
                        level=trophy_summary.trophy_level,
                        total_count=trophy_summary.earned_trophies.bronze +
                                   trophy_summary.earned_trophies.silver +
                                   trophy_summary.earned_trophies.gold +
                                   trophy_summary.earned_trophies.platinum
                    )
                except Exception as e:
                    logger.debug(f"Could not fetch trophy data: {e}")

            return UserProfile(
                online_id=online_id,
                account_id=account_id,
                resign_id=resign_id,
                region=region_display,
                avatar_url=avatar_url,
                trophies=trophies,
                profile_base64=profile_base64
            )

        except Exception as e:
            logger.error(f"Failed to get profile: {e}")
            return None

    def _get_region_display(self, region_code: str) -> str:
        """Convert region code to display name (optimized)."""
        if not region_code:
            return "Unknown"

        # Simple mapping for common regions (fast)
        common_regions = {
            'US': 'United States',
            'GB': 'United Kingdom',
            'DE': 'Germany',
            'FR': 'France',
            'IT': 'Italy',
            'ES': 'Spain',
            'JP': 'Japan',
            'KR': 'South Korea',
            'AU': 'Australia',
            'CA': 'Canada',
            'BR': 'Brazil',
            'MX': 'Mexico',
            'RU': 'Russia',
            'CN': 'China',
            'IN': 'India',
            'NL': 'Netherlands',
            'SE': 'Sweden',
            'NO': 'Norway',
            'DK': 'Denmark',
            'FI': 'Finland'
        }

        region_upper = region_code.upper()
        if region_upper in common_regions:
            return f"{common_regions[region_upper]} ({region_upper})"

        # Fallback to pycountry for less common regions
        try:
            import pycountry
            country = pycountry.countries.get(alpha_2=region_upper)
            if country:
                return f"{country.name} ({region_upper})"
        except Exception:
            pass

        return region_upper

    def get_friends_list(self, limit: int = 200, progress_callback=None) -> List[str]:
        """Get list of friends' online IDs."""
        if not self.is_authenticated():
            logger.error("Not authenticated. Please set NPSSO token first.")
            return []

        try:
            logger.info("Fetching friends list...")
            if progress_callback:
                progress_callback("Connecting to PSN...")

            me = self.psnawp.me()
            friends_generator = me.friends_list(limit=limit)

            friends = []
            processed = 0

            for friend_user in friends_generator:
                try:
                    if hasattr(friend_user, 'online_id'):
                        friend_name = friend_user.online_id
                    elif hasattr(friend_user, 'get_profile'):
                        profile = friend_user.get_profile()
                        friend_name = profile.get('onlineId', 'Unknown')
                    else:
                        friend_name = str(friend_user)

                    friends.append(friend_name)
                    processed += 1

                    # Update progress every 10 friends
                    if progress_callback and processed % 10 == 0:
                        progress_callback(f"Loaded {processed} friends...")

                except Exception as e:
                    logger.warning(f"Error processing friend: {e}")
                    continue

            if progress_callback:
                progress_callback(f"Completed! Found {len(friends)} friends")

            logger.info(f"Found {len(friends)} friends")
            return friends

        except Exception as e:
            logger.error(f"Failed to get friends list: {e}")
            if progress_callback:
                progress_callback("Error loading friends list")
            return []

    def get_user_friends_list(self, online_id: str, limit: int = 100) -> List[str]:
        """Get another user's friends list by their online ID.

        Note: PSN privacy settings usually make friends lists private.
        This will only work for users who have made their friends list public.
        """
        if not self.is_authenticated():
            logger.error("Not authenticated. Please set NPSSO token first.")
            return []

        if not online_id or not online_id.strip():
            logger.error("Online ID cannot be empty")
            return []

        try:
            logger.info(f"Attempting to get friends list for user: {online_id}")

            # Check if this is the current user's own friends list
            me = self.psnawp.me()
            if me.online_id.lower() == online_id.strip().lower():
                logger.info("Getting your own friends list - using direct API")
                return self.get_friends_list(limit=limit)

            # Try to get the user's friends list
            user = self.psnawp.user(online_id=online_id.strip())

            # Check if the user object has a friends_list method
            if hasattr(user, 'friends_list'):
                logger.info(f"Attempting to access friends list for {online_id}")
                try:
                    friends_generator = user.friends_list(limit=limit)

                    friends = []
                    for friend_user in friends_generator:
                        try:
                            if hasattr(friend_user, 'online_id'):
                                friend_name = friend_user.online_id
                            elif hasattr(friend_user, 'get_profile'):
                                profile = friend_user.get_profile()
                                friend_name = profile.get('onlineId', 'Unknown')
                            else:
                                friend_name = str(friend_user)

                            friends.append(friend_name)
                        except Exception as e:
                            logger.warning(f"Error processing friend for {online_id}: {e}")
                            continue

                    logger.info(f"Successfully retrieved {len(friends)} friends for {online_id}")
                    return friends

                except Exception as e:
                    logger.warning(f"Could not access friends list for {online_id}: {e}")
                    logger.info("This user may have their friends list set to private")
                    return []

            else:
                logger.warning(f"PSNAWP user object does not support friends_list for user: {online_id}")
                return []

        except Exception as e:
            logger.error(f"Failed to get friends list for {online_id}: {e}")
            return []

    def get_games_list(self, limit: int = 100) -> List[GameData]:
        """Get list of current user's games."""
        if not self.is_authenticated():
            logger.error("Not authenticated. Please set NPSSO token first.")
            return []

        try:
            logger.info("Fetching games list...")
            me = self.psnawp.me()
            games_iterator = me.title_stats(limit=limit)

            games = []
            for game in games_iterator:
                try:
                    game_info = GameData(
                        name=getattr(game, 'name', 'Unknown Game'),
                        play_count=getattr(game, 'play_count', 0),
                        category=getattr(game, 'category', 'Unknown'),
                        platform=str(getattr(game, 'platform', 'Unknown')),
                        title_id=getattr(game, 'title_id', ''),
                        progress=getattr(game, 'progress', None),
                        play_duration=str(getattr(game, 'play_duration', '')) if getattr(game, 'play_duration', None) else None,
                        first_played=str(getattr(game, 'first_played_date', ''))[:10] if getattr(game, 'first_played_date', None) else None,
                        last_played=str(getattr(game, 'last_played_date', ''))[:10] if getattr(game, 'last_played_date', None) else None
                    )

                    # Get image URL
                    try:
                        if hasattr(game, 'image_url') and game.image_url:
                            game_info.image_url = game.image_url
                        elif hasattr(game, 'concept') and game.concept and hasattr(game.concept, 'image_url'):
                            game_info.image_url = game.concept.image_url
                    except:
                        pass

                    games.append(game_info)

                except Exception as e:
                    logger.warning(f"Error processing game: {e}")
                    continue

            logger.info(f"Found {len(games)} games")
            return games

        except Exception as e:
            logger.error(f"Failed to get games list: {e}")
            return []

    def get_user_games_list(self, online_id: str, limit: int = 100) -> List[GameData]:
        """Get another user's games list by their online ID.

        Note: PSN privacy settings usually make games lists private.
        This will only work for users who have made their games list public.
        """
        if not self.is_authenticated():
            logger.error("Not authenticated. Please set NPSSO token first.")
            return []

        if not online_id or not online_id.strip():
            logger.error("Online ID cannot be empty")
            return []

        try:
            logger.info(f"Attempting to get games list for user: {online_id}")

            # Check if this is the current user's own games list
            me = self.psnawp.me()
            if me.online_id.lower() == online_id.strip().lower():
                logger.info("Getting your own games list - using direct API")
                return self.get_games_list(limit=limit)

            # Try to get the user's games list
            user = self.psnawp.user(online_id=online_id.strip())

            # Check if the user object has a title_stats method
            if hasattr(user, 'title_stats'):
                logger.info(f"Attempting to access games list for {online_id}")
                try:
                    games_iterator = user.title_stats(limit=limit)

                    games = []
                    for game in games_iterator:
                        try:
                            game_info = GameData(
                                name=getattr(game, 'name', 'Unknown Game'),
                                play_count=getattr(game, 'play_count', 0),
                                category=getattr(game, 'category', 'Unknown'),
                                platform=str(getattr(game, 'platform', 'Unknown')),
                                title_id=getattr(game, 'title_id', ''),
                                progress=getattr(game, 'progress', None),
                                play_duration=str(getattr(game, 'play_duration', '')) if getattr(game, 'play_duration', None) else None,
                                first_played=str(getattr(game, 'first_played_date', ''))[:10] if getattr(game, 'first_played_date', None) else None,
                                last_played=str(getattr(game, 'last_played_date', ''))[:10] if getattr(game, 'last_played_date', None) else None
                            )

                            # Get image URL
                            try:
                                if hasattr(game, 'image_url') and game.image_url:
                                    game_info.image_url = game.image_url
                                elif hasattr(game, 'concept') and game.concept and hasattr(game.concept, 'image_url'):
                                    game_info.image_url = game.concept.image_url
                            except:
                                pass

                            games.append(game_info)

                        except Exception as e:
                            logger.warning(f"Error processing game for {online_id}: {e}")
                            continue

                    logger.info(f"Successfully retrieved {len(games)} games for {online_id}")
                    return games

                except Exception as e:
                    logger.warning(f"Could not access games list for {online_id}: {e}")
                    logger.info("This user may have their games list set to private")
                    return []

            else:
                logger.warning(f"PSNAWP user object does not support title_stats for user: {online_id}")
                return []

        except Exception as e:
            logger.error(f"Failed to get games list for {online_id}: {e}")
            return []

    def search_user(self, online_id: str) -> Optional[UserProfile]:
        """Search for a user by online ID."""
        if not self.is_authenticated():
            logger.error("Not authenticated. Please set NPSSO token first.")
            return None

        if not online_id or not online_id.strip():
            logger.error("Online ID cannot be empty")
            return None

        try:
            logger.info(f"Searching for user: {online_id}")
            user = self.psnawp.user(online_id=online_id.strip())

            # Basic info
            found_online_id = getattr(user, "online_id", None)
            account_id = user.account_id

            # Convert account ID to resign ID
            try:
                account_id_int = int(account_id)
                resign_id = f"{account_id_int:x}"
            except Exception:
                resign_id = "N/A"

            # Region
            try:
                region = user.get_region()
                if hasattr(region, 'alpha_2'):
                    region_display = get_cached_region(region.alpha_2, self._get_region_display)
                elif hasattr(region, 'alpha_2_code'):
                    region_display = get_cached_region(region.alpha_2_code, self._get_region_display)
                else:
                    region_display = "Unknown"
            except Exception:
                region_display = "Unknown"

            # Avatar and full profile data
            avatar_url = None
            profile_base64 = None
            try:
                legacy_profile = user.get_profile_legacy()
                # Base64 encode the full profile JSON
                profile_base64 = base64.b64encode(
                    json.dumps(legacy_profile).encode()
                ).decode()
                avatar_info = legacy_profile['profile']['avatarUrls']
                if avatar_info:
                    avatar_url = avatar_info[0]['avatarUrl']
            except Exception:
                pass

            # Trophies
            trophies = None
            try:
                trophy_summary = user.trophy_summary()
                trophies = TrophyData(
                    bronze=trophy_summary.earned_trophies.bronze,
                    silver=trophy_summary.earned_trophies.silver,
                    gold=trophy_summary.earned_trophies.gold,
                    platinum=trophy_summary.earned_trophies.platinum,
                    level=trophy_summary.trophy_level,
                    total_count=trophy_summary.earned_trophies.bronze +
                               trophy_summary.earned_trophies.silver +
                               trophy_summary.earned_trophies.gold +
                               trophy_summary.earned_trophies.platinum
                )
            except Exception as e:
                logger.warning(f"Could not fetch trophy data: {e}")

            # Last online
            last_online = None
            try:
                presence = user.get_presence()
                if hasattr(presence, 'last_online_date_time') and presence.last_online_date_time:
                    last_online = str(presence.last_online_date_time)[:19].replace('T', ' ')
            except Exception:
                pass

            return UserProfile(
                online_id=found_online_id or online_id,
                account_id=account_id,
                resign_id=resign_id,
                region=region_display,
                avatar_url=avatar_url,
                trophies=trophies,
                last_online=last_online,
                profile_base64=profile_base64
            )

        except Exception as e:
            logger.error(f"User '{online_id}' not found or profile is private: {e}")
            return None

    def search_users_by_name(self, name: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search for users by name/display name."""
        if not self.is_authenticated():
            logger.error("Not authenticated. Please set NPSSO token first.")
            return []

        if not name or not name.strip():
            logger.error("Search name cannot be empty")
            return []

        try:
            logger.info(f"Searching for users with name: {name}")
            # PSNAWP doesn't have a direct name search, but we can try online_id search
            # For a more comprehensive search, we'd need to use the search API
            # For now, we'll implement a basic online_id search
            user = self.search_user(name.strip())
            if user:
                return [{
                    'online_id': user.online_id,
                    'account_id': user.account_id,
                    'region': user.region,
                    'avatar_url': user.avatar_url,
                    'trophies': user.trophies,
                    'last_online': user.last_online,
                    'profile_base64': user.profile_base64
                }]
            else:
                logger.info(f"No users found with online ID: {name}")
                return []

        except Exception as e:
            logger.error(f"Error searching for users by name '{name}': {e}")
            return []
