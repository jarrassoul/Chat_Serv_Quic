import pytest
from src.client.client_state import ClientStateManager, ConnectionState

def test_client_state_manager():
    """Test client state management"""
    csm = ClientStateManager()
    
    # Test initial state
    assert csm.current_state == ConnectionState.DISCONNECTED
    assert not csm.is_authenticated
    
    # Test username setting
    csm.set_username("testuser")
    assert csm.config.username == "testuser"
    
    # Test token setting
    csm.set_token("test-token")
    assert csm.config.token == "test-token"
    
    # Test state transitions
    assert csm.transition_to(ConnectionState.CONNECTING)
    assert csm.transition_to(ConnectionState.AUTHENTICATING)
    assert csm.transition_to(ConnectionState.AUTHENTICATED)
    assert csm.is_authenticated