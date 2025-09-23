from queue import Queue
import threading
from typing import Callable
from musicscheduler.utils.logger import get_logger
from logging import INFO, DEBUG

LOGGING_CONSOLE_HANDLER_THRESHOLD_LEVEL = INFO
LOGGING_FILE_HANDLER_THRESHOLD_LEVEL = DEBUG
LOGGER = get_logger(__name__, LOGGING_CONSOLE_HANDLER_THRESHOLD_LEVEL, LOGGING_FILE_HANDLER_THRESHOLD_LEVEL)

class UnexpectedOperationError(Exception):
    pass

class Queueing:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        # Prevent reinitialization
        if hasattr(self, "_initialized") and self._initialized:
            return

        # Initialize state and start worker thread
        self._running = True
        self._queue: Queue[Callable[[], None]] = Queue()
        self._worker: threading.Thread = threading.Thread(target=self._run, daemon=True)
        self._worker.start()

        # Used to prevent re-initialization
        self._initialized = True

    def add(self, function: Callable[[], None]) -> None:
        if not self._running:
            message = f'Cannot add task: {self} has already been shut down.'
            LOGGER.error(message)
            raise UnexpectedOperationError(message)
        
        if not callable(function):
            message = f'Cannot add task: {function} is not a callable.'
            LOGGER.warning(message)
        else:
            self._queue.put(function)

    def _run(self) -> None:
        while True:
            function = self._queue.get()
            if function is None:  # Sentinel to exit
                self._queue.task_done()
                break
            try:
                function()
            except Exception as e:
                message = f'Task {function} failed: \'{e}\'.'
                LOGGER.warning(message)
            finally:
                self._queue.task_done()

    def shutdown(self) -> None:
        if not self._running:
            message = f'shutdown(...) called, but {self} has already been shut down.'
            LOGGER.error(message)
            raise UnexpectedOperationError(message)
        
        self._running = False
        self._queue.put(None)
        self._worker.join()
        self._worker = None

def main() -> None:
    pass

if __name__ == '__main__':
    main()
