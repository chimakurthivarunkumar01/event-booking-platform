# Deployment Guide

## Production Environment Setup

### Backend Deployment

#### Environment Variables

Create `.env` for production:

```
DATABASE_URL=postgresql://user:password@host:5432/event_booking
SECRET_KEY=your-production-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
ENVIRONMENT=production
DEBUG=False
SEAT_LOCK_DURATION=300
```

#### Using Gunicorn

```bash
pip install gunicorn
gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app
```

#### Using Docker

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ ./app/

CMD ["gunicorn", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "app.main:app"]
```

Build and run:
```bash
docker build -t event-booking-api .
docker run -p 8000:8000 event-booking-api
```

### Frontend Deployment

#### Build for Production

```bash
cd frontend
npm run build
```

Output: `frontend/dist/`

#### Deploy to Vercel

```bash
npm install -g vercel
vercel
```

#### Deploy to Netlify

```bash
npm install -g netlify-cli
netlify deploy --prod --dir=dist
```

#### Deploy to AWS S3 + CloudFront

```bash
aws s3 sync dist/ s3://your-bucket-name/
aws cloudfront create-invalidation --distribution-id YOUR_DIST_ID --paths "/*"
```

## Database Migration

### PostgreSQL Setup

```bash
# Create database
createdb event_booking

# Create user
createuser event_user
```

### Running Migrations

If using Alembic:
```bash
alembic upgrade head
```

## Monitoring

### Application Monitoring

- Set up error tracking (Sentry)
- Configure logging aggregation (ELK Stack)
- Monitor API response times
- Track database performance

### Health Checks

```bash
curl https://api.example.com/health
```

## Security Checklist

- [ ] HTTPS enabled
- [ ] CORS properly configured
- [ ] Rate limiting implemented
- [ ] Input validation active
- [ ] SQL injection prevention
- [ ] XSS protection enabled
- [ ] CSRF tokens implemented
- [ ] Dependencies updated
- [ ] Secrets not in code
- [ ] Database backups configured

## Performance Optimization

- Enable gzip compression
- Implement caching headers
- Use CDN for static assets
- Optimize database queries
- Implement pagination
- Use connection pooling

## Backup Strategy

- Daily database backups
- Version control for code
- Environment configuration backup
- Regular restore testing

## Rollback Procedure

1. Identify issue
2. Revert to previous version
3. Restore database backup if needed
4. Verify functionality
5. Document incident

## Scaling Considerations

- Horizontal scaling with load balancer
- Database replication
- Caching layer (Redis)
- CDN for static content
- Microservices architecture (future)

## Support and Maintenance

- Monitor error logs
- Track performance metrics
- Plan regular updates
- Security patches
- Dependency updates
