from typing import Any, Callable
from schoolsoundsystem.utils.logger import get_logger
from logging import INFO, DEBUG

LOGGING_CONSOLE_HANDLER_THRESHOLD_LEVEL = INFO
LOGGING_FILE_HANDLER_THRESHOLD_LEVEL = DEBUG
LOGGER = get_logger(__name__, LOGGING_CONSOLE_HANDLER_THRESHOLD_LEVEL, LOGGING_FILE_HANDLER_THRESHOLD_LEVEL)

class Task:
    def __init__(self, function: Callable[..., Any], on_success: Callable[[], Any], on_failure: Callable[[], Any]):
        self.function = function
        self.on_success = on_success
        self.on_failure = on_failure

def main() -> None:
    pass

if __name__ == '__main__':
    main()
