import logging
from typing import Any

LOGGING_FORMAT = "%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s"
LOGGING_LEVEL = "INFO"


class Singleton(type):
    """
    Singleton metaclass
    """

    _instances: Any = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(
                Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class Logger(object, metaclass=Singleton):
    # __metaclass__ = SingletonType   # python 2 Style
    """
    Logger is the parent class of all the logger
    """
    _logger = None

    def __init__(self):
        self._logger = logging.getLogger("_logger")
        self._logger.setLevel(LOGGING_LEVEL)
        formatter = logging.Formatter(LOGGING_FORMAT)

        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)
        self._logger.addHandler(stream_handler)

    def get_logger(self):
        return self._logger
