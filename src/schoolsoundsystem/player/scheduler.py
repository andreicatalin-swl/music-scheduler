import os
from datetime import datetime
from typing import Callable, ClassVar
from schoolsoundsystem.player.state import State
from schoolsoundsystem.player.state_machine import StateMachine
from apscheduler.executors.pool import ThreadPoolExecutor
from apscheduler.schedulers.background import BackgroundScheduler
from schoolsoundsystem.utils.cache import Cache
from schoolsoundsystem.utils.logger import get_logger
from logging import INFO, DEBUG

LOGGING_CONSOLE_HANDLER_THRESHOLD_LEVEL = INFO
LOGGING_FILE_HANDLER_THRESHOLD_LEVEL = DEBUG
LOGGER = get_logger(__name__, LOGGING_CONSOLE_HANDLER_THRESHOLD_LEVEL, LOGGING_FILE_HANDLER_THRESHOLD_LEVEL)

class Scheduler(StateMachine):
    _TRANSITIONS: dict[tuple[State, str], State] = StateMachine._TRANSITIONS
    _TRANSITIONS.update({
        (State.INACTIVE, 'set_directory'): State.INACTIVE,
        (State.INACTIVE, 'set_on_start'): State.INACTIVE,
        (State.INACTIVE, 'set_on_end'): State.INACTIVE,
        (State.INACTIVE, '_add_intervals'): State.INACTIVE
    })

    _DEFAULT_DIRECTORY: ClassVar[str] = ''
    def default_callback() -> None:
        message = f'Default callback invoked. No custom callback was set.'
        LOGGER.warning(message)
    _DEFAULT_ON_START: Callable[[], None] = default_callback
    _DEFAULT_ON_END: Callable[[], None] = default_callback

    _VALID_DAYS: ClassVar[tuple[str, ...]] = ('mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun')

    _SCHEDULER_DIRECTORY_CACHE_KEY: ClassVar[str] = 'scheduler_directory'

    def __init__(self, directory: str = _DEFAULT_DIRECTORY, on_start: Callable[[], None] = _DEFAULT_ON_START, on_end: Callable[[], None] = _DEFAULT_ON_END) -> None:
        super().__init__()

        self._directory: str = directory
        self._on_start: Callable[[], None] = on_start
        self._on_end: Callable[[], None] = on_end

        self._cache = Cache()

        # Only allow one job to run at a time
        executors = {'default': ThreadPoolExecutor(1)}
        job_defaults = {'max_instances': 1}

        self._background_scheduler: BackgroundScheduler = BackgroundScheduler(executors=executors, job_defaults=job_defaults)
        # Start background scheduler
        self._background_scheduler.start()
        # Prevent scheduled jobs from running until Scheduler transitions from State.INACTIVE
        self._background_scheduler.pause()
        # Add intervals from directory
        self._add_intervals()

    def get_directory(self) -> str:
        return self._directory
    
    def get_on_start(self) -> Callable[[], None]:
        return self._on_start
    
    def get_on_end(self) -> Callable[[], None]:
        return self._on_end
    
    def set_directory(self, directory: str) -> None:
        method = self.set_directory
        self._transition(method)

        self._directory = directory
        # Save to cache
        self._cache[self._SCHEDULER_DIRECTORY_CACHE_KEY] = directory

        # Remove all current intervals
        self._background_scheduler.remove_all_jobs()
        # Add intervals from directory
        self._add_intervals()

    def set_on_start(self, on_start: Callable[[], None]) -> None:
        method = self.set_on_start
        self._transition(method)

        self._on_start = on_start

    def set_on_end(self, on_end: Callable[[], None]) -> None:
        method = self.set_on_end
        self._transition(method)

        self._on_end = on_end

    def _add_intervals(self) -> None:
        method = self._add_intervals
        self._transition(method)

        def get_intervals():
            exists = os.path.exists(self._directory)
            # If directory is not valid, do not add any intervals
            if not exists:
                message = f'Directory \'{self._directory}\' does not exist. Found intervals = [].'
                LOGGER.warning(message)       
                return []

            intervals = []
            # Interval template: [start HH:MM:SS, end HH:MM:SS, day]
            with open(self._directory, 'r') as file:
                for line in file:
                    # Remove trailing empty spaces
                    line = line.strip()
                    # If line is empty, continue
                    if not line:
                        continue

                    # Remove square brackets (if present)
                    if line.startswith('[') and line.endswith(']'):
                        line = line[1:-1]
                    
                    # Split by comma
                    parts = [p.strip() for p in line.split(',')]
                    if len(parts) != 3:
                        message = f'Line has wrong format: \'{line}\'.'
                        LOGGER.error(message)
                        raise ValueError(message)

                    start_str, end_str, day_str = parts
                    # Parse times
                    start_time = datetime.strptime(start_str, "%H:%M:%S").time()
                    end_time = datetime.strptime(end_str, "%H:%M:%S").time()
                    # Normalize day to lowercase
                    day_str = day_str.lower()

                    interval = (start_time, end_time, day_str)
                    intervals.append(interval)

            return intervals
        
        intervals = get_intervals()
        for i, interval in enumerate(intervals):
            start, end, day = interval
            
            # Check if interval day is valid
            if day not in self._VALID_DAYS:
                message = f'Cannot add interval {interval} because day {day} is not valid. Valid days are {self._VALID_DAYS}. No intervals will be added.'
                LOGGER.error(message)
                raise ValueError(message)
            
            # Check if interval order is valid
            if start >= end:
                message = f'Cannot add interval {interval} because start time {(start, day)} is not before end time {(end, day)}. No intervals will be added.'
                LOGGER.error(message)
                raise ValueError(message)
            
            # Check if interval doesn't overlap with other intervals
            is_valid = True
            for existing_interval in intervals[:i]:
                existing_start, existing_end, existing_day = existing_interval
                
                if existing_interval == interval:
                    is_valid = False
                elif day == existing_day and not (end < existing_start or start > existing_end):
                    is_valid = False
                if not is_valid:
                    message = f'Cannot add interval {(start, end, day)} because it overlaps with existing interval {existing_interval}. No intervals will be added.'
                    LOGGER.error(message)
                    raise ValueError(message)
        
        # If all intervals are valid, schedule them
        for interval in intervals:
            start, end, day = interval

            # Add scheduled jobs
            self._background_scheduler.add_job(func=lambda: self._on_start(), trigger='cron', day_of_week=day, hour=start.hour, minute=start.minute, second=start.second)
            self._background_scheduler.add_job(func=lambda: self._on_end(), trigger='cron', day_of_week=day, hour=end.hour, minute=end.minute, second=end.second)

            message = f'Added interval {interval}.'
            LOGGER.debug(message)
    
    def activate(self) -> None:
        super().activate()

        self._background_scheduler.resume()

    def deactivate(self) -> None:
        super().deactivate()

        self._background_scheduler.pause()

    def shutdown(self) -> None:
        super().shutdown()

        self._background_scheduler.shutdown()
        
def main() -> None:
    pass

if __name__ == '__main__':
    main()