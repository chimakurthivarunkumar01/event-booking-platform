from sqlalchemy.orm import Session
from app.models import User, UserRole
from app.repositories import UserRepository
from app.security import hash_password, verify_password, create_access_token
from app.exceptions import (
    AuthenticationException,
    DuplicateResourceException,
    ResourceNotFoundException
)
from app.schemas import UserCreate, UserLogin, TokenResponse, UserResponse
from datetime import timedelta
import logging

logger = logging.getLogger(__name__)


class AuthService:
    """Authentication service"""
    
    def __init__(self, db: Session):
        self.db = db
        self.user_repo = UserRepository(db)
    
    def signup(self, user_data: UserCreate) -> TokenResponse:
        """Register a new user"""
        # Check if email exists
        existing_user = self.user_repo.get_by_email(user_data.email)
        if existing_user:
            raise DuplicateResourceException("User", "email", user_data.email)
        
        # Check if username exists
        existing_user = self.user_repo.get_by_username(user_data.username)
        if existing_user:
            raise DuplicateResourceException("User", "username", user_data.username)
        
        # Create user
        user = self.user_repo.create({
            "email": user_data.email,
            "username": user_data.username,
            "hashed_password": hash_password(user_data.password),
            "role": UserRole.USER,
        })
        
        logger.info(f"User registered: {user.email}")
        
        # Generate token
        access_token = create_access_token(
            data={"sub": user.id, "role": user.role.value}
        )
        
        return TokenResponse(
            access_token=access_token,
            user=UserResponse.from_orm(user)
        )
    
    def login(self, login_data: UserLogin) -> TokenResponse:
        """Authenticate user and return token"""
        user = self.user_repo.get_by_email(login_data.email)
        
        if not user or not verify_password(login_data.password, user.hashed_password):
            raise AuthenticationException("Invalid email or password")
        
        if not user.is_active:
            raise AuthenticationException("User account is inactive")
        
        logger.info(f"User logged in: {user.email}")
        
        # Generate token
        access_token = create_access_token(
            data={"sub": user.id, "role": user.role.value}
        )
        
        return TokenResponse(
            access_token=access_token,
            user=UserResponse.from_orm(user)
        )
    
    def get_user(self, user_id: int) -> User:
        """Get user by id"""
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise ResourceNotFoundException("User", user_id)
        return user
