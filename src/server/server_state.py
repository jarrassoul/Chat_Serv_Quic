#server_state.py
from dataclasses import dataclass
from typing import Dict, Optional
from src.protocol.states import StateManager, ConnectionState

@dataclass
class ClientInfo:
    username: str
    protocol: 'ChatProtocol'
    state: StateManager
    token: Optional[str] = None

class ServerStateManager:
    def __init__(self):
        self.clients: Dict[str, ClientInfo] = {}
        self.state_manager = StateManager()

    def add_client(self, username: str, protocol: 'ChatProtocol') -> None:
        """Register a new client connection"""
        if username not in self.clients:
            self.clients[username] = ClientInfo(
                username=username,
                protocol=protocol,
                state=StateManager()
            )
            self.clients[username].state.transition_to(ConnectionState.AUTHENTICATED)

    def remove_client(self, username: str) -> None:
        """Remove a client connection"""
        if username in self.clients:
            del self.clients[username]

    def get_client(self, username: str) -> Optional[ClientInfo]:
        """Get client information"""
        return self.clients.get(username)

    def get_online_users(self) -> list:
        """Get list of online users"""
        return list(self.clients.keys())

    def is_client_online(self, username: str) -> bool:
        """Check if a client is online"""
        return username in self.clients

    def update_client_token(self, username: str, token: str) -> None:
        """Update client's authentication token"""
        if username in self.clients:
            self.clients[username].token = token