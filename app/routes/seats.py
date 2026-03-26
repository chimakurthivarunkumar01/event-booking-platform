from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.security import get_current_user
from app.services import SeatService
from app.schemas import AvailableSeatsResponse
from app.exceptions import AppException, exception_to_http_exception
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/seats", tags=["Seats"])


@router.get("/show/{show_id}", response_model=AvailableSeatsResponse)
async def get_available_seats(
    show_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get available seats for a show"""
    try:
        service = SeatService(db)
        return service.get_available_seats(show_id)
    except AppException as e:
        raise exception_to_http_exception(e)
