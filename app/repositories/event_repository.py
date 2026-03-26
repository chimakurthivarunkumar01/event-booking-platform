from sqlalchemy.orm import Session
from app.models import Event
from app.repositories.base_repository import BaseRepository
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)


class EventRepository(BaseRepository[Event]):
    """Event repository"""
    
    def __init__(self, db: Session):
        super().__init__(db, Event)
    
    def get_active_events(self, skip: int = 0, limit: int = 10) -> tuple[List[Event], int]:
        """Get active events"""
        query = self.db.query(Event).filter(Event.is_active == True)
        total = query.count()
        items = query.offset(skip).limit(limit).all()
        return items, total
    
    def get_by_category(self, category: str, skip: int = 0, limit: int = 10) -> tuple[List[Event], int]:
        """Get events by category"""
        query = self.db.query(Event).filter(
            Event.category == category,
            Event.is_active == True
        )
        total = query.count()
        items = query.offset(skip).limit(limit).all()
        return items, total
