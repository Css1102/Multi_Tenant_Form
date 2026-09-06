from fastapi import APIRouter, Depends, HTTPException,Request,Response,status
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select
from pydantic import BaseModel, EmailStr, Field
from typing import Literal, Optional
from uuid import UUID
from ..database import get_session
from ..models import OrganizationInvite, User, Organization
from ..auth import verify_password, create_access_token, SECRET_KEY, ALGORITHM, get_password_hash
from slowapi import Limiter
from slowapi.util import get_remote_address
import jwt
from datetime import datetime, timezone
from ..redis_client import sync_redis  
from ..tenant_migration import normalize_organization_name
from ..dependencies import get_current_user
limiter = Limiter(key_func=get_remote_address)
router = APIRouter(prefix="/auth", tags=["Authentication"])

class LoginRequest(BaseModel):
    email: str
    password: str
class SignupRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, description="Password must be at least 8 characters long")
    organization_name: Optional[str] = None
    invite_code: Optional[UUID] = None

class InviteRequest(BaseModel):
    role: Literal["admin", "member"] = "member"

@router.post("/signup", status_code=status.HTTP_201_CREATED)
@limiter.limit("5/minute")
def signup(
    request: Request,
    payload: SignupRequest,
    session: Session = Depends(get_session)
):
    if bool(payload.organization_name) == bool(payload.invite_code):
        raise HTTPException(status_code=422, detail="Provide a new organization name or an invite code")

    statement = select(User).where(User.email == payload.email)
    existing_user = session.exec(statement).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A user with this email already exists"
        )

    if payload.invite_code:
        invite = session.get(OrganizationInvite, payload.invite_code)
        if not invite or invite.used_at:
            raise HTTPException(status_code=403, detail="Invite code is invalid or already used")
        organization_id, role = invite.organization_id, invite.role
        invite.used_at = datetime.now(timezone.utc)
    else:
        organization_name = normalize_organization_name(payload.organization_name or "")
        if not organization_name:
            raise HTTPException(status_code=422, detail="Organization name is required")
        statement_org = select(Organization).where(Organization.name == organization_name)
        if session.exec(statement_org).first():
            raise HTTPException(status_code=403, detail="Organization exists. Ask for an invite code")
        new_org = Organization(name=organization_name)
        session.add(new_org)
        try:
            session.commit()
            session.refresh(new_org)
            organization_id, role = new_org.id, "owner"
        except IntegrityError:
            session.rollback()
            raise HTTPException(status_code=409, detail="Organization exists. Ask for an invite code")

    hashed_password = get_password_hash(payload.password)
    new_user = User(
        email=payload.email,
        hashed_password=hashed_password,
        organization_id=organization_id,
        role=role
    )

    # 4. Save to the database
    session.add(new_user)
    session.commit()
    session.refresh(new_user)
    return {"message": "User successfully created. Please log in."}

@router.post("/invites")
def create_invite(payload: InviteRequest, session: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    if current_user.role not in {"owner", "admin"}:
        raise HTTPException(status_code=403, detail="Only owners and admins can create invites")
    invite = OrganizationInvite(organization_id=current_user.organization_id, role=payload.role)
    session.add(invite); session.commit(); session.refresh(invite)
    return {"invite_code": invite.id, "role": invite.role}

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
        secure=True,       
        samesite="none",    
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


@router.get("/me")
def get_me(current_user: User = Depends(get_current_user)):
    """Expose only the identity details needed by the authenticated UI."""
    return {
        "id": current_user.id,
        "email": current_user.email,
        "organization_id": current_user.organization_id,
        "role": current_user.role,
    }
