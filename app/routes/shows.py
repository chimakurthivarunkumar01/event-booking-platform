from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.security import get_current_user, get_admin_user
from app.services import ShowService
from app.schemas import ShowCreate, ShowUpdate, ShowResponse
from app.exceptions import AppException, exception_to_http_exception
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/shows", tags=["Shows"])


@router.post("", response_model=ShowResponse, status_code=status.HTTP_201_CREATED)
async def create_show(
    show_data: ShowCreate,
    admin_user: dict = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Create a new show with seats (admin only)"""
    try:
        service = ShowService(db)
        return service.create_show(show_data)
    except AppException as e:
        raise exception_to_http_exception(e)


@router.get("/{show_id}", response_model=ShowResponse)
async def get_show(show_id: int, db: Session = Depends(get_db)):
    """Get show details"""
    try:
        service = ShowService(db)
        return service.get_show(show_id)
    except AppException as e:
        raise exception_to_http_exception(e)


@router.get("/event/{event_id}", response_model=dict)
async def get_shows_by_event(
    event_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Get all shows for an event"""
    try:
        service = ShowService(db)
        shows, total = service.get_shows_by_event(event_id, skip, limit)
        return {
            "total": total,
            "skip": skip,
            "limit": limit,
            "items": shows
        }
    except AppException as e:
        raise exception_to_http_exception(e)


@router.get("", response_model=dict)
async def get_upcoming_shows(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Get upcoming shows"""
    try:
        service = ShowService(db)
        shows, total = service.get_upcoming_shows(skip, limit)
        return {
            "total": total,
            "skip": skip,
            "limit": limit,
            "items": shows
        }
    except AppException as e:
        raise exception_to_http_exception(e)


@router.put("/{show_id}", response_model=ShowResponse)
async def update_show(
    show_id: int,
    show_data: ShowUpdate,
    admin_user: dict = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Update show (admin only)"""
    try:
        service = ShowService(db)
        return service.update_show(show_id, show_data)
    except AppException as e:
        raise exception_to_http_exception(e)


@router.delete("/{show_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_show(
    show_id: int,
    admin_user: dict = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Delete show (admin only)"""
    try:
        service = ShowService(db)
        service.delete_show(show_id)
    except AppException as e:
        raise exception_to_http_exception(e)
