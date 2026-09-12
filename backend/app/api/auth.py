from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.models.api_key import APIKey
from app.services.password import hash_password, verify_password
from app.services.auth import create_access_token, verify_token, create_api_key
from app.schemas.user import UserCreate, UserLogin, UserResponse, TokenResponse, APIKeyGenerate, APIKeyResponse
from datetime import timedelta
from app.config import settings

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])

@router.post("/register", response_model=UserResponse)
async def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """Register a new user"""
    
    # Check if user exists
    existing_user = db.query(User).filter(
        (User.email == user_data.email) | (User.username == user_data.username)
    ).first()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email or username already registered"
        )
    
    # Create new user
    new_user = User(
        email=user_data.email,
        username=user_data.username,
        password_hash=hash_password(user_data.password),
        full_name=user_data.full_name,
        status="active"
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return new_user

@router.post("/login", response_model=TokenResponse)
async def login(credentials: UserLogin, db: Session = Depends(get_db)):
    """Login user and get access token"""
    
    # Find user
    user = db.query(User).filter(User.email == credentials.email).first()
    
    if not user or not verify_password(credentials.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    if user.status == "suspended":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is suspended"
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.user_id), "email": user.email},
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user
    }

@router.post("/api-key/generate", response_model=APIKeyResponse)
async def generate_api_key(
    key_data: APIKeyGenerate,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Generate a new API key for current user"""
    
    # Generate key
    full_key, key_hash, key_prefix = create_api_key(str(current_user.user_id))
    
    # Store in database
    api_key = APIKey(
        user_id=current_user.user_id,
        key_hash=key_hash,
        key_prefix=key_prefix,
        name=key_data.name,
        status="active",
        rate_limit_requests=key_data.rate_limit_requests,
        rate_limit_window_seconds=key_data.rate_limit_window_seconds
    )
    
    db.add(api_key)
    db.commit()
    db.refresh(api_key)
    
    return {
        "api_key_id": str(api_key.api_key_id),
        "key": full_key,  # Only show once!
        "key_prefix": api_key.key_prefix,
        "name": api_key.name,
        "status": api_key.status,
        "created_at": api_key.created_at
    }

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current user information"""
    return current_user

# Dependency: Get current authenticated user
async def get_current_user(
    token: str = None,
    db: Session = Depends(get_db)
) -> User:
    """Extract and validate current user from JWT token"""
    
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
    
    payload = verify_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
    
    user_id = payload.get("user_id")
    user = db.query(User).filter(User.user_id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    return user