from sqlalchemy.orm import Session
from sqlalchemy import and_
from app.models import Booking, BookingStatus
from app.repositories.base_repository import BaseRepository
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)


class BookingRepository(BaseRepository[Booking]):
    """Booking repository"""
    
    def __init__(self, db: Session):
        super().__init__(db, Booking)
    
    def get_by_user_id(self, user_id: int, skip: int = 0, limit: int = 10) -> tuple[List[Booking], int]:
        """Get bookings by user id"""
        query = self.db.query(Booking).filter(Booking.user_id == user_id).order_by(Booking.created_at.desc())
        total = query.count()
        items = query.offset(skip).limit(limit).all()
        return items, total
    
    def get_by_show_id(self, show_id: int, skip: int = 0, limit: int = 10) -> tuple[List[Booking], int]:
        """Get bookings by show id"""
        query = self.db.query(Booking).filter(Booking.show_id == show_id)
        total = query.count()
        items = query.offset(skip).limit(limit).all()
        return items, total
    
    def get_pending_bookings(self, user_id: int) -> List[Booking]:
        """Get pending bookings for user"""
        return self.db.query(Booking).filter(
            and_(
                Booking.user_id == user_id,
                Booking.status == BookingStatus.PENDING
            )
        ).all()
    
    def get_confirmed_bookings(self, user_id: int, skip: int = 0, limit: int = 10) -> tuple[List[Booking], int]:
        """Get confirmed bookings for user"""
        query = self.db.query(Booking).filter(
            and_(
                Booking.user_id == user_id,
                Booking.status == BookingStatus.CONFIRMED
            )
        ).order_by(Booking.confirmed_at.desc())
        total = query.count()
        items = query.offset(skip).limit(limit).all()
        return items, total
    
    def get_by_user_and_show(self, user_id: int, show_id: int) -> Optional[Booking]:
        """Get booking by user and show"""
        return self.db.query(Booking).filter(
            and_(
                Booking.user_id == user_id,
                Booking.show_id == show_id,
                Booking.status == BookingStatus.PENDING
            )
        ).first()
