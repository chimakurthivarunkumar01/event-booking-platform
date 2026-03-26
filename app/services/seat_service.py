from sqlalchemy.orm import Session
from sqlalchemy import and_
from app.models import Seat, SeatStatus, Show
from app.repositories import SeatRepository, ShowRepository
from app.exceptions import ResourceNotFoundException, InvalidOperationException
from app.schemas import SeatResponse, AvailableSeatsResponse
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class SeatService:
    """Seat management service"""
    
    def __init__(self, db: Session):
        self.db = db
        self.seat_repo = SeatRepository(db)
        self.show_repo = ShowRepository(db)
    
    def get_available_seats(self, show_id: int) -> AvailableSeatsResponse:
        """Get available seats for a show"""
        show = self.show_repo.get_by_id(show_id)
        if not show:
            raise ResourceNotFoundException("Show", show_id)
        
        seats, _ = self.seat_repo.get_by_show_id(show_id, skip=0, limit=1000)
        
        available = [s for s in seats if s.status == SeatStatus.AVAILABLE]
        locked = [s for s in seats if s.status == SeatStatus.LOCKED]
        booked = [s for s in seats if s.status == SeatStatus.BOOKED]
        
        return AvailableSeatsResponse(
            show_id=show_id,
            total_seats=show.total_seats,
            available_count=len(available),
            locked_count=len(locked),
            booked_count=len(booked),
            seats=[SeatResponse.from_orm(s) for s in available]
        )
    
    def release_expired_locks(self, show_id: int, lock_duration: int) -> int:
        """Release expired seat locks"""
        expiry_time = datetime.utcnow() - timedelta(seconds=lock_duration)
        expired_seats = self.seat_repo.get_expired_locks(show_id, expiry_time)
        
        released_count = 0
        for seat in expired_seats:
            seat.status = SeatStatus.AVAILABLE
            seat.locked_by = None
            seat.lock_timestamp = None
            released_count += 1
        
        if released_count > 0:
            self.db.commit()
            logger.info(f"Released {released_count} expired locks for show {show_id}")
        
        return released_count
    
    def get_seat(self, seat_id: int) -> Seat:
        """Get seat by id"""
        seat = self.seat_repo.get_by_id(seat_id)
        if not seat:
            raise ResourceNotFoundException("Seat", seat_id)
        return seat
