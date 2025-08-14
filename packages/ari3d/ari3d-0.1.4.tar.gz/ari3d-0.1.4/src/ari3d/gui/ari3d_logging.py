"""Logging module."""

import logging
import sys
import time
from pathlib import Path
from ari3d import __version__ as ari3d_version

LOGGER_NAME = "ARI3D"

CALL_TIME = None


def get_log_file_prefix() -> str:
    """Get the time when the program was called.

    Returns:
        Time when the program was called.

    """
    global CALL_TIME

    if not CALL_TIME:
        CALL_TIME = time.strftime("%Y%m%d_%H-%M-%S")

    call_time = CALL_TIME

    return "run_%s" % call_time

def get_logger():
    """Get the logger."""
    return logging.getLogger(LOGGER_NAME)  # root logger


def configure_logger(loglevel="INFO", logfile_name=None, formatter_string=None):
    """Configure the logger with the given parameters."""
    logger = logging.getLogger(LOGGER_NAME)
    logger.setLevel(loglevel)

    # create formatter
    if not formatter_string:
        formatter = get_default_formatter()
    else:
        formatter = logging.Formatter(formatter_string)

    ch = logging.StreamHandler(stream=sys.stdout)
    ch.setLevel(loglevel)
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    if logfile_name:
        ch = logging.FileHandler(logfile_name, mode="a", encoding=None, delay=False)
        ch.setLevel(loglevel)
        ch.setFormatter(formatter)
        logger.addHandler(ch)

    return logger


def close_logger():
    """Close the logger."""
    for h in logging.getLogger(LOGGER_NAME).handlers:
        if isinstance(h, logging.FileHandler):
            h.close()
    logging.getLogger(LOGGER_NAME).handlers.clear()


def get_default_formatter():
    """Get the default formatter."""
    return logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s", datefmt="%H:%M:%S"
    )


class Ari3dLogger:
    """Ari3d logger class."""

    _instance = None

    def __new__(cls, *args, **kwargs):
        """Singleton pattern to ensure only one instance of the logger exists."""
        if not cls._instance:
            cls._instance = super().__new__(cls)
            cls._instance._initialize(*args, **kwargs)
        return cls._instance

    def _initialize(self, loglevel="INFO", formatter_string=None):
        """Initialize the logger with the given parameters."""
        base_log_path = Path.home().joinpath(".ari3d")
        base_log_path.mkdir(parents=True, exist_ok=True)

        self.log_file_path = base_log_path.joinpath("ari3d_" + get_log_file_prefix() + ".log")
        self.log = configure_logger(loglevel, self.log_file_path, formatter_string)

        # print version information
        self.log.info("ARI3D version: %s", ari3d_version)

    def set_log_level_info(self):
        """Set the loglevel to INFO."""
        self.log.info("Set loglevel to INFO...")
        self.set_log_level(logging.INFO)

    def set_log_level_debug(self):
        """Set the loglevel to DEBUG."""
        self.log.info("Set loglevel to DEBUG...")
        self.set_log_level(logging.DEBUG)

    def set_log_level_warning(self):
        """Set the loglevel to WARNING."""
        self.log.info("Set loglevel to WARNING...")
        self.set_log_level(logging.WARNING)

    def set_log_level_none(self):
        """Disable logging."""
        self.log.info("Disable logging...")
        self.log.disabled = True

    def set_log_level(self, loglevel):
        """Set the loglevel."""
        self.log.setLevel(loglevel)
        for handler in self.log.handlers:
            handler.setLevel(loglevel)

    def __del__(self):
        """Close the logger when object gets deleted."""
        close_logger()
