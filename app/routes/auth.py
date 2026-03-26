from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.services import AuthService
from app.schemas import UserCreate, UserLogin, TokenResponse, UserResponse
from app.exceptions import AppException, exception_to_http_exception
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


@router.post("/signup", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def signup(user_data: UserCreate, db: Session = Depends(get_db)):
    """
    Register a new user.
    
    - **email**: User email (must be unique)
    - **username**: Username (must be unique, 3-100 chars)
    - **password**: Password (min 8 chars, must contain uppercase and digit)
    """
    try:
        service = AuthService(db)
        return service.signup(user_data)
    except AppException as e:
        raise exception_to_http_exception(e)


@router.post("/login", response_model=TokenResponse)
async def login(login_data: UserLogin, db: Session = Depends(get_db)):
    """
    Login user and get JWT token.
    
    - **email**: User email
    - **password**: User password
    """
    try:
        service = AuthService(db)
        return service.login(login_data)
    except AppException as e:
        raise exception_to_http_exception(e)


@router.get("/me", response_model=UserResponse)
async def get_current_user(current_user: dict = Depends(lambda: None), db: Session = Depends(get_db)):
    """Get current authenticated user info"""
    # This endpoint requires authentication via JWT
    # The current_user dependency is handled by security middleware
    try:
        from app.security import get_current_user as get_user
        user_data = await get_user(None)  # Will be injected by FastAPI
        service = AuthService(db)
        user = service.get_user(user_data["user_id"])
        return UserResponse.from_orm(user)
    except AppException as e:
        raise exception_to_http_exception(e)
