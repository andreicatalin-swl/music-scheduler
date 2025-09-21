from wakepy import keep
from musicscheduler.utils.logger import get_logger
from logging import INFO, DEBUG

LOGGING_CONSOLE_HANDLER_THRESHOLD_LEVEL = INFO
LOGGING_FILE_HANDLER_THRESHOLD_LEVEL = DEBUG
LOGGER = get_logger(__name__, LOGGING_CONSOLE_HANDLER_THRESHOLD_LEVEL, LOGGING_FILE_HANDLER_THRESHOLD_LEVEL)

_keeper = None

def prevent_sleep() -> None:
    global _keeper
    if _keeper is None:
        _keeper = keep.running()
        _keeper.__enter__()
    else:
        message = f'prevent_sleep() called, but sleep prevention is already active.'
        LOGGER.error(message)
        raise RuntimeError(message)

def allow_sleep() -> None:
    global _keeper
    if _keeper is not None:
        _keeper.__exit__(None, None, None)
        _keeper = None
    else:
        message = f'allow_sleep() called, but sleep prevention is not active.'
        LOGGER.error(message)
        raise RuntimeError(message)

def main() -> None:
    pass

if __name__ == '__main__':
    main()
