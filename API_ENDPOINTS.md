# Event Booking Platform - API Endpoints

## Base URL
```
http://localhost:8000/api
```

## Authentication
All endpoints except `/auth/signup` and `/auth/login` require JWT token in Authorization header:
```
Authorization: Bearer <token>
```

---

## Authentication Endpoints

### 1. User Signup
**POST** `/auth/signup`

Register a new user account.

**Request:**
```json
{
  "email": "user@example.com",
  "username": "john_doe",
  "password": "SecurePass123"
}
```

**Response (201 Created):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "username": "john_doe",
    "role": "user",
    "is_active": true,
    "created_at": "2024-03-26T10:30:00"
  }
}
```

**Errors:**
- `409 Conflict`: Email or username already exists
- `422 Unprocessable Entity`: Invalid input (weak password, invalid email)

---

### 2. User Login
**POST** `/auth/login`

Authenticate user and get JWT token.

**Request:**
```json
{
  "email": "user@example.com",
  "password": "SecurePass123"
}
```

**Response (200 OK):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "username": "john_doe",
    "role": "user",
    "is_active": true,
    "created_at": "2024-03-26T10:30:00"
  }
}
```

**Errors:**
- `401 Unauthorized`: Invalid email or password

---

## Event Endpoints

### 3. Create Event (Admin Only)
**POST** `/events`

Create a new event.

**Request:**
```json
{
  "title": "Avengers: Endgame",
  "description": "Epic superhero movie",
  "category": "Movie"
}
```

**Response (201 Created):**
```json
{
  "id": 1,
  "title": "Avengers: Endgame",
  "description": "Epic superhero movie",
  "category": "Movie",
  "is_active": true,
  "created_at": "2024-03-26T10:30:00",
  "updated_at": "2024-03-26T10:30:00"
}
```

**Errors:**
- `403 Forbidden`: User is not admin

---

### 4. Get All Events
**GET** `/events?skip=0&limit=10`

Retrieve all active events with pagination.

**Response (200 OK):**
```json
{
  "total": 25,
  "skip": 0,
  "limit": 10,
  "items": [
    {
      "id": 1,
      "title": "Avengers: Endgame",
      "description": "Epic superhero movie",
      "category": "Movie",
      "is_active": true,
      "created_at": "2024-03-26T10:30:00",
      "updated_at": "2024-03-26T10:30:00"
    }
  ]
}
```

---

### 5. Get Event by Category
**GET** `/events/category/{category}?skip=0&limit=10`

Get events filtered by category.

**Response (200 OK):**
```json
{
  "total": 5,
  "skip": 0,
  "limit": 10,
  "items": [...]
}
```

---

### 6. Get Event Details
**GET** `/events/{event_id}`

Get event with all associated shows.

**Response (200 OK):**
```json
{
  "id": 1,
  "title": "Avengers: Endgame",
  "description": "Epic superhero movie",
  "category": "Movie",
  "is_active": true,
  "created_at": "2024-03-26T10:30:00",
  "updated_at": "2024-03-26T10:30:00",
  "shows": [
    {
      "id": 1,
      "event_id": 1,
      "show_date": "2024-04-01T18:00:00",
      "total_seats": 100,
      "available_seats": 45,
      "price": 250.0,
      "is_active": true,
      "created_at": "2024-03-26T10:30:00",
      "updated_at": "2024-03-26T10:30:00"
    }
  ]
}
```

---

### 7. Update Event (Admin Only)
**PUT** `/events/{event_id}`

Update event details.

**Request:**
```json
{
  "title": "Avengers: Endgame - Extended",
  "is_active": true
}
```

**Response (200 OK):**
```json
{
  "id": 1,
  "title": "Avengers: Endgame - Extended",
  "description": "Epic superhero movie",
  "category": "Movie",
  "is_active": true,
  "created_at": "2024-03-26T10:30:00",
  "updated_at": "2024-03-26T11:00:00"
}
```

---

### 8. Delete Event (Admin Only)
**DELETE** `/events/{event_id}`

Delete an event and all associated shows/bookings.

**Response (204 No Content)**

---

## Show Endpoints

### 9. Create Show (Admin Only)
**POST** `/shows`

Create a new show with seats.

**Request:**
```json
{
  "event_id": 1,
  "show_date": "2024-04-01T18:00:00",
  "total_seats": 100,
  "price": 250.0
}
```

**Response (201 Created):**
```json
{
  "id": 1,
  "event_id": 1,
  "show_date": "2024-04-01T18:00:00",
  "total_seats": 100,
  "available_seats": 100,
  "price": 250.0,
  "is_active": true,
  "created_at": "2024-03-26T10:30:00",
  "updated_at": "2024-03-26T10:30:00"
}
```

---

### 10. Get Show Details
**GET** `/shows/{show_id}`

Get show information.

**Response (200 OK):**
```json
{
  "id": 1,
  "event_id": 1,
  "show_date": "2024-04-01T18:00:00",
  "total_seats": 100,
  "available_seats": 45,
  "price": 250.0,
  "is_active": true,
  "created_at": "2024-03-26T10:30:00",
  "updated_at": "2024-03-26T10:30:00"
}
```

---

### 11. Get Shows by Event
**GET** `/shows/event/{event_id}?skip=0&limit=10`

Get all shows for an event.

**Response (200 OK):**
```json
{
  "total": 5,
  "skip": 0,
  "limit": 10,
  "items": [...]
}
```

---

### 12. Get Upcoming Shows
**GET** `/shows?skip=0&limit=10`

Get all upcoming shows.

**Response (200 OK):**
```json
{
  "total": 15,
  "skip": 0,
  "limit": 10,
  "items": [...]
}
```

