import logging

from pyaslreport.core.config import config

def get_logger(name: str):
    """
    Get a logger with the specified name, configured according to the global settings.
    If the logger already exists, it will return the existing logger.
    If it does not exist, it will create a new logger with the specified name and
    configure it based on the global configuration settings.
    Args:
        name (str): The name of the logger.
    Returns:
        logging.Logger: The configured logger instance.
    """
    log_level = config.get("log_level", "INFO").upper()
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, log_level, logging.INFO))

    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            "[%(asctime)s] %(levelname)s - %(name)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger
