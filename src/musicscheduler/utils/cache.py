import os
import json
from typing import Any, ClassVar
from appdirs import user_data_dir
from musicscheduler.__about__ import __app_name__, __author__
from musicscheduler.utils.logger import get_logger
from logging import INFO, DEBUG

LOGGING_CONSOLE_HANDLER_THRESHOLD_LEVEL = INFO
LOGGING_FILE_HANDLER_THRESHOLD_LEVEL = DEBUG
LOGGER = get_logger(__name__, LOGGING_CONSOLE_HANDLER_THRESHOLD_LEVEL, LOGGING_FILE_HANDLER_THRESHOLD_LEVEL)

class Cache:
    _DEFAULT_FOLDER: ClassVar[str] = 'cache'
    _DEFAULT_FILE_NAME: ClassVar[str] = 'cache.json'

    def __init__(self, folder: str = _DEFAULT_FOLDER, file_name: str = _DEFAULT_FILE_NAME) -> None:
        # Determine a safe base directory to write in/read from
        base_dir = user_data_dir(__app_name__, appauthor=__author__)
        os.makedirs(base_dir, exist_ok=True)
        cache_dir = os.path.join(base_dir, folder)
        os.makedirs(cache_dir, exist_ok=True)
        cache_file = os.path.join(cache_dir, file_name)
        
        self._cache_file: str = cache_file
        self._data: dict[str, Any] = {}
        self._load()
    
    def _load(self) -> None:
        if os.path.exists(self._cache_file):
            try:
                with open(self._cache_file, 'r') as file:
                    self._data = json.load(file)
                    message = f'Cache loaded from file {self._cache_file}.'
                    LOGGER.debug(message)
            except (json.JSONDecodeError, OSError) as e:
                message = f'Error loading cache from file {self._cache_file}: {e}'
                LOGGER.warning(message)
                self._data = {}
        else:
            message = f'Cache file {self._cache_file} does not exist. Starting with empty cache.'
            LOGGER.debug(message)
            self._data = {}

    def _store(self) -> None:
        with open(self._cache_file, 'w') as file:
            json.dump(self._data, file, indent=4)
            message = f'Cache stored to file {self._cache_file}.'
            LOGGER.debug(message)

    def set(self, key: str, value: Any) -> None:
        self._data[key] = value
        self._store()

    def __setitem__(self, key: str, value: Any) -> None:
        self.set(key, value)
    
    def get(self, key: str) -> Any:
        if key in self._data:
            return self._data[key]
        else:
            message = f'Key {key} not found in cache.'
            LOGGER.error(message)
            raise KeyError(message)
        
    def __getitem__(self, key: str) -> Any:
        return self.get(key)
        
    def delete(self, key: str) -> None:
        if key in self._data:
            del self._data[key]
            self._store()
        else:
            message = f'Key {key} not found in cache.'
            LOGGER.error(message)
            raise KeyError(message)
        
    def contains(self, key: str) -> bool:
        return key in self._data
    
    def __contains__(self, key: str) -> bool:
        return self.contains(key)
    
    def clear(self) -> None:
        self._data = {}
        self._store()

    def keys(self) -> list[str]:
        return list(self._data.keys())

def main() -> None:
    pass

if __name__ == '__main__':
    main() 
