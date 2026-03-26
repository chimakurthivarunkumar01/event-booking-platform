from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.security import get_current_user
from app.services import BookingService
from app.schemas import (
    LockSeatsRequest,
    LockSeatsResponse,
    ConfirmBookingRequest,
    BookingResponse,
    BookingDetailResponse,
    CancelBookingRequest
)
from app.exceptions import AppException, exception_to_http_exception
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/bookings", tags=["Bookings"])


@router.post("/lock-seats", response_model=LockSeatsResponse, status_code=status.HTTP_201_CREATED)
async def lock_seats(
    lock_request: LockSeatsRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Lock seats for booking (5 minute expiry).
    
    Returns booking ID and lock expiry time.
    Must confirm booking within 5 minutes or seats will be released.
    """
    try:
        service = BookingService(db)
        return service.lock_seats(current_user["user_id"], lock_request)
    except AppException as e:
        raise exception_to_http_exception(e)


@router.post("/confirm", response_model=BookingDetailResponse)
async def confirm_booking(
    confirm_request: ConfirmBookingRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Confirm a pending booking.
    Changes seat status from LOCKED to BOOKED.
    """
    try:
        service = BookingService(db)
        return service.confirm_booking(current_user["user_id"], confirm_request.booking_id)
    except AppException as e:
        raise exception_to_http_exception(e)


@router.post("/cancel", response_model=BookingResponse)
async def cancel_booking(
    cancel_request: CancelBookingRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Cancel a booking and release seats.
    Only pending or confirmed bookings can be cancelled.
    """
    try:
        service = BookingService(db)
        return service.cancel_booking(current_user["user_id"], cancel_request.booking_id)
    except AppException as e:
        raise exception_to_http_exception(e)


@router.get("", response_model=dict)
async def get_user_bookings(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all bookings for current user"""
    try:
        service = BookingService(db)
        bookings, total = service.get_user_bookings(current_user["user_id"], skip, limit)
        return {
            "total": total,
            "skip": skip,
            "limit": limit,
            "items": bookings
        }
    except AppException as e:
        raise exception_to_http_exception(e)


@router.get("/{booking_id}", response_model=BookingDetailResponse)
async def get_booking(
    booking_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get booking details"""
    try:
        service = BookingService(db)
        booking = service.get_booking(booking_id)
        
        # Verify ownership
        if booking.user_id != current_user["user_id"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot access booking of another user"
            )
        
        return booking
    except AppException as e:
        raise exception_to_http_exception(e)
