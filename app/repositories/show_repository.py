from sqlalchemy.orm import Session
from sqlalchemy import and_
from app.models import Show
from app.repositories.base_repository import BaseRepository
from typing import List, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class ShowRepository(BaseRepository[Show]):
    """Show repository"""
    
    def __init__(self, db: Session):
        super().__init__(db, Show)
    
    def get_by_event_id(self, event_id: int, skip: int = 0, limit: int = 10) -> tuple[List[Show], int]:
        """Get shows by event id"""
        query = self.db.query(Show).filter(Show.event_id == event_id)
        total = query.count()
        items = query.offset(skip).limit(limit).all()
        return items, total
    
    def get_upcoming_shows(self, skip: int = 0, limit: int = 10) -> tuple[List[Show], int]:
        """Get upcoming shows"""
        query = self.db.query(Show).filter(
            and_(
                Show.show_date > datetime.utcnow(),
                Show.is_active == True
            )
        ).order_by(Show.show_date)
        total = query.count()
        items = query.offset(skip).limit(limit).all()
        return items, total
    
    def get_available_shows(self, skip: int = 0, limit: int = 10) -> tuple[List[Show], int]:
        """Get shows with available seats"""
        query = self.db.query(Show).filter(
            and_(
                Show.available_seats > 0,
                Show.is_active == True,
                Show.show_date > datetime.utcnow()
            )
        ).order_by(Show.show_date)
        total = query.count()
        items = query.offset(skip).limit(limit).all()
        return items, total
