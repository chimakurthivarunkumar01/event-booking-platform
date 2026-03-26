from pydantic import BaseModel, EmailStr, Field, validator
from datetime import datetime
from typing import Optional, List
from app.models import UserRole, SeatStatus, BookingStatus


# ============ User Schemas ============
class UserBase(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=100)


class UserCreate(UserBase):
    password: str = Field(..., min_length=8)
    
    @validator('password')
    def password_strength(cls, v):
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain uppercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain digit')
        return v


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(UserBase):
    id: int
    role: UserRole
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


# ============ Event Schemas ============
class EventBase(BaseModel):
    title: str = Field(..., min_length=3, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    category: str = Field(..., min_length=2, max_length=100)


class EventCreate(EventBase):
    pass


class EventUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=3, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    category: Optional[str] = Field(None, min_length=2, max_length=100)
    is_active: Optional[bool] = None


class EventResponse(EventBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class EventDetailResponse(EventResponse):
    shows: List['ShowResponse'] = []


# ============ Show Schemas ============
class ShowBase(BaseModel):
    event_id: int
    show_date: datetime
    total_seats: int = Field(..., gt=0)
    price: float = Field(..., gt=0)


class ShowCreate(ShowBase):
    pass


class ShowUpdate(BaseModel):
    show_date: Optional[datetime] = None
    price: Optional[float] = Field(None, gt=0)
    is_active: Optional[bool] = None


class ShowResponse(ShowBase):
    id: int
    available_seats: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# ============ Seat Schemas ============
class SeatResponse(BaseModel):
    id: int
    seat_number: str
    status: SeatStatus
    locked_by: Optional[int] = None
    lock_timestamp: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class AvailableSeatsResponse(BaseModel):
    show_id: int
    total_seats: int
    available_count: int
    locked_count: int
    booked_count: int
    seats: List[SeatResponse]


# ============ Booking Schemas ============
class LockSeatsRequest(BaseModel):
    show_id: int
    seat_ids: List[int] = Field(..., min_items=1)


class LockSeatsResponse(BaseModel):
    booking_id: int
    locked_seats: List[SeatResponse]
    lock_expiry: datetime
    total_price: float


class ConfirmBookingRequest(BaseModel):
    booking_id: int


class BookingResponse(BaseModel):
    id: int
    user_id: int
    show_id: int
    status: BookingStatus
    total_price: float
    seat_count: int
    created_at: datetime
    confirmed_at: Optional[datetime] = None
    cancelled_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class BookingDetailResponse(BookingResponse):
    booking_seats: List['BookingSeatResponse'] = []


class BookingSeatResponse(BaseModel):
    id: int
    seat_id: int
    
    class Config:
        from_attributes = True


class UserBookingsResponse(BaseModel):
    total: int
    bookings: List[BookingDetailResponse]


class CancelBookingRequest(BaseModel):
    booking_id: int


# ============ Pagination ============
class PaginationParams(BaseModel):
    skip: int = Field(0, ge=0)
    limit: int = Field(10, ge=1, le=100)


class PaginatedResponse(BaseModel):
    total: int
    skip: int
    limit: int
    items: List


# Update forward references
EventDetailResponse.model_rebuild()
BookingDetailResponse.model_rebuild()
