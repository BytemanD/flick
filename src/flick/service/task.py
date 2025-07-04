import asyncio
from typing import Callable

from loguru import logger


def start_task(task: Callable, *args, **kwargs):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    # def _task():
    #     try:
    #         task(*args, **kwargs)
    #     except Exception as e:
    #         logger.error("run task {} failed: {}", task.__name__, e)

    loop.run_until_complete(task(*args, **kwargs))
    # loop.run_until_complete(_task())
