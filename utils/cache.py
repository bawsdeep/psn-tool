"""Caching utilities for PSN Tool."""

import time
from typing import Any, Dict

# Cache for region lookups (avoid slow pycountry calls)
_region_cache: Dict[str, str] = {}

# Simple profile cache (5 minute TTL)
_profile_cache: Dict[str, tuple] = {}
_CACHE_TTL = 300  # 5 minutes


def get_cached_region(region_code: str, lookup_func) -> str:
    """Cached version of region display lookup."""
    if region_code in _region_cache:
        return _region_cache[region_code]

    result = lookup_func(region_code)
    _region_cache[region_code] = result
    return result


def get_cached_profile(cache_key: str, fetch_func, *args, **kwargs) -> Any:
    """Get cached profile data or fetch new data."""
    if cache_key in _profile_cache:
        cached_time, cached_data = _profile_cache[cache_key]
        if time.time() - cached_time < _CACHE_TTL:
            return cached_data

    # Fetch new data
    data = fetch_func(*args, **kwargs)
    _profile_cache[cache_key] = (time.time(), data)
    return data


def clear_cache():
    """Clear all cached data."""
    global _profile_cache, _region_cache
    _profile_cache.clear()
    _region_cache.clear()
