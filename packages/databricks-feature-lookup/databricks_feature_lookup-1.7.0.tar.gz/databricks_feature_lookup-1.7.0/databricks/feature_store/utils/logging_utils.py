import logging


def get_logger(name: str, log_level: int = logging.WARNING) -> logging.Logger:
    logger = logging.getLogger(name)
    # A handler needs to be created to config the current logger.
    handler = logging.StreamHandler()
    formatter = logging.Formatter("%(levelname)s %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(log_level)
    return logger
