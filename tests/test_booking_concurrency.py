import pytest
from fastapi import status
from datetime import datetime, timedelta
from app.models import Event, Show, User, UserRole, SeatStatus
from app.security import hash_password, create_access_token
import threading
import time


@pytest.fixture
def event_with_show(db):
    """Create event with show for testing"""
    event = Event(
        title="Concert",
        description="Test concert",
        category="Music",
        is_active=True
    )
    db.add(event)
    db.commit()
    
    show = Show(
        event_id=event.id,
        show_date=datetime.utcnow() + timedelta(days=1),
        total_seats=10,
        available_seats=10,
        price=100.0,
        is_active=True
    )
    db.add(show)
    db.commit()
    
    # Create seats
    from app.models import Seat
    for i in range(10):
        seat = Seat(
            show_id=show.id,
            seat_number=f"A{i+1}",
            status=SeatStatus.AVAILABLE
        )
        db.add(seat)
    db.commit()
    
    return event, show


def test_concurrent_seat_locking(client, db, event_with_show, user_token):
    """Test concurrent seat locking doesn't cause double booking"""
    event, show = event_with_show
    
    # Get available seats
    response = client.get(
        f"/api/seats/show/{show.id}",
        headers={"Authorization": f"Bearer {user_token}"}
    )
    assert response.status_code == status.HTTP_200_OK
    seats = response.json()["seats"]
    seat_ids = [s["id"] for s in seats[:2]]
    
    # Attempt concurrent locking of same seats
    results = []
    
    def lock_seats():
        response = client.post(
            "/api/bookings/lock-seats",
            json={"show_id": show.id, "seat_ids": seat_ids},
            headers={"Authorization": f"Bearer {user_token}"}
        )
        results.append(response.status_code)
    
    threads = [threading.Thread(target=lock_seats) for _ in range(2)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    
    # One should succeed, one should fail
    assert status.HTTP_201_CREATED in results
    assert status.HTTP_409_CONFLICT in results


def test_seat_lock_expiry(client, db, event_with_show, user_token):
    """Test that locked seats are released after expiry"""
    event, show = event_with_show
    
    # Get available seats
    response = client.get(
        f"/api/seats/show/{show.id}",
        headers={"Authorization": f"Bearer {user_token}"}
    )
    seats = response.json()["seats"]
    seat_ids = [s["id"] for s in seats[:1]]
    
    # Lock seats
    response = client.post(
        "/api/bookings/lock-seats",
        json={"show_id": show.id, "seat_ids": seat_ids},
        headers={"Authorization": f"Bearer {user_token}"}
    )
    assert response.status_code == status.HTTP_201_CREATED
    booking_id = response.json()["booking_id"]
    
    # Verify seats are locked
    response = client.get(
        f"/api/seats/show/{show.id}",
        headers={"Authorization": f"Bearer {user_token}"}
    )
    available_before = len(response.json()["seats"])
    
    # Simulate lock expiry by updating database
    from app.models import Booking
    from datetime import datetime, timedelta
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    booking.created_at = datetime.utcnow() - timedelta(seconds=301)
    db.commit()
    
    # Cleanup expired locks
    from app.services import BookingService
    service = BookingService(db)
    released = service.cleanup_expired_locks(show.id)
    assert released == 1
    
    # Verify seats are available again
    response = client.get(
        f"/api/seats/show/{show.id}",
        headers={"Authorization": f"Bearer {user_token}"}
    )
    available_after = len(response.json()["seats"])
    assert available_after > available_before


def test_booking_confirmation_within_lock_period(client, db, event_with_show, user_token):
    """Test booking confirmation within lock period succeeds"""
    event, show = event_with_show
    
    # Get available seats
    response = client.get(
        f"/api/seats/show/{show.id}",
        headers={"Authorization": f"Bearer {user_token}"}
    )
    seats = response.json()["seats"]
    seat_ids = [s["id"] for s in seats[:1]]
    
    # Lock seats
    response = client.post(
        "/api/bookings/lock-seats",
        json={"show_id": show.id, "seat_ids": seat_ids},
        headers={"Authorization": f"Bearer {user_token}"}
    )
    assert response.status_code == status.HTTP_201_CREATED
    booking_id = response.json()["booking_id"]
    
    # Confirm booking
    response = client.post(
        "/api/bookings/confirm",
        json={"booking_id": booking_id},
        headers={"Authorization": f"Bearer {user_token}"}
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["status"] == "confirmed"


def test_prevent_double_booking(client, db, event_with_show, user_token):
    """Test that same seat cannot be booked twice"""
    event, show = event_with_show
    
    # Get available seats
    response = client.get(
        f"/api/seats/show/{show.id}",
        headers={"Authorization": f"Bearer {user_token}"}
    )
    seats = response.json()["seats"]
    seat_id = seats[0]["id"]
    
    # First booking
    response = client.post(
        "/api/bookings/lock-seats",
        json={"show_id": show.id, "seat_ids": [seat_id]},
        headers={"Authorization": f"Bearer {user_token}"}
    )
    assert response.status_code == status.HTTP_201_CREATED
    booking_id_1 = response.json()["booking_id"]
    
    # Confirm first booking
    response = client.post(
        "/api/bookings/confirm",
        json={"booking_id": booking_id_1},
        headers={"Authorization": f"Bearer {user_token}"}
    )
    assert response.status_code == status.HTTP_200_OK
    
    # Try to book same seat again
    response = client.post(
        "/api/bookings/lock-seats",
        json={"show_id": show.id, "seat_ids": [seat_id]},
        headers={"Authorization": f"Bearer {user_token}"}
    )
    assert response.status_code == status.HTTP_409_CONFLICT
