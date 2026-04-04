from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from auth.schemas import LoginRequest, LoginResponse, RegisterRequest, RegisterResponse
from auth.service import login, register
from db.dependencies import get_db

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register", response_model=RegisterResponse, status_code=201)
async def register_user(payload: RegisterRequest, db: AsyncSession = Depends(get_db)):
    """
    Register a new user. All new users start with role=viewer.
    Use /users/{id}/role to elevate to analyst or admin.
    """
    return await register(payload.email, payload.password, db)


@router.post("/login", response_model=LoginResponse)
async def login_user(payload: LoginRequest, db: AsyncSession = Depends(get_db)):
    """
    Login with email + password. Returns JWT + role.
    """
    return await login(payload.email, payload.password, db)