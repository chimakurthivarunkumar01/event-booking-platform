from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from app.models import Booking, BookingStatus, Seat, SeatStatus, Show, BookingSeat
from app.repositories import BookingRepository, SeatRepository, ShowRepository
from app.exceptions import (
    ResourceNotFoundException,
    InvalidOperationException,
    SeatLockException,
    BookingException,
    ConcurrencyException
)
from app.schemas import (
    LockSeatsRequest,
    LockSeatsResponse,
    ConfirmBookingRequest,
    BookingResponse,
    BookingDetailResponse,
    SeatResponse
)
from datetime import datetime, timedelta
from app.config import get_settings
import logging

logger = logging.getLogger(__name__)
settings = get_settings()


class BookingService:
    """Booking service with concurrency handling"""
    
    def __init__(self, db: Session):
        self.db = db
        self.booking_repo = BookingRepository(db)
        self.seat_repo = SeatRepository(db)
        self.show_repo = ShowRepository(db)
    
    def lock_seats(self, user_id: int, lock_request: LockSeatsRequest) -> LockSeatsResponse:
        """
        Lock seats for booking with concurrency control.
        Uses database-level locking to prevent race conditions.
        """
        show_id = lock_request.show_id
        seat_ids = lock_request.seat_ids
        
        # Validate show exists
        show = self.show_repo.get_by_id(show_id)
        if not show:
            raise ResourceNotFoundException("Show", show_id)
        
        if not show.is_active:
            raise InvalidOperationException("Show is not active")
        
        if show.show_date <= datetime.utcnow():
            raise InvalidOperationException("Show has already started")
        
        # Validate seat count
        if len(seat_ids) == 0:
            raise InvalidOperationException("At least one seat must be selected")
        
        if len(seat_ids) > 10:
            raise InvalidOperationException("Maximum 10 seats can be booked at once")
        
        try:
            # Use database transaction with row-level locking
            # This prevents concurrent modifications
            seats = self.seat_repo.get_seats_by_ids(seat_ids)
            
            if len(seats) != len(seat_ids):
                raise InvalidOperationException("One or more seats not found")
            
            # Verify all seats belong to the same show
            if not all(seat.show_id == show_id for seat in seats):
                raise InvalidOperationException("All seats must belong to the same show")
            
            # Check seat availability and lock them atomically
            locked_seats = []
            for seat in seats:
                if seat.status != SeatStatus.AVAILABLE:
                    raise SeatLockException(
                        f"Seat {seat.seat_number} is not available (status: {seat.status})"
                    )
                
                # Lock the seat
                seat.status = SeatStatus.LOCKED
                seat.locked_by = user_id
                seat.lock_timestamp = datetime.utcnow()
                locked_seats.append(seat)
            
            # Create pending booking
            total_price = len(seats) * show.price
            booking = self.booking_repo.create({
                "user_id": user_id,
                "show_id": show_id,
                "status": BookingStatus.PENDING,
                "total_price": total_price,
                "seat_count": len(seats),
            })
            
            # Create booking-seat relationships
            for seat in locked_seats:
                booking_seat = BookingSeat(
                    booking_id=booking.id,
                    seat_id=seat.id
                )
                self.db.add(booking_seat)
            
            # Update show available seats
            show.available_seats -= len(seats)
            
            # Commit transaction
            self.db.commit()
            
            logger.info(
                f"Seats locked for booking {booking.id}: "
                f"user={user_id}, show={show_id}, seats={len(seats)}"
            )
            
            lock_expiry = datetime.utcnow() + timedelta(seconds=settings.SEAT_LOCK_DURATION)
            
            return LockSeatsResponse(
                booking_id=booking.id,
                locked_seats=[SeatResponse.from_orm(s) for s in locked_seats],
                lock_expiry=lock_expiry,
                total_price=total_price
            )
        
        except Exception as e:
            self.db.rollback()
            if isinstance(e, (SeatLockException, InvalidOperationException)):
                raise
            logger.error(f"Error locking seats: {str(e)}")
            raise ConcurrencyException("Failed to lock seats due to concurrent access")
    
    def confirm_booking(self, user_id: int, booking_id: int) -> BookingDetailResponse:
        """
        Confirm a pending booking.
        Changes seat status from LOCKED to BOOKED.
        """
        booking = self.booking_repo.get_by_id(booking_id)
        if not booking:
            raise ResourceNotFoundException("Booking", booking_id)
        
        # Verify ownership
        if booking.user_id != user_id:
            raise InvalidOperationException("Cannot confirm booking of another user")
        
        if booking.status != BookingStatus.PENDING:
            raise InvalidOperationException(
                f"Booking is already {booking.status.value}"
            )
        
        # Check if lock has expired
        lock_expiry = booking.created_at + timedelta(seconds=settings.SEAT_LOCK_DURATION)
        if datetime.utcnow() > lock_expiry:
            # Release seats and cancel booking
            self._release_booking_seats(booking)
            booking.status = BookingStatus.CANCELLED
            booking.cancelled_at = datetime.utcnow()
            self.db.commit()
            raise BookingException("Booking lock has expired. Please try again.")
        
        try:
            # Update booking status
            booking.status = BookingStatus.CONFIRMED
            booking.confirmed_at = datetime.utcnow()
            
            # Update seat statuses
            for booking_seat in booking.booking_seats:
                seat = booking_seat.booking_seats if hasattr(booking_seat, 'booking_seats') else None
                if not seat:
                    seat = self.seat_repo.get_by_id(booking_seat.seat_id)
                
                seat.status = SeatStatus.BOOKED
                seat.locked_by = None
                seat.lock_timestamp = None
            
            self.db.commit()
            
            logger.info(f"Booking confirmed: {booking_id}")
            
            return BookingDetailResponse.from_orm(booking)
        
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error confirming booking: {str(e)}")
            raise BookingException("Failed to confirm booking")
    
    def cancel_booking(self, user_id: int, booking_id: int) -> BookingResponse:
        """Cancel a booking and release seats"""
        booking = self.booking_repo.get_by_id(booking_id)
        if not booking:
            raise ResourceNotFoundException("Booking", booking_id)
        
        # Verify ownership
        if booking.user_id != user_id:
            raise InvalidOperationException("Cannot cancel booking of another user")
        
        if booking.status == BookingStatus.CANCELLED:
            raise InvalidOperationException("Booking is already cancelled")
        
        try:
            # Release seats
            self._release_booking_seats(booking)
            
            # Update booking status
            booking.status = BookingStatus.CANCELLED
            booking.cancelled_at = datetime.utcnow()
            
            # Update show available seats
            show = self.show_repo.get_by_id(booking.show_id)
            show.available_seats += booking.seat_count
            
            self.db.commit()
            
            logger.info(f"Booking cancelled: {booking_id}")
            
            return BookingResponse.from_orm(booking)
        
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error cancelling booking: {str(e)}")
            raise BookingException("Failed to cancel booking")
    
    def _release_booking_seats(self, booking: Booking):
        """Release all seats in a booking"""
        for booking_seat in booking.booking_seats:
            seat = self.seat_repo.get_by_id(booking_seat.seat_id)
            seat.status = SeatStatus.AVAILABLE
            seat.locked_by = None
            seat.lock_timestamp = None
    
    def get_user_bookings(self, user_id: int, skip: int = 0, limit: int = 10) -> tuple[list[BookingDetailResponse], int]:
        """Get all bookings for a user"""
        bookings, total = self.booking_repo.get_by_user_id(user_id, skip, limit)
        return [BookingDetailResponse.from_orm(b) for b in bookings], total
    
    def get_booking(self, booking_id: int) -> BookingDetailResponse:
        """Get booking details"""
        booking = self.booking_repo.get_by_id(booking_id)
        if not booking:
            raise ResourceNotFoundException("Booking", booking_id)
        return BookingDetailResponse.from_orm(booking)
    
    def cleanup_expired_locks(self, show_id: int) -> int:
        """
        Cleanup expired locks and release seats.
        Should be called periodically via background task.
        """
        expiry_time = datetime.utcnow() - timedelta(seconds=settings.SEAT_LOCK_DURATION)
        
        # Find expired bookings
        expired_bookings = self.db.query(Booking).filter(
            and_(
                Booking.show_id == show_id,
                Booking.status == BookingStatus.PENDING,
                Booking.created_at < expiry_time
            )
        ).all()
        
        released_count = 0
        for booking in expired_bookings:
            self._release_booking_seats(booking)
            booking.status = BookingStatus.CANCELLED
            booking.cancelled_at = datetime.utcnow()
            
            # Update show available seats
            show = self.show_repo.get_by_id(booking.show_id)
            show.available_seats += booking.seat_count
            
            released_count += 1
        
        if released_count > 0:
            self.db.commit()
            logger.info(f"Cleaned up {released_count} expired locks for show {show_id}")
        
        return released_count
