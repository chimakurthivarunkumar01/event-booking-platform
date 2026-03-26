# Contributing Guidelines

## Code Standards

### Python Code Style

- Follow PEP 8 guidelines
- Use type hints for function parameters and return values
- Maximum line length: 100 characters
- Use meaningful variable and function names

Example:
```python
def get_available_seats(show_id: int, db: Session) -> List[Seat]:
    """Retrieve available seats for a specific show."""
    return db.query(Seat).filter(
        Seat.show_id == show_id,
        Seat.status == SeatStatus.AVAILABLE
    ).all()
```

### JavaScript/React Code Style

- Use ES6+ syntax
- Use functional components with hooks
- Use meaningful component names
- Add PropTypes or TypeScript types

Example:
```javascript
const EventCard = ({ event, onBookClick }) => {
  return (
    <div className="event-card">
      <h3>{event.title}</h3>
      <button onClick={() => onBookClick(event.id)}>
        Book Now
      </button>
    </div>
  );
};
```

## Commit Messages

Use clear, descriptive commit messages:

```
feat: Add seat locking mechanism
fix: Resolve JWT token validation issue
docs: Update API documentation
refactor: Simplify booking service logic
test: Add concurrency tests for bookings
```

Format: `<type>: <description>`

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `refactor`: Code refactoring
- `test`: Test additions
- `chore`: Build/dependency updates

## Testing

### Running Tests

```bash
# All tests
pytest

# Specific test file
pytest tests/test_auth.py

# With coverage
pytest --cov=app tests/

# Verbose output
pytest -v
```

### Writing Tests

- Use descriptive test names
- Test both success and failure cases
- Mock external dependencies
- Keep tests isolated and independent

Example:
```python
def test_lock_seats_success(db: Session):
    """Test successful seat locking."""
    show = create_test_show(db)
    seats = create_test_seats(db, show.id)
    
    result = lock_seats(show.id, [s.id for s in seats], db)
    
    assert result.status == "locked"
    assert len(result.seats) == len(seats)
```

## Pull Request Process

1. Create a feature branch: `git checkout -b feature/your-feature`
2. Make your changes
3. Write or update tests
4. Update documentation if needed
5. Commit with clear messages
6. Push to your fork
7. Create a pull request with description

## Code Review Checklist

- [ ] Code follows style guidelines
- [ ] Tests are included and passing
- [ ] Documentation is updated
- [ ] No breaking changes
- [ ] Performance impact considered
- [ ] Security implications reviewed

## Performance Considerations

- Optimize database queries with proper indexing
- Use pagination for large datasets
- Implement caching where appropriate
- Monitor API response times
- Profile frontend animations

## Security Guidelines

- Never commit sensitive data (.env files)
- Validate all user inputs
- Use parameterized queries
- Implement proper authentication
- Follow OWASP guidelines
- Keep dependencies updated

## Documentation

- Update README.md for major changes
- Add docstrings to functions
- Document API endpoints
- Include usage examples
- Update CHANGELOG if applicable

## Questions or Issues?

- Check existing issues and documentation
- Create a new issue with detailed description
- Include steps to reproduce for bugs
- Provide context and environment details
