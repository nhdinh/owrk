"""
Pytest configuration and fixtures for integration tests
"""

import sys
import os

# Set TESTING environment variable before importing app
os.environ["TESTING"] = "true"

# Add parent directory to path to import app module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.core.database import Base, get_db
from app.models.asset import Asset
from app.models.category import AssetCategory
from app.models.assignment import AssetAssignment
from app.models.maintenance import MaintenanceRecord

# Use in-memory SQLite for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session():
    """Create a fresh database for each test"""
    # Remove schema from table metadata for SQLite
    for table in Base.metadata.tables.values():
        table.schema = None

    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    """Create a test client with database override and auth bypass"""
    from app.core.dependencies import get_current_user

    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    def override_get_current_user():
        """Override authentication to return a mock user"""
        return {"id": 1, "email": "admin@example.com", "role": "admin"}

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = override_get_current_user

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture
def auth_headers():
    """Mock authentication headers - not actually needed since we override dependency"""
    return {"Authorization": "Bearer test_token"}


@pytest.fixture
def mock_current_user():
    """Mock current user for authentication"""
    return {"id": 1, "email": "admin@example.com", "role": "admin"}


@pytest.fixture
def sample_category(db_session):
    """Create a sample category in the database"""
    from app.models.category import AssetCategory

    category = AssetCategory(
        code="IT-HW",
        name="IT Hardware",
        description="Computer equipment",
        is_active=True,
    )
    db_session.add(category)
    db_session.commit()
    db_session.refresh(category)
    return category


@pytest.fixture
def sample_asset(db_session, sample_category):
    """Create a sample asset in the database"""
    from app.models.asset import Asset, AssetType, AssetStatus
    from decimal import Decimal
    from datetime import date

    asset = Asset(
        asset_code="LAP-001",
        name="Test Laptop",
        category_id=sample_category.id,
        asset_type=AssetType.FIXED_ASSET,
        description="Dell Latitude 5520",
        purchase_price=Decimal("1299.99"),
        purchase_date=date(2023, 1, 15),
        status=AssetStatus.NEW,
        created_by=1,
    )
    db_session.add(asset)
    db_session.commit()
    db_session.refresh(asset)
    return asset
