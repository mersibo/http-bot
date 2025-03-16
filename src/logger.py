import logging
from loguru import logger

logging.getLogger().handlers = []

logger.add("logs/bot.log", format="{time} {level} {message}", level="INFO", rotation="10 MB")

def get_logger():
    return logger
