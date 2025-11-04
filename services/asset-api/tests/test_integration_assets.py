"""
Integration tests for Asset API endpoints
"""

import pytest
from decimal import Decimal
from datetime import date
from unittest.mock import patch

from app.core.dependencies import get_current_user


@pytest.fixture(autouse=True)
def mock_auth(mock_current_user):
    """Mock authentication for all tests"""
    with patch.object(get_current_user, "__call__", return_value=mock_current_user):
        yield


class TestAssetEndpoints:
    """Test Asset CRUD endpoints"""

    def test_create_asset(self, client, sample_category, auth_headers):
        """Test creating a new asset"""
        asset_data = {
            "asset_code": "LAP-TEST-001",
            "name": "Test Laptop",
            "category_id": sample_category.id,
            "asset_type": "FIXED_ASSET",
            "description": "Dell Latitude 5520",
            "purchase_price": "1299.99",
            "purchase_date": "2023-01-15",
            "created_by": 1,
        }

        response = client.post("/api/v1/assets/", json=asset_data, headers=auth_headers)

        assert response.status_code == 201
        data = response.json()
        assert data["asset_code"] == "LAP-TEST-001"
        assert data["name"] == "Test Laptop"
        assert data["status"] == "NEW"
        assert "id" in data
        assert "qr_code" in data

    def test_create_asset_duplicate_code(self, client, sample_asset, auth_headers):
        """Test creating asset with duplicate code fails"""
        asset_data = {
            "asset_code": sample_asset.asset_code,  # Duplicate
            "name": "Another Laptop",
            "category_id": sample_asset.category_id,
            "asset_type": "FIXED_ASSET",
            "purchase_price": "999.99",
            "purchase_date": "2023-01-15",
            "created_by": 1,
        }

        response = client.post("/api/v1/assets/", json=asset_data, headers=auth_headers)

        assert response.status_code == 400
        assert "already exists" in response.json()["detail"].lower()

    def test_list_assets(self, client, sample_asset, auth_headers):
        """Test listing assets"""
        response = client.get("/api/v1/assets/", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert "assets" in data
        assert len(data["assets"]) >= 1
        assert data["assets"][0]["asset_code"] == sample_asset.asset_code

    def test_list_assets_with_filters(self, client, sample_asset, auth_headers):
        """Test listing assets with status filter"""
        response = client.get("/api/v1/assets/?status=NEW", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert all(asset["status"] == "NEW" for asset in data["assets"])

    def test_get_asset(self, client, sample_asset, auth_headers):
        """Test getting a single asset"""
        response = client.get(f"/api/v1/assets/{sample_asset.id}", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == sample_asset.id
        assert data["asset_code"] == sample_asset.asset_code
        assert data["name"] == sample_asset.name

    def test_get_asset_not_found(self, client, auth_headers):
        """Test getting non-existent asset"""
        response = client.get("/api/v1/assets/99999", headers=auth_headers)

        assert response.status_code == 404

    def test_update_asset(self, client, sample_asset, auth_headers):
        """Test updating an asset"""
        update_data = {
            "name": "Updated Laptop Name",
            "description": "Updated description",
        }

        response = client.put(
            f"/api/v1/assets/{sample_asset.id}", json=update_data, headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Laptop Name"
        assert data["description"] == "Updated description"
        assert data["asset_code"] == sample_asset.asset_code  # Unchanged

    def test_delete_asset(self, client, sample_asset, auth_headers):
        """Test deleting an asset"""
        response = client.delete(
            f"/api/v1/assets/{sample_asset.id}", headers=auth_headers
        )

        assert response.status_code == 204

        # Verify asset is deleted
        get_response = client.get(
            f"/api/v1/assets/{sample_asset.id}", headers=auth_headers
        )
        assert get_response.status_code == 404

    def test_get_asset_qrcode(self, client, sample_asset, auth_headers):
        """Test getting asset QR code"""
        response = client.get(
            f"/api/v1/assets/{sample_asset.id}/qrcode", headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert "qr_code" in data
        assert "asset_code" in data
        assert data["asset_code"] == sample_asset.asset_code

    def test_get_asset_statistics(self, client, sample_asset, auth_headers):
        """Test getting asset statistics"""
        response = client.get("/api/v1/assets/statistics/summary", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert "total_assets" in data
        assert "by_status" in data
        assert "by_type" in data


class TestAssetValidation:
    """Test asset data validation"""

    def test_create_asset_missing_required_fields(self, client, auth_headers):
        """Test creating asset without required fields"""
        asset_data = {
            "name": "Test Laptop"
            # Missing asset_code, category_id, etc.
        }

        response = client.post("/api/v1/assets/", json=asset_data, headers=auth_headers)

        assert response.status_code == 422  # Validation error

    def test_create_asset_invalid_price(self, client, sample_category, auth_headers):
        """Test creating asset with invalid price"""
        asset_data = {
            "asset_code": "LAP-001",
            "name": "Test Laptop",
            "category_id": sample_category.id,
            "asset_type": "FIXED_ASSET",
            "purchase_price": "-100",  # Negative price
            "purchase_date": "2023-01-15",
            "created_by": 1,
        }

        response = client.post("/api/v1/assets/", json=asset_data, headers=auth_headers)

        # Should either reject or handle gracefully
        assert response.status_code in [400, 422]

    def test_create_asset_invalid_date(self, client, sample_category, auth_headers):
        """Test creating asset with invalid date format"""
        asset_data = {
            "asset_code": "LAP-001",
            "name": "Test Laptop",
            "category_id": sample_category.id,
            "asset_type": "FIXED_ASSET",
            "purchase_price": "1299.99",
            "purchase_date": "invalid-date",
            "created_by": 1,
        }

        response = client.post("/api/v1/assets/", json=asset_data, headers=auth_headers)

        assert response.status_code == 422


class TestAssetPagination:
    """Test asset list pagination"""

    def test_list_assets_pagination(
        self, client, db_session, sample_category, auth_headers
    ):
        """Test asset listing with pagination"""
        from app.models.asset import Asset, AssetType, AssetStatus
        from decimal import Decimal

        # Create multiple assets
        for i in range(15):
            asset = Asset(
                asset_code=f"ASSET-{i:03d}",
                name=f"Asset {i}",
                category_id=sample_category.id,
                asset_type=AssetType.FIXED_ASSET,
                purchase_price=Decimal("100.00"),
                purchase_date=date(2023, 1, 1),
                status=AssetStatus.NEW,
                created_by=1,
            )
            db_session.add(asset)
        db_session.commit()

        # Test first page
        response = client.get(
            "/api/v1/assets/?page=1&page_size=10", headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data["assets"]) == 10
        assert data["total"] >= 15
        assert data["page"] == 1

        # Test second page
        response = client.get(
            "/api/v1/assets/?page=2&page_size=10", headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data["assets"]) >= 5
        assert data["page"] == 2
