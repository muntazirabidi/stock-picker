"""System API router."""

from fastapi import APIRouter, HTTPException

from api.schemas import CacheStats

router = APIRouter()


@router.get("/cache-stats")
async def get_cache_stats() -> CacheStats:
    """Get cache statistics."""
    try:
        from src.data.yahoo_client import YahooFinanceClient

        client = YahooFinanceClient()
        stats = client.cache_stats()

        return CacheStats(
            valid_count=stats.get("valid", 0),
            expired_count=stats.get("expired", 0),
            total_size_mb=stats.get("total_size_mb", 0),
            ttl_hours=stats.get("ttl_hours", 24),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/clear-cache")
async def clear_cache() -> dict:
    """Clear the cache."""
    try:
        from src.data.cache import FileCache

        cache = FileCache()
        cache.clear()

        return {"status": "cleared"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
