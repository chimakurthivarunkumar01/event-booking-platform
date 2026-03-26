from fastapi import HTTPException, status
import logging

logger = logging.getLogger(__name__)


class AppException(Exception):
    """Base application exception"""
    def __init__(self, message: str, status_code: int = status.HTTP_400_BAD_REQUEST):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class AuthenticationException(AppException):
    """Authentication failed"""
    def __init__(self, message: str = "Authentication failed"):
        super().__init__(message, status.HTTP_401_UNAUTHORIZED)


class AuthorizationException(AppException):
    """User not authorized"""
    def __init__(self, message: str = "Not authorized"):
        super().__init__(message, status.HTTP_403_FORBIDDEN)


class ResourceNotFoundException(AppException):
    """Resource not found"""
    def __init__(self, resource: str, resource_id: int):
        message = f"{resource} with id {resource_id} not found"
        super().__init__(message, status.HTTP_404_NOT_FOUND)


class DuplicateResourceException(AppException):
    """Resource already exists"""
    def __init__(self, resource: str, field: str, value: str):
        message = f"{resource} with {field} '{value}' already exists"
        super().__init__(message, status.HTTP_409_CONFLICT)


class InvalidOperationException(AppException):
    """Invalid operation"""
    def __init__(self, message: str):
        super().__init__(message, status.HTTP_400_BAD_REQUEST)


class SeatLockException(AppException):
    """Seat locking failed"""
    def __init__(self, message: str = "Failed to lock seats"):
        super().__init__(message, status.HTTP_409_CONFLICT)


class BookingException(AppException):
    """Booking operation failed"""
    def __init__(self, message: str):
        super().__init__(message, status.HTTP_400_BAD_REQUEST)


class ConcurrencyException(AppException):
    """Concurrency conflict"""
    def __init__(self, message: str = "Concurrency conflict occurred"):
        super().__init__(message, status.HTTP_409_CONFLICT)


def exception_to_http_exception(exc: AppException) -> HTTPException:
    """Convert AppException to HTTPException"""
    logger.error(f"Application error: {exc.message}")
    return HTTPException(
        status_code=exc.status_code,
        detail=exc.message
    )
