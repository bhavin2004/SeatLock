from app.core.redis_client import get_redis_client




def _increment_counter(key: str, *, window_seconds: int = 60) -> tuple[int, int]:
    client = get_redis_client()
    with client.pipeline(transaction=True) as pipe:
        pipe.incr(key)
        pipe.expire(key, window_seconds, nx=True)
        pipe.ttl(key)
        count, _, ttl = pipe.execute()
    return int(count), int(ttl)

def count_login_request(ip: str, *, window_seconds: int = 60) -> tuple[int, int]:
    return _increment_counter(
        f"cinebook:login:ip:{ip}", 
        window_seconds=window_seconds
    )

def  count_login_request_by_email(email: str, *, window_seconds: int = 60) -> tuple[int, int]:
    normalized_email = email.strip().lower()
    return _increment_counter(
        f"cinebook:login:email:{normalized_email}", 
        window_seconds=window_seconds
    )