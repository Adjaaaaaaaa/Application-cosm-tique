# BeautyScan Test Suite

This directory contains comprehensive tests for the BeautyScan application after its refactoring to Clean Architecture.

## Test Structure

```
tests/
├── unit/                          # Unit tests
│   ├── core/                      # Domain layer tests
│   │   ├── entities/              # Entity tests
│   │   │   ├── test_user.py       # User entity tests
│   │   │   ├── test_profile.py    # UserProfile entity tests
│   │   │   └── test_scan.py       # Scan entity tests
│   │   └── value_objects/         # Value object tests
│   │       ├── test_skin_type.py  # SkinType tests
│   │       ├── test_age_range.py  # AgeRange tests
│   │       ├── test_safety_score.py # SafetyScore tests
│   │       └── test_ingredient.py # Ingredient tests
│   ├── usecases/                  # Use case tests
│   │   ├── test_get_user_profile.py      # GetUserProfileUseCase tests
│   │   ├── test_get_user_allergies.py    # GetUserAllergiesUseCase tests
│   │   └── test_format_profile_for_ai.py # FormatProfileForAIUseCase tests
│   └── infrastructure/            # Infrastructure tests
│       └── test_django_repositories.py   # Django repository tests
├── integration/                   # Integration tests
│   └── apps/                      # Django app tests
│       ├── test_accounts_integration.py  # Accounts app tests
│       ├── test_scans_integration.py     # Scans app tests
│       └── test_payments_integration.py  # Payments app tests
├── conftest.py                    # Pytest configuration and fixtures
├── pytest.ini                    # Pytest settings
└── README.md                      # This file
```

## Running Tests

### Prerequisites

Make sure you have the required dependencies installed:

```bash
pip install pytest pytest-django
```

### Running All Tests

```bash
# From the project root
python -m pytest tests/

# Or using Django's test runner
python manage.py test
```

### Running Specific Test Categories

```bash
# Unit tests only
python -m pytest tests/unit/ -m unit

# Integration tests only
python -m pytest tests/integration/ -m integration

# Domain layer tests
python -m pytest tests/unit/core/

# Use case tests
python -m pytest tests/unit/usecases/

# Infrastructure tests
python -m pytest tests/unit/infrastructure/
```

### Running Specific Test Files

```bash
# Test specific entities
python -m pytest tests/unit/core/entities/test_user.py

# Test specific use cases
python -m pytest tests/unit/usecases/test_get_user_profile.py

# Test specific apps
python -m pytest tests/integration/apps/test_accounts_integration.py
```

### Running Tests with Coverage

```bash
# Install coverage
pip install coverage

# Run tests with coverage
coverage run --source='.' -m pytest tests/
coverage report
coverage html
```

## Test Categories

### Unit Tests

Unit tests focus on testing individual components in isolation:

- **Domain Entities**: Test business logic, validation, and behavior
- **Value Objects**: Test validation, equality, and immutability
- **Use Cases**: Test application logic with mocked dependencies
- **Infrastructure**: Test repository implementations with database

### Integration Tests

Integration tests verify that components work together correctly:

- **Django Apps**: Test views, forms, and endpoints
- **Database Integration**: Test actual database operations
- **Template Rendering**: Test HTML template rendering
- **Static Files**: Test CSS and JavaScript loading

## Test Data and Fixtures

The test suite includes several fixtures for common test data:

- `sample_user`: A sample User domain entity
- `sample_profile`: A sample UserProfile domain entity
- `sample_scan`: A sample Scan domain entity
- `django_user`: A Django User instance
- `django_profile`: A Django UserProfile instance
- `django_scan`: A Django Scan instance
- Mock repositories for unit testing

## Test Configuration

### Pytest Configuration

The `pytest.ini` file configures pytest for Django testing:

- Django settings module
- Test discovery patterns
- Markers for test categorization
- Warning filters

### Django Test Settings

Tests use the development settings (`config.settings.dev`) with:

- In-memory SQLite database for speed
- Disabled migrations for faster test execution
- Test-specific logging configuration

## Writing New Tests

### Unit Tests

When writing unit tests:

1. Use `unittest.TestCase` or `pytest` functions
2. Mock external dependencies
3. Test one thing at a time
4. Use descriptive test names
5. Include both positive and negative test cases

Example:

```python
def test_create_user_with_valid_data(self):
    """Test creating user with valid data."""
    user = User(
        user_id=1,
        username='testuser',
        email='test@example.com'
    )
    
    self.assertEqual(user.id, 1)
    self.assertEqual(user.username, 'testuser')
```

### Integration Tests

When writing integration tests:

1. Use Django's `TestCase` for database tests
2. Test complete user workflows
3. Verify template rendering
4. Check HTTP status codes and responses
5. Test authentication and permissions

Example:

```python
def test_profile_page_accessible_when_logged_in(self):
    """Test that profile page is accessible when logged in."""
    self.client.login(username='testuser', password='testpass123')
    response = self.client.get('/profile/')
    
    self.assertEqual(response.status_code, 200)
    self.assertContains(response, 'testuser')
```

## Test Best Practices

1. **Isolation**: Each test should be independent
2. **Clarity**: Use descriptive test names and docstrings
3. **Coverage**: Test both happy path and edge cases
4. **Performance**: Keep tests fast and efficient
5. **Maintenance**: Keep tests up to date with code changes

## Troubleshooting

### Common Issues

1. **Import Errors**: Make sure the project root is in the Python path
2. **Database Issues**: Ensure test database is properly configured
3. **Fixture Errors**: Check that fixtures are properly defined
4. **Permission Issues**: Verify file permissions for test files

### Debug Mode

Run tests in verbose mode for more information:

```bash
python -m pytest tests/ -v
```

### Test Database

If you encounter database issues, you can reset the test database:

```bash
python manage.py test --keepdb
```

## Contributing

When adding new tests:

1. Follow the existing test structure
2. Add appropriate docstrings
3. Use meaningful test names
4. Include both positive and negative cases
5. Update this README if needed

## Continuous Integration

The test suite is designed to run in CI/CD environments:

- Fast execution with in-memory database
- No external dependencies
- Clear error reporting
- Coverage reporting
