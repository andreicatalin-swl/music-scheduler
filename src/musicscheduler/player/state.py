from enum import Enum, auto
from musicscheduler.utils.logger import get_logger
from logging import INFO, DEBUG

LOGGING_CONSOLE_HANDLER_THRESHOLD_LEVEL = INFO
LOGGING_FILE_HANDLER_THRESHOLD_LEVEL = DEBUG
LOGGER = get_logger(__name__, LOGGING_CONSOLE_HANDLER_THRESHOLD_LEVEL, LOGGING_FILE_HANDLER_THRESHOLD_LEVEL)

class State(Enum):
    INACTIVE: 'State' = auto()
    ACTIVE: 'State' = auto()
    SHUTDOWN: 'State' = auto()

def main() -> None:
    pass

if __name__ == '__main__':
    main()
