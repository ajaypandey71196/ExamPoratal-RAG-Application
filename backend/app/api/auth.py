"""Authentication API endpoints."""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from pydantic import BaseModel

from app.database import get_db
from app.models import User
from app.utils.security import (
    get_password_hash, verify_password, create_access_token,
    create_refresh_token, decode_token
)

router = APIRouter()


class RegisterRequest(BaseModel):
    """User registration request body."""
    email: str
    username: str
    password: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None


class LoginRequest(BaseModel):
    """User login request body."""
    email: str
    password: str


class RefreshTokenRequest(BaseModel):
    """Refresh token request body."""
    refresh_token: str


@router.post("/register")
async def register(
    request: RegisterRequest,
    db: AsyncSession = Depends(get_db)
):
    """Register a new user."""
    # Check if user already exists
    stmt = select(User).where((User.email == request.email) | (User.username == request.username))
    result = await db.execute(stmt)
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email or username already registered"
        )

    # Create new user
    user = User(
        email=request.email,
        username=request.username,
        password_hash=get_password_hash(request.password),
        first_name=request.first_name,
        last_name=request.last_name
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)

    return {
        "user_id": str(user.id),
        "email": user.email,
        "username": user.username,
        "message": "User registered successfully"
    }


@router.post("/login")
async def login(
    request: LoginRequest,
    db: AsyncSession = Depends(get_db)
):
    """Login user and return tokens."""
    # Find user
    stmt = select(User).where(User.email == request.email)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if not user or not verify_password(request.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )

    # Create tokens
    access_token = create_access_token({"sub": str(user.id)})
    refresh_token = create_refresh_token({"sub": str(user.id)})

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user_id": str(user.id)
    }


@router.post("/refresh")
async def refresh_token(request: RefreshTokenRequest):
    """Refresh access token."""
    payload = decode_token(request.refresh_token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token"
        )

    user_id = payload.get("sub")
    access_token = create_access_token({"sub": user_id})

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }
