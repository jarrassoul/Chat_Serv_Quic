import pytest
from src.protocol import Message, MsgType, pack, unpack
from src.protocol.auth import AuthManager
from src.protocol.states import StateManager, ConnectionState

def test_message_packing():
    """Test message serialization and deserialization"""
    original_msg = {
        "v": 1,
        "t": MsgType.CHAT,
        "body": "Hello, World!",
        "to": None,
        "token": "test-token"
    }
    
    packed = pack(original_msg)
    unpacked = unpack(packed)
    
    assert isinstance(packed, bytes)
    assert unpacked == original_msg

def test_auth_manager():
    """Test authentication manager functionality"""
    auth = AuthManager(secret_key="test-key")
    
    # Test registration
    assert auth.register("testuser", "password")
    assert not auth.register("testuser", "password")  # Duplicate registration
    
    # Test verification
    assert auth.verify("testuser", "password")
    assert not auth.verify("testuser", "wrong-password")
    assert not auth.verify("nonexistent", "password")
    
    # Test token operations
    token = auth.issue_token("testuser")
    assert isinstance(token, str)
    
    username = auth.validate_token(token)
    assert username == "testuser"
    
    assert auth.validate_token("invalid-token") is None

def test_state_manager():
    """Test state management functionality"""
    sm = StateManager()
    
    # Test initial state
    assert sm.current_state == ConnectionState.DISCONNECTED
    
    # Test valid transitions
    assert sm.transition_to(ConnectionState.CONNECTING)
    assert sm.transition_to(ConnectionState.AUTHENTICATING)
    assert sm.transition_to(ConnectionState.AUTHENTICATED)
    
    # Test invalid transition
    assert not sm.transition_to(ConnectionState.CONNECTING)
    
    # Test error state
    assert sm.transition_to(ConnectionState.ERROR, "Test error")
    assert sm.has_error