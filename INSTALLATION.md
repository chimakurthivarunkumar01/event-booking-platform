# Installation Guide

## Prerequisites

- Python 3.8 or higher
- Node.js 16 or higher
- npm or yarn package manager
- Git for version control

## Backend Installation

### 1. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 2. Environment Configuration

Create a `.env` file in the project root:

```bash
cp .env.example .env
```

Edit `.env` with your configuration:

```
DATABASE_URL=sqlite:///./event_booking.db
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
ENVIRONMENT=development
DEBUG=True
SEAT_LOCK_DURATION=300
```

### 3. Start Backend Server

```bash
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

API documentation: `http://localhost:8000/api/docs`

## Frontend Installation

### 1. Navigate to Frontend Directory

```bash
cd frontend
```

### 2. Install Dependencies

```bash
npm install
```

### 3. Start Development Server

```bash
npm run dev
```

The application will be available at `http://localhost:3000`

## Verification

### Backend Health Check

```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "environment": "development"
}
```

### Frontend Verification

Open `http://localhost:3000` in your browser and verify:
- Home page loads with animations
- Navigation between pages works
- All UI elements are visible

## Production Build

### Frontend Production Build

```bash
cd frontend
npm run build
```

Output will be in `frontend/dist/`

### Backend Production Deployment

```bash
pip install gunicorn
gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app
```

## Troubleshooting

### Port Already in Use

**Backend:**
```bash
python -m uvicorn app.main:app --reload --port 8001
```

**Frontend:**
```bash
npm run dev -- --port 3001
```

### Module Not Found

Ensure all dependencies are installed:
```bash
pip install -r requirements.txt
npm install
```

### Database Issues

Delete the database file and restart:
```bash
rm event_booking.db
python -m uvicorn app.main:app --reload
```

## Next Steps

- Review API documentation at `http://localhost:8000/api/docs`
- Check `API_ENDPOINTS.md` for endpoint details
- Review `DATABASE_SCHEMA.md` for database structure
