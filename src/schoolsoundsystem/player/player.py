from schoolsoundsystem.player.playlist import Playlist
from schoolsoundsystem.player.scheduler import Scheduler
from schoolsoundsystem.player.state import State
from schoolsoundsystem.player.state_machine import StateMachine
from schoolsoundsystem.utils.logger import get_logger
from logging import INFO, DEBUG

from schoolsoundsystem.utils.queueing import Queueing

LOGGING_CONSOLE_HANDLER_THRESHOLD_LEVEL = INFO
LOGGING_FILE_HANDLER_THRESHOLD_LEVEL = DEBUG
LOGGER = get_logger(__name__, LOGGING_CONSOLE_HANDLER_THRESHOLD_LEVEL, LOGGING_FILE_HANDLER_THRESHOLD_LEVEL)

class Player(StateMachine):
    _TRANSITIONS: dict[tuple[State, str], State] = dict(StateMachine._TRANSITIONS)
    _TRANSITIONS.update({
        (State.INACTIVE, 'set_scheduler_directory'): State.INACTIVE,
        (State.INACTIVE, 'set_playlist_directory'): State.INACTIVE,
        (State.INACTIVE, 'set_playlist_shuffle'): State.INACTIVE
    })

    def __init__(self) -> None:
        super().__init__()
        
        self._scheduler: Scheduler = Scheduler()
        self._playlist: Playlist = Playlist()

        self._queueing: Queueing = Queueing()

        self._scheduler.set_on_start(self._on_start)
        self._scheduler.set_on_end(self._on_end)

    def get_scheduler_directory(self) -> str:
        return self._scheduler.get_directory()

    def get_playlist_directory(self) -> str:
        return self._playlist.get_directory()
    
    def get_playlist_shuffle(self) -> bool:
        return self._playlist.get_shuffle()
    
    def set_scheduler_directory(self, directory: str) -> None:
        method = self.set_scheduler_directory
        self._transition(method)

        self._scheduler.set_directory(directory)
    
    def set_playlist_directory(self, directory: str) -> None:
        method = self.set_playlist_directory
        self._transition(method)

        self._playlist.set_directory(directory)
    
    def set_playlist_shuffle(self, shuffle: bool) -> None:
        method = self.set_playlist_shuffle
        self._transition(method)

        self._playlist.set_shuffle(shuffle)

    def is_active(self) -> bool:
        return self._state == State.ACTIVE
 
    def _on_start(self) -> None:
        # Define on success callback
        def on_success():
            message = f'Function execution successful.'
            LOGGER.debug(message)
        # Define on failure callback
        def on_failure(e):
            message = f'Function execution failed: \'{e}\'.'
            LOGGER.warning(message)
        # Define task
        def function():
            try:
                self._playlist.activate()
            except Exception as e:
                on_failure(e)
                return
            on_success()
                
        self._queueing.add(function)

    def _on_end(self) -> None:
        # Define on success callback
        def on_success():
            message = f'Function execution successful.'
            LOGGER.debug(message)
        # Define on failure callback
        def on_failure(e):
            message = f'Function execution failed: \'{e}\'.'
            LOGGER.warning(message)
        # Define task
        def function():
            try:
                if self._playlist.is_active():
                    self._playlist.deactivate()
                else:
                    message = 'Playlist is not in State.ACTIVE, no tracks are playing.'
                    LOGGER.debug(message)
            except Exception as e:
                on_failure(e)
                return
            on_success()

        self._queueing.add(function)

    def activate(self) -> None:
        super().activate()

        self._scheduler.activate()

    def deactivate(self) -> None:
        super().deactivate()

        self._scheduler.deactivate()
        # Playlist may already not be in State.ACTIVE if no track is playing
        if self._playlist.is_active():
            self._playlist.deactivate()
        else:
            message = 'Playlist is not in State.ACTIVE, no tracks are playing.'
            LOGGER.debug(message)

    def shutdown(self) -> None:
        super().shutdown()

        self._scheduler.shutdown()
        self._playlist.shutdown()
        self._queueing.shutdown()

def main() -> None:
    pass

if __name__ == '__main__':
    main()
