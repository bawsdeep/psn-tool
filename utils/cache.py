"""Caching utilities for PSN Tool (disabled - always fresh data)."""

from typing import Any


def get_cached_region(region_code: str, lookup_func) -> str:
    """Always fresh region lookup (no caching)."""
    return lookup_func(region_code)


def get_cached_profile(cache_key: str, fetch_func, *args, **kwargs) -> Any:
    """Always fetch fresh data - no caching."""
    # Always fetch fresh data (no caching)
    return fetch_func(*args, **kwargs)


def clear_cache():
    """No-op function (caching disabled)."""
    pass
