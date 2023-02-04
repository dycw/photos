from sys import stdout

from loguru import logger

logger.remove()
_ = logger.add(stdout, format="{time:HH:mm:ss}: {message}")

__version__ = "0.1.2"
