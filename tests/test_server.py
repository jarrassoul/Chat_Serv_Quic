import pytest
from src.server.server_state import ServerStateManager, ClientInfo
from src.protocol.states import StateManager

class MockProtocol:
    """Mock protocol class for testing"""
    def __init__(self):
        self.messages = []
        
    async def async_send(self, *args, **kwargs):
        self.messages.append((args, kwargs))

def test_server_state_manager():
    """Test server state management"""
    ssm = ServerStateManager()
    
    # Test client registration
    mock_protocol = MockProtocol()
    ssm.add_client("testuser", mock_protocol)
    
    assert "testuser" in ssm.clients
    assert ssm.is_client_online("testuser")
    assert len(ssm.get_online_users()) == 1
    
    # Test client removal
    ssm.remove_client("testuser")
    assert "testuser" not in ssm.clients
    assert not ssm.is_client_online("testuser")
    assert len(ssm.get_online_users()) == 0
    
    # Test token update
    ssm.add_client("testuser", mock_protocol)
    ssm.update_client_token("testuser", "test-token")
    assert ssm.get_client("testuser").token == "test-token"