---

## Seat Endpoints

### 13. Get Available Seats
**GET** `/seats/show/{show_id}`

Get all available seats for a show.

**Response (200 OK):**
```json
{
  "show_id": 1,
  "total_seats": 100,
  "available_count": 45,
  "locked_count": 10,
  "booked_count": 45,
  "seats": [
    {
      "id": 1,
      "seat_number": "A1",
      "status": "available",
      "locked_by": null,
      "lock_timestamp": null
    },
    {
      "id": 2,
      "seat_number": "A2",
      "status": "locked",
      "locked_by": 5,
      "lock_timestamp": "2024-03-26T10:35:00"
    }
  ]
}
```

---

## Booking Endpoints (CRITICAL)

### 14. Lock Seats
**POST** `/bookings/lock-seats`

Lock seats for booking (5-minute expiry). **MOST IMPORTANT ENDPOINT**

**Request:**
```json
{
  "show_id": 1,
  "seat_ids": [1, 2, 3]
}
```

**Response (201 Created):**
```json
{
  "booking_id": 42,
  "locked_seats": [
    {
      "id": 1,
      "seat_number": "A1",
      "status": "locked",
      "locked_by": 5,
      "lock_timestamp": "2024-03-26T10:35:00"
    },
    {
      "id": 2,
      "seat_number": "A2",
      "status": "locked",
      "locked_by": 5,
      "lock_timestamp": "2024-03-26T10:35:00"
    },
    {
      "id": 3,
      "seat_number": "A3",
      "status": "locked",
      "locked_by": 5,
      "lock_timestamp": "2024-03-26T10:35:00"
    }
  ],
  "lock_expiry": "2024-03-26T10:40:00",
  "total_price": 750.0
}
```

**Errors:**
- `409 Conflict`: Seat already booked/locked or concurrent access
- `400 Bad Request`: Invalid seat selection

**Concurrency Handling:**
- Uses database transactions to prevent race conditions
- Returns 409 if seats are already locked/booked
- Automatically releases locks after 5 minutes

---

### 15. Confirm Booking
**POST** `/bookings/confirm`

Confirm a pending booking (changes seats from LOCKED to BOOKED).

**Request:**
```json
{
  "booking_id": 42
}
```

**Response (200 OK):**
```json
{
  "id": 42,
  "user_id": 5,
  "show_id": 1,
  "status": "confirmed",
  "total_price": 750.0,
  "seat_count": 3,
  "created_at": "2024-03-26T10:35:00",
  "confirmed_at": "2024-03-26T10:36:00",
  "cancelled_at": null,
  "booking_seats": [
    {
      "id": 1,
      "seat_id": 1
    },
    {
      "id": 2,
      "seat_id": 2
    },
    {
      "id": 3,
      "seat_id": 3
    }
  ]
}
```

**Errors:**
- `400 Bad Request`: Lock expired or booking already confirmed
- `404 Not Found`: Booking not found

---

### 16. Cancel Booking
**POST** `/bookings/cancel`

Cancel a booking and release seats.

**Request:**
```json
{
  "booking_id": 42
}
```

**Response (200 OK):**
```json
{
  "id": 42,
  "user_id": 5,
  "show_id": 1,
  "status": "cancelled",
  "total_price": 750.0,
  "seat_count": 3,
  "created_at": "2024-03-26T10:35:00",
  "confirmed_at": "2024-03-26T10:36:00",
  "cancelled_at": "2024-03-26T10:37:00"
}
```

---

### 17. Get User Bookings
**GET** `/bookings?skip=0&limit=10`

Get all bookings for current user.

**Response (200 OK):**
```json
{
  "total": 5,
  "skip": 0,
  "limit": 10,
  "items": [
    {
      "id": 42,
      "user_id": 5,
      "show_id": 1,
      "status": "confirmed",
      "total_price": 750.0,
      "seat_count": 3,
      "created_at": "2024-03-26T10:35:00",
      "confirmed_at": "2024-03-26T10:36:00",
      "cancelled_at": null,
      "booking_seats": [...]
    }
  ]
}
```

---

### 18. Get Booking Details
**GET** `/bookings/{booking_id}`

Get specific booking details.

**Response (200 OK):**
```json
{
  "id": 42,
  "user_id": 5,
  "show_id": 1,
  "status": "confirmed",
  "total_price": 750.0,
  "seat_count": 3,
  "created_at": "2024-03-26T10:35:00",
  "confirmed_at": "2024-03-26T10:36:00",
  "cancelled_at": null,
  "booking_seats": [...]
}
```

---

## Health Check

### 19. Health Check
**GET** `/health`

Check API health status.

**Response (200 OK):**
```json
{
  "status": "healthy",
  "environment": "development"
}
```

---

## Error Responses

### Standard Error Format
```json
{
  "detail": "Error message describing what went wrong"
}
```

### Common HTTP Status Codes
- `200 OK`: Successful GET/PUT request
- `201 Created`: Successful POST request
- `204 No Content`: Successful DELETE request
- `400 Bad Request`: Invalid input or operation
- `401 Unauthorized`: Missing or invalid token
- `403 Forbidden`: Insufficient permissions (not admin)
- `404 Not Found`: Resource not found
- `409 Conflict`: Concurrency conflict or duplicate resource
- `422 Unprocessable Entity`: Validation error
- `500 Internal Server Error`: Server error

---

## Rate Limiting & Pagination

### Pagination Parameters
- `skip`: Number of records to skip (default: 0)
- `limit`: Number of records to return (default: 10, max: 100)

### Example Paginated Request
```
GET /api/events?skip=20&limit=10
```

Returns records 20-29 (10 records starting from position 20).
