import json
from enum import IntEnum
from typing import Dict, Any, Optional
from dataclasses import dataclass

class MsgType(IntEnum):
    AUTH_REQ = 0  # Client authentication request
    AUTH_OK = 1   # Server authentication success
    AUTH_BAD = 2  # Authentication failure
    CHAT = 3      # Chat messages
    SYS = 4       # System messages

@dataclass
class Message:
    version: int = 1
    msg_type: MsgType = MsgType.CHAT
    body: str = ""
    to: Optional[str] = None
    token: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "v": self.version,
            "t": int(self.msg_type),
            "body": self.body,
            "to": self.to,
            "token": self.token
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'Message':
        return Message(
            version=data.get("v", 1),
            msg_type=MsgType(data.get("t", MsgType.CHAT)),
            body=data.get("body", ""),
            to=data.get("to"),
            token=data.get("token")
        )

def pack(msg: Dict[str, Any]) -> bytes:
    """Serialize message to bytes"""
    return json.dumps(msg).encode("utf-8")

def unpack(data: bytes) -> Dict[str, Any]:
    """Deserialize message from bytes"""
    return json.loads(data.decode("utf-8"))