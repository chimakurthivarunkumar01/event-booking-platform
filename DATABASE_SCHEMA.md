# Event Booking Platform - Database Schema

## Overview
Production-grade relational database design with proper indexing and relationships for an event booking system.

## Tables

### 1. Users
Stores user account information with role-based access control.

```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(100) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    role ENUM('user', 'admin') DEFAULT 'user',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_user_email ON users(email);
CREATE INDEX idx_user_username ON users(username);
```

**Fields:**
- `id`: Primary key
- `email`: Unique email for login
- `username`: Unique username
- `hashed_password`: Bcrypt hashed password
- `role`: User role (user/admin)
- `is_active`: Account status
- `created_at`: Account creation timestamp
- `updated_at`: Last update timestamp

---

### 2. Events
Stores event information (movies, concerts, sports, etc.).

```sql
CREATE TABLE events (
    id INTEGER PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description VARCHAR(1000),
    category VARCHAR(100) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_event_title ON events(title);
CREATE INDEX idx_event_is_active ON events(is_active);
```

**Fields:**
- `id`: Primary key
- `title`: Event name
- `description`: Event details
- `category`: Event category (Movie, Concert, Sports, etc.)
- `is_active`: Event visibility
- `created_at`: Creation timestamp
- `updated_at`: Last update timestamp

---

### 3. Shows
Stores specific date/time instances of events with seat information.

```sql
CREATE TABLE shows (
    id INTEGER PRIMARY KEY,
    event_id INTEGER NOT NULL,
    show_date TIMESTAMP NOT NULL,
    total_seats INTEGER NOT NULL,
    available_seats INTEGER NOT NULL,
    price FLOAT NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (event_id) REFERENCES events(id) ON DELETE CASCADE
);

CREATE INDEX idx_show_event_id ON shows(event_id);
CREATE INDEX idx_show_date ON shows(show_date);
CREATE INDEX idx_show_is_active ON shows(is_active);
```

**Fields:**
- `id`: Primary key
- `event_id`: Foreign key to events
- `show_date`: Date and time of the show
- `total_seats`: Total seats in the show
- `available_seats`: Currently available seats (denormalized for performance)
- `price`: Price per seat
- `is_active`: Show visibility
- `created_at`: Creation timestamp
- `updated_at`: Last update timestamp

---

### 4. Seats
Stores individual seat information with locking mechanism.

```sql
CREATE TABLE seats (
    id INTEGER PRIMARY KEY,
    show_id INTEGER NOT NULL,
    seat_number VARCHAR(10) NOT NULL,
    status ENUM('available', 'locked', 'booked') DEFAULT 'available',
    locked_by INTEGER,
    lock_timestamp TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (show_id) REFERENCES shows(id) ON DELETE CASCADE,
    FOREIGN KEY (locked_by) REFERENCES users(id)
);

CREATE INDEX idx_seat_show_id ON seats(show_id);
CREATE INDEX idx_seat_status ON seats(status);
CREATE INDEX idx_seat_locked_by ON seats(locked_by);
CREATE INDEX idx_seat_show_status ON seats(show_id, status);
```

**Fields:**
- `id`: Primary key
- `show_id`: Foreign key to shows
- `seat_number`: Seat identifier (e.g., A1, B5)
- `status`: Seat status (available/locked/booked)
- `locked_by`: User ID who locked the seat
- `lock_timestamp`: When the seat was locked
- `created_at`: Creation timestamp
- `updated_at`: Last update timestamp

**Concurrency Handling:**
- `status` field tracks seat state
- `locked_by` and `lock_timestamp` enable lock expiry detection
- Composite index on (show_id, status) for efficient queries

---

### 5. Bookings
Stores booking transactions with status tracking.

```sql
CREATE TABLE bookings (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL,
    show_id INTEGER NOT NULL,
    status ENUM('pending', 'confirmed', 'cancelled') DEFAULT 'pending',
    total_price FLOAT NOT NULL,
    seat_count INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    confirmed_at TIMESTAMP,
    cancelled_at TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (show_id) REFERENCES shows(id) ON DELETE CASCADE
);

CREATE INDEX idx_booking_user_id ON bookings(user_id);
CREATE INDEX idx_booking_show_id ON bookings(show_id);
CREATE INDEX idx_booking_status ON bookings(status);
CREATE INDEX idx_booking_user_status ON bookings(user_id, status);
```

**Fields:**
- `id`: Primary key
- `user_id`: Foreign key to users
- `show_id`: Foreign key to shows
- `status`: Booking status (pending/confirmed/cancelled)
- `total_price`: Total booking amount
- `seat_count`: Number of seats booked
- `created_at`: Booking creation timestamp
- `confirmed_at`: Confirmation timestamp
- `cancelled_at`: Cancellation timestamp
- `updated_at`: Last update timestamp

---

### 6. BookingSeats
Junction table linking bookings to seats (many-to-many).

```sql
CREATE TABLE booking_seats (
    id INTEGER PRIMARY KEY,
    booking_id INTEGER NOT NULL,
    seat_id INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (booking_id) REFERENCES bookings(id) ON DELETE CASCADE,
    FOREIGN KEY (seat_id) REFERENCES seats(id) ON DELETE CASCADE
);

CREATE INDEX idx_booking_seat_booking_id ON booking_seats(booking_id);
CREATE INDEX idx_booking_seat_seat_id ON booking_seats(seat_id);
```

**Fields:**
- `id`: Primary key
- `booking_id`: Foreign key to bookings
- `seat_id`: Foreign key to seats
- `created_at`: Creation timestamp

---

## Key Design Decisions

### 1. Denormalization
- `available_seats` in Shows table is denormalized for performance
- Updated atomically with seat status changes

### 2. Indexing Strategy
- Composite indexes on frequently queried combinations
- Separate indexes for filtering and sorting operations
- Foreign key indexes for join performance

### 3. Concurrency Control
- Database-level transactions ensure atomicity
- Row-level locking prevents race conditions
- Lock timestamp enables automatic expiry detection

### 4. Cascading Deletes
- Deleting an event cascades to shows and seats
- Deleting a show cascades to seats and bookings
- Maintains referential integrity

### 5. Timestamps
- All tables include `created_at` and `updated_at`
- Enables audit trails and sorting
- Bookings track confirmation and cancellation times

## Performance Considerations

### Query Optimization
1. **Available Seats Query**: Uses composite index (show_id, status)
2. **User Bookings**: Uses index on (user_id, status)
3. **Expired Locks**: Queries on (show_id, status, lock_timestamp)

### Scalability
- Indexes support pagination queries
- Denormalized available_seats reduces aggregation queries
- Proper foreign key constraints prevent orphaned records

## Backup & Recovery
- All tables support point-in-time recovery via timestamps
- Audit trail available through created_at/updated_at fields
- Booking history preserved even after cancellation
