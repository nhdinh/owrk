# Asset API Integration Tests

This directory contains comprehensive integration tests for the Asset API module.

## Test Structure

The test suite is organized into the following files:

### Test Files

1. **[conftest.py](conftest.py)** - Pytest configuration and fixtures
   - Database session management (SQLite in-memory)
   - Test client with dependency overrides
   - Authentication mocking
   - Sample data fixtures

2. **[test_integration_assets.py](test_integration_assets.py)** - Asset CRUD operations (14 tests)
   - Create, Read, Update, Delete assets
   - List with filters and pagination
   - QR code generation
   - Statistics endpoint
   - Validation tests

3. **[test_integration_categories.py](test_integration_categories.py)** - Category management (13 tests)
   - Category CRUD operations
   - Parent-child hierarchy
   - Duplicate code detection
   - Validation tests

4. **[test_integration_assignments.py](test_integration_assignments.py)** - Asset assignments (10 tests)
   - Assign assets to users
   - Return assets
   - Assignment history
   - Status filtering
   - Validation tests

5. **[test_integration_maintenance.py](test_integration_maintenance.py)** - Maintenance tracking (20 tests)
   - Create maintenance records
   - Update status workflow
   - Filter by status and asset
   - Different maintenance types (preventive, corrective, emergency, routine)
   - Status progression (pending → in_progress → completed)
   - Validation tests

## Test Coverage

Total integration tests: **57 tests** covering:
- ✅ Asset CRUD and lifecycle management
- ✅ Category hierarchy and management
- ✅ Assignment tracking and returns
- ✅ Maintenance record management
- ✅ Data validation
- ✅ Error handling
- ✅ Filtering and pagination

## Running Tests

### Install Test Dependencies

```bash
docker compose exec asset-api pip install -r requirements-test.txt
```

### Run All Tests

```bash
docker compose exec asset-api pytest tests/test_integration_* -v
```

### Run Specific Test File

```bash
docker compose exec asset-api pytest tests/test_integration_categories.py -v
```

### Run Specific Test

```bash
docker compose exec asset-api pytest tests/test_integration_categories.py::TestCategoryEndpoints::test_create_category -v
```

### Run with Coverage

```bash
docker compose exec asset-api pytest tests/test_integration_* --cov=app --cov-report=html
```

## Test Fixtures

### Database Fixtures

- `db_session` - In-memory SQLite database session (fresh for each test)
- `client` - FastAPI TestClient with overridden dependencies
- `sample_category` - Pre-created category for testing
- `sample_asset` - Pre-created asset for testing
- `sample_maintenance` - Pre-created maintenance record for testing

### Authentication

Authentication is handled via dependency override in the `client` fixture:
```python
app.dependency_overrides[get_current_user] = override_get_current_user
```

No actual JWT tokens are needed for tests.

## Known Limitations

1. **SQLite vs MySQL**: Tests use SQLite in-memory database instead of MySQL
   - Schema definitions are removed for compatibility
   - Some MySQL-specific features may behave differently

2. **Authentication**: Uses mocked authentication, not real JWT validation

3. **External Dependencies**:
   - QR code generation is tested but not deeply
   - File uploads are not comprehensively tested
   - RabbitMQ event publishing is not tested

## Test Patterns

### Standard Test Structure

```python
def test_operation_name(self, client, fixture1, fixture2):
    """Test description"""
    # Arrange
    test_data = {...}

    # Act
    response = client.post("/api/v1/endpoint", json=test_data)

    # Assert
    assert response.status_code == 201
    data = response.json()
    assert data["field"] == "expected_value"
```

### Error Handling Tests

```python
def test_error_condition(self, client):
    """Test error handling"""
    response = client.get("/api/v1/nonexistent/999")
    assert response.status_code == 404
```

### Validation Tests

```python
def test_invalid_data(self, client):
    """Test data validation"""
    invalid_data = {"field": "invalid_value"}
    response = client.post("/api/v1/endpoint", json=invalid_data)
    assert response.status_code == 422  # Validation error
```

## Future Improvements

1. Add end-to-end tests with real MySQL database
2. Add performance tests for pagination
3. Add concurrency tests for assignments
4. Add file upload tests
5. Add depreciation calculation tests
6. Add event publishing/consumption tests
7. Improve test data factories
8. Add API contract tests (OpenAPI validation)

## Maintenance

When adding new endpoints:
1. Add corresponding test cases to appropriate test file
2. Update fixture data if needed
3. Run tests to ensure no regressions
4. Update this README if new test patterns are introduced

## References

- [Pytest Documentation](https://docs.pytest.org/)
- [FastAPI Testing](https://fastapi.tiangolo.com/tutorial/testing/)
- [SQLAlchemy Testing](https://docs.sqlalchemy.org/en/14/orm/session_basics.html#when-do-i-construct-a-session-when-do-i-commit-it-and-when-do-i-close-it)
