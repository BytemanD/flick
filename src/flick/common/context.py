import contextvars
from functools import wraps
from typing import Callable

session_id = contextvars.ContextVar("session_id", default="")
request_id = contextvars.ContextVar("request_id", default="")


def update(sid=None, req_id=None):
    if sid:
        session_id.set(sid)
    if req_id:
        request_id.set(req_id)


def get_session_id() -> str:
    return session_id.get()


def get_request_id() -> str:
    return request_id.get()


def apply_context(ctx: contextvars.Context):
    update(sid=ctx.get(session_id), req_id=ctx.get(request_id))


def with_context(f):
    @wraps(f)
    def wrapper(self, *args, **kwargs):
        ctx = contextvars.copy_context()
        return ctx.run(lambda: f(self, *args, **kwargs))

    return wrapper


def preserve_context_and_run_on_executor(f) -> Callable:
    """组合装饰器：同时处理上下文保存和线程执行"""
    @wraps(f)
    async def async_wrapper(self, *args, **kwargs):
        # 异步部分：保存当前上下文
        ctx = contextvars.copy_context()
        # 将函数调用转移到线程池执行，并保持上下文
        return await self.run_on_executor(
            lambda: ctx.run(lambda: f(self, *args, **kwargs))
        )
    return async_wrapper
