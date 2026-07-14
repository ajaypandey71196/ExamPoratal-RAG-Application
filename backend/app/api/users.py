"""User API endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.database import get_db
from app.models import User

router = APIRouter()


def get_current_user_id(authorization: str = None) -> str:
    """Extract user ID from JWT token."""
    from app.utils.security import decode_token
    
    if not authorization:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    
    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid auth scheme")
        
        payload = decode_token(token)
        if not payload:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
        
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
        
        return user_id
    except:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")


@router.get("/profile")
async def get_profile(
    authorization: str = None,
    db: AsyncSession = Depends(get_db)
):
    """Get user profile."""
    user_id = get_current_user_id(authorization)
    
    stmt = select(User).where(User.id == user_id)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    return {
        "id": str(user.id),
        "email": user.email,
        "username": user.username,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "role": user.role,
        "subscription_tier": user.subscription_tier,
        "created_at": user.created_at
    }


@router.put("/profile")
async def update_profile(
    first_name: str = None,
    last_name: str = None,
    bio: str = None,
    authorization: str = None,
    db: AsyncSession = Depends(get_db)
):
    """Update user profile."""
    user_id = get_current_user_id(authorization)
    
    stmt = select(User).where(User.id == user_id)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    if first_name:
        user.first_name = first_name
    if last_name:
        user.last_name = last_name
    if bio:
        user.bio = bio
    
    await db.commit()
    await db.refresh(user)
    
    return {
        "message": "Profile updated successfully",
        "user": {
            "id": str(user.id),
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "bio": user.bio
        }
    }
