"""File-based caching with TTL for API responses."""

import hashlib
import json
import time
from pathlib import Path
from typing import Any

from pydantic_settings import BaseSettings


class CacheSettings(BaseSettings):
    """Cache configuration from environment."""

    cache_ttl_hours: int = 168  # 7 days - fundamentals change quarterly
    cache_dir: Path = Path("data/cache")

    class Config:
        env_file = ".env"
        extra = "ignore"


class FileCache:
    """Simple file-based cache with TTL support.

    Stores JSON-serializable data in files with metadata for expiration.
    """

    def __init__(self, cache_dir: Path | None = None, ttl_hours: int | None = None):
        settings = CacheSettings()
        self.cache_dir = cache_dir or settings.cache_dir
        self.ttl_seconds = (ttl_hours or settings.cache_ttl_hours) * 3600
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def _get_cache_path(self, key: str) -> Path:
        """Generate cache file path from key."""
        # Hash the key to handle special characters and long keys
        key_hash = hashlib.md5(key.encode()).hexdigest()
        return self.cache_dir / f"{key_hash}.json"

    def get(self, key: str) -> Any | None:
        """Retrieve cached value if exists and not expired.

        Args:
            key: Cache key (typically endpoint + params)

        Returns:
            Cached data or None if not found/expired
        """
        cache_path = self._get_cache_path(key)

        if not cache_path.exists():
            return None

        try:
            with open(cache_path) as f:
                cached = json.load(f)

            # Check expiration
            if time.time() - cached["timestamp"] > self.ttl_seconds:
                cache_path.unlink()  # Delete expired cache
                return None

            return cached["data"]

        except (json.JSONDecodeError, KeyError):
            # Corrupted cache file
            cache_path.unlink(missing_ok=True)
            return None

    def set(self, key: str, data: Any) -> None:
        """Store data in cache.

        Args:
            key: Cache key
            data: JSON-serializable data to cache
        """
        cache_path = self._get_cache_path(key)

        cached = {
            "timestamp": time.time(),
            "key": key,
            "data": data,
        }

        with open(cache_path, "w") as f:
            json.dump(cached, f)

    def invalidate(self, key: str) -> bool:
        """Remove specific cache entry.

        Returns:
            True if entry was removed, False if not found
        """
        cache_path = self._get_cache_path(key)
        if cache_path.exists():
            cache_path.unlink()
            return True
        return False

    def clear(self) -> int:
        """Clear all cached data.

        Returns:
            Number of cache files removed
        """
        count = 0
        for cache_file in self.cache_dir.glob("*.json"):
            cache_file.unlink()
            count += 1
        return count

    def stats(self) -> dict[str, Any]:
        """Get cache statistics."""
        cache_files = list(self.cache_dir.glob("*.json"))
        total_size = sum(f.stat().st_size for f in cache_files)

        expired = 0
        valid = 0
        now = time.time()

        for f in cache_files:
            try:
                with open(f) as file:
                    cached = json.load(file)
                if now - cached["timestamp"] > self.ttl_seconds:
                    expired += 1
                else:
                    valid += 1
            except (json.JSONDecodeError, KeyError):
                expired += 1

        return {
            "total_files": len(cache_files),
            "valid": valid,
            "expired": expired,
            "total_size_mb": round(total_size / (1024 * 1024), 2),
            "ttl_hours": self.ttl_seconds / 3600,
        }
