import os
import pathlib
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


def strtobool(value: str) -> bool:
    if not value:
        return False
    return value.lower() in ("true", "1", "yes", "on")


def data_path(app_name: str) -> pathlib.Path:
    """获取数据目录下的文件路径"""
    appdir = os.getenv("APPDIR")
    if not appdir:
        appdir = "/usr/share"
    return pathlib.Path(appdir, app_name)
