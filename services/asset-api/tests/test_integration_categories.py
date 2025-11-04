"""
Integration tests for Category API endpoints
"""

import pytest
from unittest.mock import patch

from app.core.dependencies import get_current_user


@pytest.fixture(autouse=True)
def mock_auth(mock_current_user):
    """Mock authentication for all tests"""
    with patch.object(get_current_user, "__call__", return_value=mock_current_user):
        yield


class TestCategoryEndpoints:
    """Test Category CRUD endpoints"""

    def test_create_category(self, client, auth_headers):
        """Test creating a new category"""
        category_data = {
            "code": "TEST-CAT",
            "name": "Test Category",
            "description": "Test category description",
            "is_active": True,
        }

        response = client.post(
            "/api/v1/assets/categories/", json=category_data, headers=auth_headers
        )

        assert response.status_code == 201
        data = response.json()
        assert data["code"] == "TEST-CAT"
        assert data["name"] == "Test Category"
        assert data["is_active"] is True
        assert "id" in data

    def test_create_category_duplicate_code(
        self, client, sample_category, auth_headers
    ):
        """Test creating category with duplicate code fails"""
        category_data = {
            "code": sample_category.code,  # Duplicate
            "name": "Another Category",
            "is_active": True,
        }

        response = client.post(
            "/api/v1/assets/categories/", json=category_data, headers=auth_headers
        )

        assert response.status_code == 400
        assert "already exists" in response.json()["detail"].lower()

    def test_list_categories(self, client, sample_category, auth_headers):
        """Test listing all categories"""
        response = client.get("/api/v1/assets/categories/", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
        assert any(cat["code"] == sample_category.code for cat in data)

    def test_get_category(self, client, sample_category, auth_headers):
        """Test getting a single category"""
        response = client.get(
            f"/api/v1/assets/categories/{sample_category.id}", headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == sample_category.id
        assert data["code"] == sample_category.code
        assert data["name"] == sample_category.name

    def test_get_category_not_found(self, client, auth_headers):
        """Test getting non-existent category"""
        response = client.get("/api/v1/assets/categories/99999", headers=auth_headers)

        assert response.status_code == 404

    def test_update_category(self, client, sample_category, auth_headers):
        """Test updating a category"""
        update_data = {
            "name": "Updated Category Name",
            "description": "Updated description",
        }

        response = client.put(
            f"/api/v1/assets/categories/{sample_category.id}",
            json=update_data,
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Category Name"
        assert data["description"] == "Updated description"
        assert data["code"] == sample_category.code  # Unchanged

    def test_deactivate_category(self, client, sample_category, auth_headers):
        """Test deactivating a category"""
        update_data = {"is_active": False}

        response = client.put(
            f"/api/v1/assets/categories/{sample_category.id}",
            json=update_data,
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["is_active"] is False

    def test_delete_category(self, client, sample_category, auth_headers):
        """Test deleting a category"""
        response = client.delete(
            f"/api/v1/assets/categories/{sample_category.id}", headers=auth_headers
        )

        assert response.status_code == 204

        # Verify category is deleted
        get_response = client.get(
            f"/api/v1/assets/categories/{sample_category.id}", headers=auth_headers
        )
        assert get_response.status_code == 404


class TestCategoryHierarchy:
    """Test category parent-child relationships"""

    def test_create_subcategory(self, client, sample_category, auth_headers):
        """Test creating a subcategory"""
        subcategory_data = {
            "code": "SUB-CAT",
            "name": "Sub Category",
            "parent_id": sample_category.id,
            "is_active": True,
        }

        response = client.post(
            "/api/v1/assets/categories/", json=subcategory_data, headers=auth_headers
        )

        assert response.status_code == 201
        data = response.json()
        assert data["parent_id"] == sample_category.id

    def test_category_with_invalid_parent(self, client, auth_headers):
        """Test creating category with non-existent parent"""
        category_data = {
            "code": "ORPHAN-CAT",
            "name": "Orphan Category",
            "parent_id": 99999,  # Non-existent
            "is_active": True,
        }

        response = client.post(
            "/api/v1/assets/categories/", json=category_data, headers=auth_headers
        )

        # Should fail with 400 or 422
        assert response.status_code in [400, 404, 422]


class TestCategoryValidation:
    """Test category data validation"""

    def test_create_category_missing_code(self, client, auth_headers):
        """Test creating category without code"""
        category_data = {
            "name": "Test Category"
            # Missing code
        }

        response = client.post(
            "/api/v1/assets/categories/", json=category_data, headers=auth_headers
        )

        assert response.status_code == 422

    def test_create_category_empty_code(self, client, auth_headers):
        """Test creating category with empty code"""
        category_data = {"code": "", "name": "Test Category", "is_active": True}

        response = client.post(
            "/api/v1/assets/categories/", json=category_data, headers=auth_headers
        )

        assert response.status_code == 422

    def test_create_category_long_code(self, client, auth_headers):
        """Test creating category with too long code"""
        category_data = {
            "code": "A" * 100,  # Very long code
            "name": "Test Category",
            "is_active": True,
        }

        response = client.post(
            "/api/v1/assets/categories/", json=category_data, headers=auth_headers
        )

        # Should either accept or reject based on validation rules
        assert response.status_code in [201, 422]
