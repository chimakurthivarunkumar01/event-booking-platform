# Event Booking Platform

A production-grade event booking system built with React and FastAPI, featuring real-time seat management, JWT authentication, and advanced concurrency handling.

## Overview

This project implements a complete event booking platform similar to BookMyShow. It demonstrates clean architecture principles, modern web development practices, and production-ready code patterns.

## Architecture

### Frontend
- **Framework**: React 18 with TypeScript support
- **Styling**: Tailwind CSS with custom animations
- **Animation**: Framer Motion for smooth UI transitions
- **Build Tool**: Vite for optimized development and production builds
- **Routing**: React Router v6 for client-side navigation

### Backend
- **Framework**: FastAPI with async/await support
- **Database**: SQLAlchemy ORM with SQLite
- **Authentication**: JWT-based token authentication
- **Validation**: Pydantic for request/response validation
- **Testing**: Pytest with async support

## Key Features

### Authentication & Authorization
- JWT-based authentication with refresh tokens
- Role-based access control (user/admin)
- Secure password hashing with bcrypt
- Token expiration and validation

### Booking System
- Real-time seat availability tracking
- Seat locking mechanism with 5-minute expiry
- Concurrency-safe booking with database transactions
- Prevention of double-booking through optimistic locking

### API Design
- RESTful API with 18 endpoints
- Comprehensive error handling
- Request validation with Pydantic schemas
- Interactive API documentation with Swagger UI

### Frontend Experience
- Responsive design for mobile, tablet, and desktop
- Smooth animations and transitions (60fps)
- Real-time booking summary updates
- Intuitive user navigation flow

## Project Structure

```
event-booking-platform/
├── app/
│   ├── main.py                 # FastAPI application entry point
│   ├── config.py               # Configuration management
│   ├── database.py             # Database connection and session
│   ├── models.py               # SQLAlchemy ORM models
│   ├── schemas.py              # Pydantic validation schemas
│   ├── security.py             # JWT authentication logic
│   ├── exceptions.py           # Custom exception classes
│   ├── routes/                 # API route handlers
│   │   ├── auth.py
│   │   ├── events.py
│   │   ├── shows.py
│   │   ├── seats.py
│   │   └── bookings.py
│   ├── services/               # Business logic layer
│   │   ├── auth_service.py
│   │   ├── event_service.py
│   │   ├── show_service.py
│   │   ├── seat_service.py
│   │   └── booking_service.py
│   └── repositories/           # Data access layer
│       ├── base_repository.py
│       ├── user_repository.py
│       ├── event_repository.py
│       ├── show_repository.py
│       ├── seat_repository.py
│       └── booking_repository.py
├── frontend/
│   ├── src/
│   │   ├── pages/              # Page components
│   │   ├── components/         # Reusable components
│   │   ├── utils/              # Utility functions
│   │   └── styles/             # Global styles
│   ├── package.json
│   ├── tailwind.config.js
│   └── vite.config.js
├── tests/
│   ├── test_auth.py
│   ├── test_booking_concurrency.py
│   └── conftest.py
├── requirements.txt
└── .env.example
```

## Installation

### Prerequisites
- Python 3.8+
- Node.js 16+
- npm or yarn

### Backend Setup

```bash
# Install Python dependencies
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env

# Run database migrations (if applicable)
# Database tables are created automatically on first run

# Start the development server
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

## API Documentation

### Authentication Endpoints
- `POST /auth/signup` - Register new user
- `POST /auth/login` - Authenticate user and receive JWT token

### Event Management
- `GET /events` - Retrieve all events with pagination
- `GET /events/{id}` - Get specific event details
- `POST /events` - Create new event (admin only)
- `PUT /events/{id}` - Update event (admin only)
- `DELETE /events/{id}` - Delete event (admin only)

### Show Management
- `GET /shows` - List all shows
- `GET /shows/{id}` - Get show details
- `POST /shows` - Create show (admin only)
- `PUT /shows/{id}` - Update show (admin only)
- `DELETE /shows/{id}` - Delete show (admin only)

### Seat Management
- `GET /seats/{show_id}` - Get available seats for a show
- `POST /seats` - Create seats for a show (admin only)

### Booking Operations
- `POST /bookings/lock-seats` - Lock seats with 5-minute expiry
- `POST /bookings/confirm` - Confirm booking after payment
- `GET /bookings/my-bookings` - Retrieve user's booking history
- `GET /bookings/{id}` - Get booking details
- `DELETE /bookings/{id}` - Cancel booking

Interactive API documentation available at `http://localhost:8000/api/docs`

## Database Schema

### Core Tables
- **users**: User accounts with authentication credentials
- **events**: Event catalog with metadata
- **shows**: Event instances with date/time information
- **seats**: Seat inventory with status tracking
- **bookings**: Booking records with pricing
- **booking_seats**: Junction table for booking-seat relationships

## Development

### Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_auth.py

# Run with coverage report
pytest --cov=app tests/

# Run concurrency tests
pytest tests/test_booking_concurrency.py -v
```

### Code Quality

The project follows PEP 8 style guidelines and includes:
- Type hints for better code clarity
- Comprehensive error handling
- Logging for debugging and monitoring
- Input validation at all layers

## Deployment

### Production Build

```bash
# Frontend
cd frontend
npm run build

# Backend
gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app
```

### Environment Configuration

Create `.env` file with required variables:
```
DATABASE_URL=postgresql://user:password@localhost:5432/event_booking
SECRET_KEY=your-secret-key-here
ENVIRONMENT=production
DEBUG=False
```

## Performance Considerations

- Database query optimization with proper indexing
- Connection pooling for database efficiency
- Frontend animations optimized for 60fps
- Lazy loading of components
- Caching strategies for frequently accessed data

## Security

- Password hashing with bcrypt
- JWT token-based authentication
- CORS configuration for cross-origin requests
- Input validation and sanitization
- SQL injection prevention through ORM
- Rate limiting recommendations for production

## License

MIT License - See LICENSE file for details

## Contact

For inquiries or support, please contact the development team.
