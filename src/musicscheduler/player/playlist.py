import os
import random
import threading
import pygame
from typing import ClassVar, Optional
from musicscheduler.player.state import State
from musicscheduler.player.state_machine import StateMachine
from musicscheduler.utils.cache import Cache
from musicscheduler.utils.logger import get_logger
from logging import INFO, DEBUG

LOGGING_CONSOLE_HANDLER_THRESHOLD_LEVEL = INFO
LOGGING_FILE_HANDLER_THRESHOLD_LEVEL = DEBUG
LOGGER = get_logger(__name__, LOGGING_CONSOLE_HANDLER_THRESHOLD_LEVEL, LOGGING_FILE_HANDLER_THRESHOLD_LEVEL)

class Playlist(StateMachine):
    _TRANSITIONS: dict[tuple[State, str], State] = dict(StateMachine._TRANSITIONS)
    _TRANSITIONS.update({
        (State.INACTIVE, 'set_directory'): State.INACTIVE,
        (State.INACTIVE, 'set_shuffle'): State.INACTIVE
    })

    _DEFAULT_DIRECTORY: ClassVar[str] = ''
    _DEFAULT_SHUFFLE: ClassVar[bool] = False
    # The fade out blocks the thread until it is complete. A value higher than 1000 (ms) may cause delays in the queue if intervals are close together. It is recommended that this value is not greater than the minimum gap in allowed between intervals.
    _DEFAULT_FADE_OUT_DURATION: ClassVar[int] = 1000
    
    _VALID_EXTENSIONS: tuple[str, ...] = ('.mp3', '.wav')
    _UPDATE_RATE: int = 10

    _PLAYLIST_DIRECTORY_CACHE_KEY: ClassVar[str] = 'playlist_directory'
    _PLAYLIST_SHUFFLE_CACHE_KEY: ClassVar[str] = 'playlist_shuffle'

    def __init__(self, directory: str = _DEFAULT_DIRECTORY, shuffle: bool = _DEFAULT_SHUFFLE, fade_out_duration: int = _DEFAULT_FADE_OUT_DURATION) -> None:
        super().__init__()

        self._directory: str = directory
        self._shuffle: bool = shuffle
        self._fade_out_duration: int = fade_out_duration

        self._cache: Cache = Cache()
        self._worker: Optional[threading.Thread] = None
        self._tracks: list[str] = []
        pygame.mixer.init()

    def get_directory(self) -> str:
        return self._directory
    
    def get_shuffle(self) -> bool:
        return self._shuffle
    
    def set_directory(self, directory: str) -> None:
        method = self.set_directory
        self._transition(method)

        self._directory = directory
        # Save to cache
        self._cache[self._PLAYLIST_DIRECTORY_CACHE_KEY] = directory
        # Reset tracks queue
        self._tracks = []

    def set_shuffle(self, shuffle: bool) -> None:
        method = self.set_shuffle
        self._transition(method)

        # Save to cache
        self._cache[self._PLAYLIST_SHUFFLE_CACHE_KEY] = shuffle
        self._shuffle = shuffle

    def is_active(self) -> bool:
        return self._state == State.ACTIVE

    def activate(self) -> None:
        super().activate()

        def playback():
            def get_tracks():
                exists = os.path.exists(self._directory)
                # If directory is not valid, do not add any tracks
                if not exists:
                    return []
            
                # Get path for every music file (extensions supported in self._VALID_EXTENSIONS) from directory
                tracks = [os.path.join(self._directory, file) for file in os.listdir(self._directory) if file.lower().endswith(self._VALID_EXTENSIONS)]

                if self._shuffle:
                    random.shuffle(tracks)

                return tracks
            
            clock = pygame.time.Clock()
            # Keep running while state is not set to State.INACTIVE
            while self._state != State.INACTIVE:
                # If there are no tracks in the queue, get tracks from get_tracks()
                if not self._tracks:
                    self._tracks = get_tracks()
                    # If get_tracks() doesn't return any tracks, continue
                    if not self._tracks:
                        clock.tick(self._UPDATE_RATE)
                        continue
                
                # Start playing next track in queue
                track = self._tracks.pop(0)
                pygame.mixer.music.load(track)
                pygame.mixer.music.play()

                message = f'Playing track {track}.'
                LOGGER.debug(message)

                # Wait for track to end before moving to the next one
                while pygame.mixer.music.get_busy():
                    clock.tick(self._UPDATE_RATE)
                    # If state is set to State.INACTIVE, exit the loop
                    if self._state == State.INACTIVE:
                        break

        if self._worker is not None:
            message = f'Cannot active worker thread: worker thread already has a reference to another object.'
            LOGGER.error(message)
            raise RuntimeError(message)
        else:
            # Initialize worker thread to play tracks
            self._worker = threading.Thread(target=playback, daemon=True)
            # Start worker thread
            self._worker.start()
        
    def deactivate(self, fade_out: bool) -> None:
        super().deactivate()

        if self._worker is None:
            message = f'Cannot deactivate worker thread: worker thread does not exist.'
            LOGGER.debug(message)
        elif not self._worker.is_alive():
            message = f'Cannot deactivate worker thread: worker thread exists but is not running.'
            LOGGER.debug(message)
        else:
            # Freeze current thread until worker thread and current thread are joined together
            self._worker.join()

        # Release the reference to the current worker thread
        self._worker = None

        if not pygame.mixer.music.get_busy():
            message = f'Cannot stop current track: no track is playing.'
            LOGGER.debug(message)
        else:
            if fade_out:
                # Fade out current track
                pygame.mixer.music.fadeout(self._fade_out_duration)

                # Keep thread blocked until current track fades out
                clock = pygame.time.Clock()
                while pygame.mixer.music.get_busy():
                    clock.tick(self._UPDATE_RATE)
            # Stop playing current track
            pygame.mixer.music.stop()

    def shutdown(self) -> None:
        super().shutdown()

        pygame.mixer.quit()

def main() -> None:
    pass

if __name__ == '__main__':
    main()
