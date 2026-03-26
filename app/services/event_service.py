from sqlalchemy.orm import Session
from app.models import Event
from app.repositories import EventRepository
from app.exceptions import ResourceNotFoundException, InvalidOperationException
from app.schemas import EventCreate, EventUpdate, EventResponse, EventDetailResponse
import logging

logger = logging.getLogger(__name__)


class EventService:
    """Event management service"""
    
    def __init__(self, db: Session):
        self.db = db
        self.event_repo = EventRepository(db)
    
    def create_event(self, event_data: EventCreate) -> EventResponse:
        """Create a new event (admin only)"""
        event = self.event_repo.create({
            "title": event_data.title,
            "description": event_data.description,
            "category": event_data.category,
            "is_active": True,
        })
        
        logger.info(f"Event created: {event.id} - {event.title}")
        return EventResponse.from_orm(event)
    
    def get_event(self, event_id: int) -> EventDetailResponse:
        """Get event details with shows"""
        event = self.event_repo.get_by_id(event_id)
        if not event:
            raise ResourceNotFoundException("Event", event_id)
        
        return EventDetailResponse.from_orm(event)
    
    def get_all_events(self, skip: int = 0, limit: int = 10) -> tuple[list[EventResponse], int]:
        """Get all active events"""
        events, total = self.event_repo.get_active_events(skip, limit)
        return [EventResponse.from_orm(e) for e in events], total
    
    def get_events_by_category(self, category: str, skip: int = 0, limit: int = 10) -> tuple[list[EventResponse], int]:
        """Get events by category"""
        events, total = self.event_repo.get_by_category(category, skip, limit)
        return [EventResponse.from_orm(e) for e in events], total
    
    def update_event(self, event_id: int, event_data: EventUpdate) -> EventResponse:
        """Update event (admin only)"""
        event = self.event_repo.get_by_id(event_id)
        if not event:
            raise ResourceNotFoundException("Event", event_id)
        
        update_data = event_data.dict(exclude_unset=True)
        event = self.event_repo.update(event_id, update_data)
        
        logger.info(f"Event updated: {event_id}")
        return EventResponse.from_orm(event)
    
    def delete_event(self, event_id: int) -> bool:
        """Delete event (admin only)"""
        event = self.event_repo.get_by_id(event_id)
        if not event:
            raise ResourceNotFoundException("Event", event_id)
        
        success = self.event_repo.delete(event_id)
        if success:
            logger.info(f"Event deleted: {event_id}")
        return success
