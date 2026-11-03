from typing import Optional, Dict, Any
import json
from app.core.config import settings
from app.core.logging import logger

try:
    import redis.asyncio as aioredis
    HAS_REDIS = True
except ImportError:
    HAS_REDIS = False
    aioredis = None

redis_pool: Optional[Any] = None


async def init_redis_pool():
    """Initialize persistent Redis async connection pool with graceful offline fallback."""
    global redis_pool
    if not HAS_REDIS:
        logger.info("Redis library not installed. Running in standalone local mode.")
        return

    if redis_pool is None:
        try:
            client = aioredis.from_url(
                settings.REDIS_URL,
                encoding="utf-8",
                decode_responses=True,
                max_connections=50,
            )
            # Ping with timeout to verify connectivity
            await client.ping()
            redis_pool = client
            logger.info("Connected to Redis successfully.")
        except Exception as e:
            logger.warning(f"Redis not available on {settings.REDIS_URL} ({e}). Falling back to local in-memory messaging.")
            redis_pool = None


async def close_redis_pool():
    """Gracefully terminate Redis pool on app shutdown."""
    global redis_pool
    if redis_pool is not None:
        try:
            await redis_pool.close()
            logger.info("Redis connection pool closed.")
        except Exception:
            pass
        redis_pool = None


async def get_redis_client():
    """Dependency or accessor for the async Redis client."""
    global redis_pool
    return redis_pool


class RedisService:
    """Helper service for Redis caching, pub/sub, and workspace broadcasting with local in-memory fallback."""

    # In-memory cache fallback when Redis is absent
    _memory_cache: Dict[str, str] = {}

    @classmethod
    async def publish_workspace_event(cls, workspace_id: str, event_type: str, data: dict):
        """Publish real-time event to a specific workspace channel or local broadcast."""
        client = await get_redis_client()
        if client:
            try:
                channel = f"workspace:{workspace_id}"
                payload = json.dumps({"event": event_type, "data": data})
                await client.publish(channel, payload)
                return
            except Exception as e:
                logger.warning(f"Failed to publish to Redis: {e}")

        # Local in-memory broadcast fallback
        from app.api.websockets.connection_manager import ws_manager
        await ws_manager.broadcast_to_workspace(
            workspace_id,
            {"event": event_type, "data": data}
        )

    @classmethod
    async def set_cache(cls, key: str, value: str, expire_seconds: int = 3600):
        client = await get_redis_client()
        if client:
            try:
                await client.set(key, value, ex=expire_seconds)
                return
            except Exception:
                pass
        cls._memory_cache[key] = value

    @classmethod
    async def get_cache(cls, key: str) -> Optional[str]:
        client = await get_redis_client()
        if client:
            try:
                return await client.get(key)
            except Exception:
                pass
        return cls._memory_cache.get(key)
