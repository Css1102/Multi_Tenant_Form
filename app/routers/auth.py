from fastapi import APIRouter, Depends, HTTPException,Request,Response
from sqlmodel import Session, select
from pydantic import BaseModel
from ..database import get_session
from ..models import User
from ..auth import verify_password, create_access_token, SECRET_KEY, ALGORITHM
from slowapi import Limiter
from slowapi.util import get_remote_address
import jwt
from datetime import datetime, timezone
from ..redis_client import sync_redis  
limiter = Limiter(key_func=get_remote_address)
router = APIRouter(prefix="/auth", tags=["Authentication"])

class LoginRequest(BaseModel):
    email: str
    password: str

@router.post("/login")
@limiter.limit("5/minute") 

def login(
    request: Request,
    payload: LoginRequest, 
    response: Response, # NEW: We need the Response object to set the cookie
    session: Session = Depends(get_session)
):
    statement = select(User).where(User.email == payload.email)
    user = session.exec(statement).first()
    
    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect email or password")
    
    access_token = create_access_token(
        data={"sub": str(user.id), "organization_id": str(user.organization_id)}
    )
    
    # --- NEW: Set the HttpOnly Cookie ---
    response.set_cookie(
        key="access_token",
        value=f"Bearer {access_token}",
        httponly=True,  
        secure=False,   
        samesite="lax", 
        max_age=1800    
    )
    
    return {"message": "Successfully logged in"}

@router.post("/logout")
def logout(request:Request,response: Response):
    token = request.cookies.get("access_token")
    if token and token.startswith("Bearer "):
        token = token.split(" ")[1]

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM], options={"verify_signature": False})
        exp = payload.get("exp")
        
        if exp:
            # Calculate remaining time to live (TTL) in seconds
            now = datetime.now(timezone.utc).timestamp()
            ttl = int(exp - now)
            
            if ttl > 0:
                # Save to Redis with an automatic expiration!
                # Key format: blacklist:<token_string>
                sync_redis.setex(f"blacklist:{token}", ttl, "revoked")
    except jwt.PyJWTError:
        pass 
        
    response.delete_cookie("access_token")
    return {"message": "Successfully logged out and token revoked"}
