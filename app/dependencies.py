import jwt
from fastapi import Request, HTTPException, Depends
from sqlmodel import Session
from uuid import UUID
from .database import get_session
from .models import User
from .auth import SECRET_KEY, ALGORITHM
from .redis_client import sync_redis
def get_current_user(
    request: Request, # NEW: Grab the raw request to access cookies
    session: Session = Depends(get_session)
) -> User:
    # --- NEW: Extract token from the cookie instead of the header ---
    token_cookie = request.cookies.get("access_token")
    
    if not token_cookie or not token_cookie.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    token = token_cookie.split(" ")[1]
    if sync_redis.exists(f"blacklist:{token}"):
        raise HTTPException(status_code=401, detail="Session has been revoked. Please log in again.")
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id_str = payload.get("sub")
        
        if user_id_str is None:
            raise HTTPException(status_code=401, detail="Token missing subject claim")
            
        user = session.get(User, UUID(user_id_str))
        if not user:
            raise HTTPException(status_code=401, detail="User no longer exists")
            
        return user
        
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token signature")


