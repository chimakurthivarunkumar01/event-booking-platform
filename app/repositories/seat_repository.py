from sqlalchemy.orm import Session
from sqlalchemy import and_
from app.models import Seat, SeatStatus
from app.repositories.base_repository import BaseRepository
from typing import List, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class SeatRepository(BaseRepository[Seat]):
    """Seat repository"""
    
    def __init__(self, db: Session):
        super().__init__(db, Seat)
    
    def get_by_show_id(self, show_id: int, skip: int = 0, limit: int = 100) -> tuple[List[Seat], int]:
        """Get seats by show id"""
        query = self.db.query(Seat).filter(Seat.show_id == show_id)
        total = query.count()
        items = query.offset(skip).limit(limit).all()
        return items, total
    
    def get_available_seats(self, show_id: int) -> List[Seat]:
        """Get available seats for a show"""
        return self.db.query(Seat).filter(
            and_(
                Seat.show_id == show_id,
                Seat.status == SeatStatus.AVAILABLE
            )
        ).all()
    
    def get_locked_seats(self, show_id: int) -> List[Seat]:
        """Get locked seats for a show"""
        return self.db.query(Seat).filter(
            and_(
                Seat.show_id == show_id,
                Seat.status == SeatStatus.LOCKED
            )
        ).all()
    
    def get_booked_seats(self, show_id: int) -> List[Seat]:
        """Get booked seats for a show"""
        return self.db.query(Seat).filter(
            and_(
                Seat.show_id == show_id,
                Seat.status == SeatStatus.BOOKED
            )
        ).all()
    
    def get_seats_by_ids(self, seat_ids: List[int]) -> List[Seat]:
        """Get seats by ids"""
        return self.db.query(Seat).filter(Seat.id.in_(seat_ids)).all()
    
    def get_expired_locks(self, show_id: int, expiry_time: datetime) -> List[Seat]:
        """Get seats with expired locks"""
        return self.db.query(Seat).filter(
            and_(
                Seat.show_id == show_id,
                Seat.status == SeatStatus.LOCKED,
                Seat.lock_timestamp < expiry_time
            )
        ).all()
