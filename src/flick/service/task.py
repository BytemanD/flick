from concurrent import futures
from typing import Callable

from loguru import logger

executor = futures.ThreadPoolExecutor()


def submit(task: Callable, *args, **kwargs):
    logger.info('submit task: {}', task)
    executor.submit(task, *args, **kwargs)
