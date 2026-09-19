from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.models.api_key import APIKey
from app.services.auth import (
    create_access_token,
    verify_password,
    hash_password,
    get_current_user
)
from app.schemas.user import UserCreate, UserResponse, LoginRequest, TokenResponse
from datetime import datetime, timedelta
from app.config import settings
import uuid

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


@router.post("/register", response_model=UserResponse, status_code=201)
async def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """Register a new user"""
    
    try:
        # Check if user exists
        existing_user = db.query(User).filter(
            (User.email == user_data.email) | (User.username == user_data.username)
        ).first()
        
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email or username already exists"
            )
        
        # Create new user
        new_user = User(
            id=str(uuid.uuid4()),
            email=user_data.email,
            username=user_data.username,
            password_hash=hash_password(user_data.password),
            full_name=user_data.full_name,
            status="active",
            created_at=datetime.utcnow()
        )
        
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        return UserResponse(
            user_id=new_user.id,
            email=new_user.email,
            username=new_user.username,
            full_name=new_user.full_name,
            status=new_user.status,
            created_at=new_user.created_at
        )
    
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        print(f"Registration error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed"
        )


@router.post("/login", response_model=TokenResponse)
async def login(credentials: LoginRequest, db: Session = Depends(get_db)):
    """Login user and return JWT token - FAST & NON-BLOCKING"""
    
    try:
        # Query user ONCE (no blocking operations)
        user = db.query(User).filter(User.email == credentials.email).first()
        
        # Verify password
        if not user or not verify_password(credentials.password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials",
                headers={"WWW-Authenticate": "Bearer"}
            )
        
        # Create token (synchronous, fast)
        access_token = create_access_token(
            data={"sub": str(user.id)},
            expires_delta=timedelta(minutes=settings.access_token_expire_minutes)
        )
        
        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            user_id=user.id,
            email=user.email,
            username=user.username
        )
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"Login error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed"
        )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current user info"""
    
    return UserResponse(
        user_id=current_user.id,
        email=current_user.email,
        username=current_user.username,
        full_name=current_user.full_name,
        status=current_user.status,
        created_at=current_user.created_at
    )


@router.post("/api-key/generate", status_code=201)
async def generate_api_key(
    request: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Generate new API key for current user"""
    
    try:
        # Create API key
        api_key_value = str(uuid.uuid4()).replace("-", "")
        api_key_prefix = api_key_value[:8]
        
        # Hash the key
        from app.services.auth import hash_password
        key_hash = hash_password(api_key_value)
        
        new_key = APIKey(
            id=str(uuid.uuid4()),
            user_id=current_user.id,
            key_hash=key_hash,
            key_prefix=api_key_prefix,
            status="active",
            rate_limit_requests=100,
            rate_limit_window_seconds=60,
            created_at=datetime.utcnow()
        )
        
        db.add(new_key)
        db.commit()
        
        return {
            "id": new_key.id,
            "key": api_key_value,
            "key_prefix": api_key_prefix,
            "status": new_key.status,
            "rate_limit": f"{new_key.rate_limit_requests} requests per {new_key.rate_limit_window_seconds}s",
            "created_at": new_key.created_at.isoformat()
        }
    
    except Exception as e:
        db.rollback()
        print(f"API key generation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate API key"
        )