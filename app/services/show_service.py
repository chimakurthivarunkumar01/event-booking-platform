from sqlalchemy.orm import Session
from app.models import Show, Seat, SeatStatus
from app.repositories import ShowRepository, EventRepository, SeatRepository
from app.exceptions import ResourceNotFoundException, InvalidOperationException
from app.schemas import ShowCreate, ShowUpdate, ShowResponse
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class ShowService:
    """Show management service"""
    
    def __init__(self, db: Session):
        self.db = db
        self.show_repo = ShowRepository(db)
        self.event_repo = EventRepository(db)
        self.seat_repo = SeatRepository(db)
    
    def create_show(self, show_data: ShowCreate) -> ShowResponse:
        """Create a new show with seats (admin only)"""
        # Verify event exists
        event = self.event_repo.get_by_id(show_data.event_id)
        if not event:
            raise ResourceNotFoundException("Event", show_data.event_id)
        
        # Validate show date is in future
        if show_data.show_date <= datetime.utcnow():
            raise InvalidOperationException("Show date must be in the future")
        
        # Create show
        show = self.show_repo.create({
            "event_id": show_data.event_id,
            "show_date": show_data.show_date,
            "total_seats": show_data.total_seats,
            "available_seats": show_data.total_seats,
            "price": show_data.price,
            "is_active": True,
        })
        
        # Create seats
        self._create_seats_for_show(show.id, show_data.total_seats)
        
        logger.info(f"Show created: {show.id} with {show_data.total_seats} seats")
        return ShowResponse.from_orm(show)
    
    def _create_seats_for_show(self, show_id: int, total_seats: int):
        """Create seats for a show"""
        seats = []
        rows = (total_seats // 10) + 1
        cols = 10
        
        for row in range(rows):
            for col in range(cols):
                if len(seats) >= total_seats:
                    break
                seat_number = f"{chr(65 + row)}{col + 1}"
                seats.append(Seat(
                    show_id=show_id,
                    seat_number=seat_number,
                    status=SeatStatus.AVAILABLE
                ))
        
        self.db.add_all(seats)
        self.db.commit()
    
    def get_show(self, show_id: int) -> ShowResponse:
        """Get show details"""
        show = self.show_repo.get_by_id(show_id)
        if not show:
            raise ResourceNotFoundException("Show", show_id)
        return ShowResponse.from_orm(show)
    
    def get_shows_by_event(self, event_id: int, skip: int = 0, limit: int = 10) -> tuple[list[ShowResponse], int]:
        """Get shows for an event"""
        event = self.event_repo.get_by_id(event_id)
        if not event:
            raise ResourceNotFoundException("Event", event_id)
        
        shows, total = self.show_repo.get_by_event_id(event_id, skip, limit)
        return [ShowResponse.from_orm(s) for s in shows], total
    
    def get_upcoming_shows(self, skip: int = 0, limit: int = 10) -> tuple[list[ShowResponse], int]:
        """Get upcoming shows"""
        shows, total = self.show_repo.get_upcoming_shows(skip, limit)
        return [ShowResponse.from_orm(s) for s in shows], total
    
    def update_show(self, show_id: int, show_data: ShowUpdate) -> ShowResponse:
        """Update show (admin only)"""
        show = self.show_repo.get_by_id(show_id)
        if not show:
            raise ResourceNotFoundException("Show", show_id)
        
        update_data = show_data.dict(exclude_unset=True)
        show = self.show_repo.update(show_id, update_data)
        
        logger.info(f"Show updated: {show_id}")
        return ShowResponse.from_orm(show)
    
    def delete_show(self, show_id: int) -> bool:
        """Delete show (admin only)"""
        show = self.show_repo.get_by_id(show_id)
        if not show:
            raise ResourceNotFoundException("Show", show_id)
        
        success = self.show_repo.delete(show_id)
        if success:
            logger.info(f"Show deleted: {show_id}")
        return success
