#state.py
from enum import Enum
from typing import Optional

class ConnectionState(Enum):
    DISCONNECTED = "DISCONNECTED"
    CONNECTING = "CONNECTING"
    AUTHENTICATING = "AUTHENTICATING"
    AUTHENTICATED = "AUTHENTICATED"
    ERROR = "ERROR"

class StateManager:
    def __init__(self):
        self.state = ConnectionState.DISCONNECTED
        self.error_message: Optional[str] = None

    def transition_to(self, new_state: ConnectionState, error_msg: str = None) -> bool:
        """
        Attempt to transition to a new state.
        Returns True if transition is valid and successful.
        """
        valid_transitions = {
            ConnectionState.DISCONNECTED: [ConnectionState.CONNECTING],
            ConnectionState.CONNECTING: [ConnectionState.AUTHENTICATING, ConnectionState.ERROR],
            ConnectionState.AUTHENTICATING: [ConnectionState.AUTHENTICATED, ConnectionState.ERROR],
            ConnectionState.AUTHENTICATED: [ConnectionState.DISCONNECTED, ConnectionState.ERROR],
            ConnectionState.ERROR: [ConnectionState.DISCONNECTED]
        }

        if new_state in valid_transitions[self.state]:
            self.state = new_state
            self.error_message = error_msg if new_state == ConnectionState.ERROR else None
            return True
        return False

    @property
    def current_state(self) -> ConnectionState:
        return self.state

    @property
    def is_connected(self) -> bool:
        return self.state in [ConnectionState.AUTHENTICATED]

    @property
    def has_error(self) -> bool:
        return self.state == ConnectionState.ERROR