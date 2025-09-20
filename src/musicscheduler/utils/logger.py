import os
import sys
import logging
from concurrent_log_handler import ConcurrentRotatingFileHandler
from typing import Optional
from appdirs import user_data_dir
from musicscheduler.__about__ import __app_name__, __author__

LOGGING_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
LOGGING_FORMATTER = logging.Formatter(LOGGING_FORMAT)
LOGGING_FILE_HANDLER_MAX_BYTES = 1_000_000
LOGGING_FILE_HANDLER_BACKUP_COUNT = 3
LOGGING_FILE_HANDLER_FOLDER_NAME = 'logs'
LOGGING_FILE_HANDLER_FILE_NAME = 'logs.log'
LOGGING_DEFAULT_THRESHOLD_LEVEL = logging.DEBUG
LOGGING_CONSOLE_HANDLER_THRESHOLD_LEVEL = logging.INFO
LOGGING_FILE_HANDLER_THRESHOLD_LEVEL = logging.DEBUG

def get_logger(name: str, console_handler_threshold_level: Optional[int] = None, file_handler_threshold_level: Optional[int] = None) -> logging.Logger:
    logger = logging.getLogger(name)

    if not logger.handlers:
        # Set default threshold level
        logger.setLevel(LOGGING_DEFAULT_THRESHOLD_LEVEL)

        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(LOGGING_FORMATTER)
        logger.addHandler(console_handler)
        # Set console handler threshold level
        console_handler.setLevel(console_handler_threshold_level if console_handler_threshold_level is not None else LOGGING_CONSOLE_HANDLER_THRESHOLD_LEVEL)

        # Determine a safe base directory to write in
        base_dir = user_data_dir(__app_name__, appauthor=__author__)
        os.makedirs(base_dir, exist_ok=True)
        log_dir = os.path.join(base_dir, LOGGING_FILE_HANDLER_FOLDER_NAME)
        os.makedirs(log_dir, exist_ok=True)
        log_file = os.path.join(log_dir, LOGGING_FILE_HANDLER_FILE_NAME)

        # Rotating file handler
        file_handler = ConcurrentRotatingFileHandler(log_file, maxBytes=LOGGING_FILE_HANDLER_MAX_BYTES, backupCount=LOGGING_FILE_HANDLER_BACKUP_COUNT)
        file_handler.setFormatter(LOGGING_FORMATTER)
        logger.addHandler(file_handler)
        # Set file handler threshold level
        file_handler.setLevel(file_handler_threshold_level if file_handler_threshold_level is not None else LOGGING_FILE_HANDLER_THRESHOLD_LEVEL)
    elif console_handler_threshold_level is not None or file_handler_threshold_level is not None:
        message = f'Logger {name} is already initialized. Re-initialization is skipped and provided parameters are ignored.'
        logger.warning(message)
    else:
        message = f'Logger {name} is already initialized. Re-initialization is skipped.'
        logger.debug(message)

    return logger

def main() -> None:
    pass

if __name__ == '__main__':
    main()
