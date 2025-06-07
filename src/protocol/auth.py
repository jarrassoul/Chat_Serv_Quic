import time
import bcrypt
from typing import Optional, Dict
from jose import jwt

class AuthManager:
    def __init__(self, secret_key: str = "your-very-secret-key"):
        self._SECRET = secret_key
        self._ALGORITHM = "HS256"
        self._EXPIRATION = 3600  # Token expiration in seconds
        self._users: Dict[str, bytes] = {}  # username -> hashed password

    def register(self, username: str, password: str) -> bool:
        """Register a new user"""
        if username in self._users:
            return False
        hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
        self._users[username] = hashed
        return True

    def verify(self, username: str, password: str) -> bool:
        """Verify user credentials"""
        hashed = self._users.get(username)
        if not hashed:
            return False
        return bcrypt.checkpw(password.encode("utf-8"), hashed)

    def issue_token(self, username: str) -> str:
        """Issue a JWT token for authenticated user"""
        payload = {
            "sub": username,
            "exp": int(time.time()) + self._EXPIRATION
        }
        return jwt.encode(payload, self._SECRET, algorithm=self._ALGORITHM)

    def validate_token(self, token: str) -> Optional[str]:
        """Validate JWT token and return username if valid"""
        try:
            data = jwt.decode(token, self._SECRET, algorithms=[self._ALGORITHM])
            return data.get("sub")
        except Exception:
            return None