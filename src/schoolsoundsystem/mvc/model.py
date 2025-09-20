from typing import Callable
from schoolsoundsystem.player.player import Player
from schoolsoundsystem.utils.logger import get_logger
from logging import INFO, DEBUG

from schoolsoundsystem.utils.queueing import Queueing

LOGGING_CONSOLE_HANDLER_THRESHOLD_LEVEL = INFO
LOGGING_FILE_HANDLER_THRESHOLD_LEVEL = DEBUG
LOGGER = get_logger(__name__, LOGGING_CONSOLE_HANDLER_THRESHOLD_LEVEL, LOGGING_FILE_HANDLER_THRESHOLD_LEVEL)

class Model:
    def __init__(self) -> None:
        self._player: Player = Player()
        self._queueing: Queueing = Queueing()

    def toggle_activation(self, on_success: Callable[[], None], on_failure: Callable[[Exception], None]) -> None:
        # Define task
        def function():
            try:
                active = self._player.is_active()
                if active:
                    self._player.deactivate()
                else:
                    self._player.activate()
            except Exception as e:
                on_failure(e)
                return
            on_success()

        self._queueing.add(function)

    def set_scheduler_directory(self, directory: str, on_success: Callable[[], None], on_failure: Callable[[Exception], None]) -> None:
        # Define task
        def function():
            try:
                self._player.set_scheduler_directory(directory)
            except Exception as e:
                on_failure(e)
                return
            on_success()
        
        self._queueing.add(function)

    def set_playlist_directory(self, directory: str, on_success: Callable[[], None], on_failure: Callable[[Exception], None]) -> None:
        # Define task
        def function():
            try:
                self._player.set_playlist_directory(directory)
            except Exception as e:
                on_failure(e)
                return
            on_success()
        
        self._queueing.add(function)

    def toggle_playlist_shuffle(self, on_success: Callable[[], None], on_failure: Callable[[Exception], None]) -> None:
        # Define task
        def function():
            try:
                shuffle = not self._player.get_playlist_shuffle()
                self._player.set_playlist_shuffle(shuffle)
            except Exception as e:
                on_failure(e)
                return
            on_success()

        self._queueing.add(function)
    
    def get_is_active(self, on_success: Callable[[bool], None], on_failure: Callable[[Exception], None]) -> None:
        # Define task
        def function():
            try:
                is_active = self._player.is_active()
            except Exception as e:
                on_failure(e)
                return
            on_success(is_active)

        self._queueing.add(function)

    def get_scheduler_directory(self, on_success: Callable[[str], None], on_failure: Callable[[Exception], None]) -> None:
        # Define task
        def function():
            try:
                directory = self._player.get_scheduler_directory()
            except Exception as e:
                on_failure(e)
                return
            on_success(directory)

        self._queueing.add(function)
    
    def get_playlist_directory(self, on_success: Callable[[str], None], on_failure: Callable[[Exception], None]) -> None:
        # Define task
        def function():
            try:
                directory = self._player.get_playlist_directory()
            except Exception as e:
                on_failure(e)
                return
            on_success(directory)

        self._queueing.add(function)
    
    def get_is_playlist_shuffle(self, on_success: Callable[[bool], None], on_failure: Callable[[Exception], None]) -> None:
        # Define task
        def function():
            try:
                shuffle = self._player.get_playlist_shuffle()
            except Exception as e:
                on_failure(e)
                return
            on_success(shuffle)

        self._queueing.add(function)
    
def main() -> None:
    pass

if __name__ == '__main__':
    main()
