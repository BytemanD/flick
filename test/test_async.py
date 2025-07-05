import asyncio
from typing import Callable
import time

from concurrent import futures

executor = futures.ThreadPoolExecutor()


def start_task(task: Callable, *args, **kwargs):
    executor.submit(task, *args, **kwargs)


def task1():
    print("task1 start")
    time.sleep(1)
    print("task1 done")


def task2():
    print("task2 start")
    time.sleep(1)
    print("task2 done")


print("start tasks")
start_task(task1)
start_task(task2)

print("all done")

time.sleep(3)
