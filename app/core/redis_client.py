from functools import lru_cache

from redis import Redis

from app.core.config import settings


@lru_cache(maxsize=1)
def get_redis_client() -> Redis:
    redis_url = settings.REDIS_URL
    if redis_url is None:
        raise RuntimeError("REDIS_URL is not configured")

    return Redis.from_url(
        redis_url.get_secret_value(),
        socket_timeout=3,
        socket_connect_timeout=3,
    )