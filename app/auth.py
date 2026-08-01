import jwt
from datetime import datetime, timedelta, timezone
from pwdlib import PasswordHash

# In production, NEVER hardcode this. Load it from a .env file.
SECRET_KEY = "your-super-secret-development-key-do-not-share"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Initialize Argon2 password hasher
password_hash = PasswordHash.recommended()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies that a plain text password matches the hash."""
    return password_hash.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Creates an Argon2 hash of a password."""
    return password_hash.hash(password)

def create_access_token(data: dict) -> str:
    """Encodes a payload into a secure JWT string."""
    to_encode = data.copy()
    
    # Calculate exact expiration time in UTC
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    
    # Generate the actual token string
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt