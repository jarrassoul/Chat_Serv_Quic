from dataclasses import dataclass
from typing import Optional
from src.protocol.states import StateManager, ConnectionState

@dataclass
class ClientConfig:
    username: str
    token: Optional[str] = None
    last_message: Optional[str] = None

class ClientStateManager:
    def __init__(self):
        self.state_manager = StateManager()
        self.config = ClientConfig(username="")
        
    def set_username(self, username: str):
        self.config.username = username
        
    def set_token(self, token: str):
        self.config.token = token
        
    def set_last_message(self, message: str):
        self.config.last_message = message
        
    def transition_to(self, state: ConnectionState, error_msg: str = None) -> bool:
        return self.state_manager.transition_to(state, error_msg)
    
    @property
    def is_authenticated(self) -> bool:
        return self.state_manager.current_state == ConnectionState.AUTHENTICATED
    
    @property
    def current_state(self) -> ConnectionState:
        return self.state_manager.current_state