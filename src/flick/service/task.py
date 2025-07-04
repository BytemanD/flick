import asyncio
from typing import Callable


def start_task(task: Callable, *args, **kwargs):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    loop.run_until_complete(task(*args, **kwargs))
