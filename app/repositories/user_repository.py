from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models import User
from app.repositories.base_repository import BaseRepository
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class UserRepository(BaseRepository[User]):
    """User repository"""
    
    def __init__(self, db: Session):
        super().__init__(db, User)
    
    def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        return self.db.query(User).filter(User.email == email).first()
    
    def get_by_username(self, username: str) -> Optional[User]:
        """Get user by username"""
        return self.db.query(User).filter(User.username == username).first()
    
    def get_active_users(self, skip: int = 0, limit: int = 10) -> tuple[list[User], int]:
        """Get active users"""
        query = self.db.query(User).filter(User.is_active == True)
        total = query.count()
        items = query.offset(skip).limit(limit).all()
        return items, total
