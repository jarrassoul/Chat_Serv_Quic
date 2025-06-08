import time
import bcrypt
from typing import Optional, Dict
from jose import jwt

class AuthManager:
    def __init__(self, secret_key: str = "your-very-secret-key"):
        # Initialize with secret key, algorithm, and token expiration time
        self._SECRET = secret_key
        self._ALGORITHM = "HS256"  # Algorithm for JWT encoding
        self._EXPIRATION = 3600  # Token expiration in seconds
        self._users: Dict[str, bytes] = {}  # Dictionary for storing username and hashed passwords

    def register(self, username: str, password: str) -> bool:
        """Register a new user"""
        # Check if username already exists
        if username in self._users:
            return False  # Registration fails if user exists
        
        # Hash the password and store it
        hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
        self._users[username] = hashed
        return True  # Registration is successful

    def verify(self, username: str, password: str) -> bool:
        """Verify user credentials"""
        # Retrieve the hashed password
        hashed = self._users.get(username)
        if not hashed:
            return False  # Return false if user is not found
        
        # Compare provided password with stored hash
        return bcrypt.checkpw(password.encode("utf-8"), hashed)

    def issue_token(self, username: str) -> str:
        """Issue a JWT token for authenticated user"""
        # Create payload with subject and expiration
        payload = {
            "sub": username,
            "exp": int(time.time()) + self._EXPIRATION  # Set token expiration
        }
        # Encode the payload to create a JWT
        return jwt.encode(payload, self._SECRET, algorithm=self._ALGORITHM)

    def validate_token(self, token: str) -> Optional[str]:
        """Validate JWT token and return username if valid"""
        try:
            # Decode the token to retrieve data
            data = jwt.decode(token, self._SECRET, algorithms=[self._ALGORITHM])
            return data.get("sub")  # Return username if token is valid
        except Exception:
            return None  # Return None if token is invalid or expired