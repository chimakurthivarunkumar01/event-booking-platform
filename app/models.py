from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Enum, Float, Index
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.database import Base


class UserRole(str, enum.Enum):
    """User roles in the system"""
    USER = "user"
    ADMIN = "admin"


class SeatStatus(str, enum.Enum):
    """Seat status in a show"""
    AVAILABLE = "available"
    LOCKED = "locked"
    BOOKED = "booked"


class BookingStatus(str, enum.Enum):
    """Booking status"""
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"


class User(Base):
    """User model"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), default=UserRole.USER, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    bookings = relationship("Booking", back_populates="user", cascade="all, delete-orphan")
    
    __table_args__ = (
        Index("idx_user_email", "email"),
        Index("idx_user_username", "username"),
    )


class Event(Base):
    """Event model"""
    __tablename__ = "events"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False, index=True)
    description = Column(String(1000), nullable=True)
    category = Column(String(100), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    shows = relationship("Show", back_populates="event", cascade="all, delete-orphan")
    
    __table_args__ = (
        Index("idx_event_title", "title"),
        Index("idx_event_is_active", "is_active"),
    )


class Show(Base):
    """Show model (specific date/time of an event)"""
    __tablename__ = "shows"
    
    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, ForeignKey("events.id", ondelete="CASCADE"), nullable=False)
    show_date = Column(DateTime, nullable=False, index=True)
    total_seats = Column(Integer, nullable=False)
    available_seats = Column(Integer, nullable=False)
    price = Column(Float, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    event = relationship("Event", back_populates="shows")
    seats = relationship("Seat", back_populates="show", cascade="all, delete-orphan")
    bookings = relationship("Booking", back_populates="show", cascade="all, delete-orphan")
    
    __table_args__ = (
        Index("idx_show_event_id", "event_id"),
        Index("idx_show_date", "show_date"),
        Index("idx_show_is_active", "is_active"),
    )


class Seat(Base):
    """Seat model"""
    __tablename__ = "seats"
    
    id = Column(Integer, primary_key=True, index=True)
    show_id = Column(Integer, ForeignKey("shows.id", ondelete="CASCADE"), nullable=False)
    seat_number = Column(String(10), nullable=False)
    status = Column(Enum(SeatStatus), default=SeatStatus.AVAILABLE, nullable=False)
    locked_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    lock_timestamp = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    show = relationship("Show", back_populates="seats")
    
    __table_args__ = (
        Index("idx_seat_show_id", "show_id"),
        Index("idx_seat_status", "status"),
        Index("idx_seat_locked_by", "locked_by"),
        Index("idx_seat_show_status", "show_id", "status"),
    )


class Booking(Base):
    """Booking model"""
    __tablename__ = "bookings"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    show_id = Column(Integer, ForeignKey("shows.id", ondelete="CASCADE"), nullable=False)
    status = Column(Enum(BookingStatus), default=BookingStatus.PENDING, nullable=False)
    total_price = Column(Float, nullable=False)
    seat_count = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    confirmed_at = Column(DateTime, nullable=True)
    cancelled_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="bookings")
    show = relationship("Show", back_populates="bookings")
    booking_seats = relationship("BookingSeat", back_populates="booking", cascade="all, delete-orphan")
    
    __table_args__ = (
        Index("idx_booking_user_id", "user_id"),
        Index("idx_booking_show_id", "show_id"),
        Index("idx_booking_status", "status"),
        Index("idx_booking_user_status", "user_id", "status"),
    )


class BookingSeat(Base):
    """Booking-Seat junction model"""
    __tablename__ = "booking_seats"
    
    id = Column(Integer, primary_key=True, index=True)
    booking_id = Column(Integer, ForeignKey("bookings.id", ondelete="CASCADE"), nullable=False)
    seat_id = Column(Integer, ForeignKey("seats.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    booking = relationship("Booking", back_populates="booking_seats")
    
    __table_args__ = (
        Index("idx_booking_seat_booking_id", "booking_id"),
        Index("idx_booking_seat_seat_id", "seat_id"),
    )
