import time
from functools import lru_cache, wraps
from typing import Optional


def timed_lru_cache(maxsize: Optional[int] = None, seconds: int = 3600):
    def wrapper_cache(func):
        func = lru_cache(maxsize=maxsize)(func)
        func.lifetime = seconds  # type: ignore
        func.expiration = time.monotonic() + func.lifetime  # type: ignore

        @wraps(func)
        def wrapped_func(*args, **kwargs):
            if time.monotonic() >= func.expiration:  # type: ignore
                func.cache_clear()
                func.expiration = time.monotonic() + func.lifetime  # type: ignore
            return func(*args, **kwargs)

        return wrapped_func

    return wrapper_cache
