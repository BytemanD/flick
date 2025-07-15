import logging
import sys

from loguru import logger

from flick.common import context

LOG_FORMAT_DEFAULT = (
    "<level>{time:YYYY-MM-DD HH:mm:ss} {level: <7} [{extra[sid]} {extra[req_id]}] {name}:{line} | "
    "{message}</level>"
)


def context_patcher(record):
    record["extra"]["sid"] = context.get_session_id() or "-"
    record["extra"]["req_id"] = context.get_request_id() or "-"


def setup_logger(level="INFO", file=None, log_format=None):
    """Setup logging configuration."""
    logger.remove()
    logger.add(
        file if file else sys.stdout,
        level=level,
        format=log_format or LOG_FORMAT_DEFAULT,
    )
    logger.configure(extra={"req_id": "-", "sid": "-"}, patcher=context_patcher)


def monkey_patch_logging():
    logging.getLogger = lambda x: logger
