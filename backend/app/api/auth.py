"""Authentication API endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.database import get_db
from app.models import User
from app.utils.security import (
    get_password_hash, verify_password, create_access_token,
    create_refresh_token, decode_token
)

router = APIRouter()


class RegisterRequest:
    """User registration request."""
    def __init__(self, email: str, username: str, password: str, first_name: str = None, last_name: str = None):
        self.email = email
        self.username = username
        self.password = password
        self.first_name = first_name
        self.last_name = last_name


class LoginRequest:
    """User login request."""
    def __init__(self, email: str, password: str):
        self.email = email
        self.password = password


@router.post("/register")
async def register(
    email: str,
    username: str,
    password: str,
    first_name: str = None,
    last_name: str = None,
    db: AsyncSession = Depends(get_db)
):
    """Register a new user."""
    # Check if user already exists
    stmt = select(User).where((User.email == email) | (User.username == username))
    result = await db.execute(stmt)
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email or username already registered"
        )

    # Create new user
    user = User(
        email=email,
        username=username,
        password_hash=get_password_hash(password),
        first_name=first_name,
        last_name=last_name
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
    email: str,
    password: str,
    db: AsyncSession = Depends(get_db)
):
    """Login user and return tokens."""
    # Find user
    stmt = select(User).where(User.email == email)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if not user or not verify_password(password, user.password_hash):
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
async def refresh_token(refresh_token: str):
    """Refresh access token."""
    payload = decode_token(refresh_token)
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
