import sys

from loguru import logger

LOG_FORMAT_DEFAULT = (
    "<level>{time:YYYY-MM-DD HH:mm:ss} {level: <7} [{extra[session]}] {name} " "{message}</level>"
)

def setup_logger(level="INFO", file=None, log_format=None):
    """Setup logging configuration."""
    logger.remove()
    logger.add(
        file if file else sys.stdout,
        level=level,
        format=log_format or LOG_FORMAT_DEFAULT,
    )
    logger.configure(extra={"session": "-"})
