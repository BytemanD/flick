from concurrent import futures
from typing import Callable

from loguru import logger

executor = futures.ThreadPoolExecutor()


def submit(task: Callable, *args, **kwargs):
    executor.submit(task, *args, **kwargs)
    logger.info('submited task: {}', task)
