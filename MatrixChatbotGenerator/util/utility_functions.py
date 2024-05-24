import inspect
import logging
from logging.handlers import RotatingFileHandler


class CustomFormatter(logging.Formatter):
    def format(self, record):
        # Modify the original format function to replace newlines with tabs
        original = super(CustomFormatter, self).format(record)
        return original.replace('\n', '\t')


def create_logger(name):
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    # Set up a RotatingFileHandler
    handler = RotatingFileHandler(f'./data/{name}.log', maxBytes=1024 * 1024 * 5, backupCount=5)
    formatter = CustomFormatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    handler.setFormatter(formatter)

    # Add the handler to the logger
    logger.addHandler(handler)
    return logger


def current_function_name():
    return inspect.stack()[1].function


