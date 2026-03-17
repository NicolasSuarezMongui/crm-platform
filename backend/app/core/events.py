import logging

import redis.asyncio as aioredis

from app.core.config import settings
from app.db.session import engine

logger = logging.getLogger(__name__)

# Module-level Redis client (shared across requests)
redis_client: aioredis.Redis | None = None


async def on_startup() -> None:
    global redis_client

    # Verify DB connection
    try:
        async with engine.connect() as conn:
            await conn.execute(__import__("sqlalchemy").text("SELECT 1"))
        logger.info("PostgreSQL connection OK")
    except Exception as e:
        logger.error(f"PostgreSQL connection FAILED: {e}")
        raise

    # Init Redis
    """try:
        redis_client = aioredis.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_response=True
        )
        await redis_client.ping()
        logger.info("Redis connection OK")
    except Exception as e:
        logger.error(f"Redis connection FAILED: {e}")
        raise
    """


async def on_shutdown() -> None:
    global redis_client

    await engine.dispose()
    logger.info("Database connections closed")

    # if redis_client:
    #    await redis_client.aclose()
    #    logger.info("Redis connection closed")


def get_redis() -> aioredis.Redis:
    """FastAPI dependency to get the Redis client."""
    if redis_client is None:
        raise RuntimeError("Redis not initialized")
    return redis_client
