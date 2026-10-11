from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from backend.app.db.session import get_db
from backend.app.core.security import verify_password, create_access_token
from backend.app.models.entities import User
from backend.app.schemas.api_schemas import Token, LoginRequest, UserResponse

router = APIRouter()

@router.post("/login", response_model=Token)
async def login(credentials: LoginRequest, db: AsyncSession = Depends(get_db)):
    stmt = select(User).where(User.email == credentials.email, User.is_active == True)
    result = await db.execute(stmt)
    user = result.scalars().first()
    
    if not user or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(subject=user.id)
    return Token(
        access_token=access_token,
        token_type="bearer",
        user_id=user.id,
        organization_id=user.organization_id,
        role=user.role,
        full_name=user.full_name
    )

@router.get("/me", response_model=UserResponse)
async def read_current_user(current_user: User = Depends(get_db)):
    return current_user
