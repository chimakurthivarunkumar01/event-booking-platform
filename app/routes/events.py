from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.security import get_current_user, get_admin_user
from app.services import EventService
from app.schemas import (
    EventCreate,
    EventUpdate,
    EventResponse,
    EventDetailResponse,
    PaginationParams
)
from app.exceptions import AppException, exception_to_http_exception
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/events", tags=["Events"])


@router.post("", response_model=EventResponse, status_code=status.HTTP_201_CREATED)
async def create_event(
    event_data: EventCreate,
    admin_user: dict = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Create a new event (admin only)"""
    try:
        service = EventService(db)
        return service.create_event(event_data)
    except AppException as e:
        raise exception_to_http_exception(e)


@router.get("", response_model=dict)
async def get_all_events(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Get all active events with pagination"""
    try:
        service = EventService(db)
        events, total = service.get_all_events(skip, limit)
        return {
            "total": total,
            "skip": skip,
            "limit": limit,
            "items": events
        }
    except AppException as e:
        raise exception_to_http_exception(e)


@router.get("/category/{category}", response_model=dict)
async def get_events_by_category(
    category: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Get events by category"""
    try:
        service = EventService(db)
        events, total = service.get_events_by_category(category, skip, limit)
        return {
            "total": total,
            "skip": skip,
            "limit": limit,
            "items": events
        }
    except AppException as e:
        raise exception_to_http_exception(e)


@router.get("/{event_id}", response_model=EventDetailResponse)
async def get_event(event_id: int, db: Session = Depends(get_db)):
    """Get event details with all shows"""
    try:
        service = EventService(db)
        return service.get_event(event_id)
    except AppException as e:
        raise exception_to_http_exception(e)


@router.put("/{event_id}", response_model=EventResponse)
async def update_event(
    event_id: int,
    event_data: EventUpdate,
    admin_user: dict = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Update event (admin only)"""
    try:
        service = EventService(db)
        return service.update_event(event_id, event_data)
    except AppException as e:
        raise exception_to_http_exception(e)


@router.delete("/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_event(
    event_id: int,
    admin_user: dict = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Delete event (admin only)"""
    try:
        service = EventService(db)
        service.delete_event(event_id)
    except AppException as e:
        raise exception_to_http_exception(e)
