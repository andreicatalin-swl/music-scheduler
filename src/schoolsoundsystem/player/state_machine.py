from typing import Any, Callable
from schoolsoundsystem.player.state import State
from schoolsoundsystem.utils.logger import get_logger
from logging import INFO, DEBUG

LOGGING_CONSOLE_HANDLER_THRESHOLD_LEVEL = INFO
LOGGING_FILE_HANDLER_THRESHOLD_LEVEL = DEBUG
LOGGER = get_logger(__name__, LOGGING_CONSOLE_HANDLER_THRESHOLD_LEVEL, LOGGING_FILE_HANDLER_THRESHOLD_LEVEL)

class InvalidTransitionError(Exception):
    pass

class StateMachine():
    _TRANSITIONS: dict[tuple[State, str], State] = {
        (State.INACTIVE, 'activate'): State.ACTIVE,
        (State.ACTIVE, 'deactivate'): State.INACTIVE,
        (State.INACTIVE, 'shutdown'): State.SHUTDOWN
    }

    def __init__(self) -> None:
        self._state: State = State.INACTIVE

    def activate(self) -> None:
        method = self.activate
        self._transition(method)

    def deactivate(self) -> None:
        method = self.deactivate
        self._transition(method)

    def shutdown(self) -> None:
        method = self.shutdown
        self._transition(method)

    def _transition(self, method: Callable[..., Any]) -> None:
        # Attempt to get the name of the called method
        method_name = getattr(method, '__name__', None)
        if not method_name:
            message = f'Cannot determine method name for Callable[..., Any] {method_name}.'
            LOGGER.warning(message)
            method_name = '<unknown>'

        current_state = self._state
        key = (current_state, method_name)
        # Attempt to get next state which follows from transition (current_state, method_name)
        next_state = self._TRANSITIONS.get(key)
        # If the transtion is valid, update the state
        if next_state:
            self._state = next_state
            message = f'State of {self} changed to {type(self._state).__name__}.{self._state.name} with method {method_name}.'
            LOGGER.debug(message)
        # If the transition is invalid, raise an InvalidTransitionError
        else:
            message = f'Cannot run method {method_name} while {self} is in state {type(self._state).__name__}.{self._state.name}.'
            LOGGER.error(message)
            raise InvalidTransitionError(message)

def main() -> None:
    pass

if __name__ == '__main__':
    main()
