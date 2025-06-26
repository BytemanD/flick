import webview
from loguru import logger


def create_and_start_window(app, http_port=5000, width=1480, height=1000, debug: bool=False):
    logger.info("create webview window")
    webview.create_window("Flick", app, http_port=http_port,
                          width=width, height=height) # type: ignore
    logger.info("start webview")
    webview.start(debug=debug)
