"""
Integration tests for Assignment API endpoints
"""

import pytest
from datetime import date
from unittest.mock import patch

from app.core.dependencies import get_current_user


@pytest.fixture(autouse=True)
def mock_auth(mock_current_user):
    """Mock authentication for all tests"""
    with patch.object(get_current_user, "__call__", return_value=mock_current_user):
        yield


class TestAssignmentEndpoints:
    """Test Assignment endpoints"""

    def test_list_assignments_empty(self, client, auth_headers):
        """Test listing assignments when none exist"""
        response = client.get("/api/v1/assets/assignments/", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_assign_asset(self, client, sample_asset, auth_headers):
        """Test assigning an asset to a user"""
        assignment_data = {
            "user_id": 2,
            "department_id": 1,
            "assigned_date": str(date.today()),
            "notes": "Test assignment",
        }

        response = client.post(
            f"/api/v1/assets/{sample_asset.id}/assign",
            json=assignment_data,
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["asset_id"] == sample_asset.id
        assert data["user_id"] == 2
        assert data["status"] == "active"
        assert "id" in data

    def test_assign_already_assigned_asset(
        self, client, db_session, sample_asset, auth_headers
    ):
        """Test assigning an already assigned asset"""
        from app.models.assignment import AssetAssignment, AssignmentStatus

        # Create an active assignment
        assignment = AssetAssignment(
            asset_id=sample_asset.id,
            user_id=2,
            department_id=1,
            assigned_date=date.today(),
            assigned_by=1,
            status=AssignmentStatus.ACTIVE,
        )
        db_session.add(assignment)
        db_session.commit()

        # Try to assign to another user
        assignment_data = {
            "user_id": 3,
            "department_id": 1,
            "assigned_date": str(date.today()),
        }

        response = client.post(
            f"/api/v1/assets/{sample_asset.id}/assign",
            json=assignment_data,
            headers=auth_headers,
        )

        # Should fail
        assert response.status_code == 400
        assert "already assigned" in response.json()["detail"].lower()

    def test_return_asset(self, client, db_session, sample_asset, auth_headers):
        """Test returning an assigned asset"""
        from app.models.assignment import AssetAssignment, AssignmentStatus

        # Create an active assignment
        assignment = AssetAssignment(
            asset_id=sample_asset.id,
            user_id=2,
            department_id=1,
            assigned_date=date.today(),
            assigned_by=1,
            status=AssignmentStatus.ACTIVE,
        )
        db_session.add(assignment)
        db_session.commit()

        # Return the asset
        return_data = {
            "returned_date": str(date.today()),
            "return_condition": "good",
            "return_notes": "Returned in good condition",
        }

        response = client.post(
            f"/api/v1/assets/{sample_asset.id}/return",
            json=return_data,
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "returned"
        assert data["return_condition"] == "good"
        assert data["returned_date"] is not None

    def test_return_unassigned_asset(self, client, sample_asset, auth_headers):
        """Test returning an asset that isn't assigned"""
        return_data = {"returned_date": str(date.today()), "return_condition": "good"}

        response = client.post(
            f"/api/v1/assets/{sample_asset.id}/return",
            json=return_data,
            headers=auth_headers,
        )

        # Should fail
        assert response.status_code == 400

    def test_list_assignments_with_filter(
        self, client, db_session, sample_asset, auth_headers
    ):
        """Test listing assignments with status filter"""
        from app.models.assignment import AssetAssignment, AssignmentStatus

        # Create assignments with different statuses
        assignment1 = AssetAssignment(
            asset_id=sample_asset.id,
            user_id=2,
            department_id=1,
            assigned_date=date.today(),
            assigned_by=1,
            status=AssignmentStatus.ACTIVE,
        )
        db_session.add(assignment1)
        db_session.commit()

        # Test filtering by status
        response = client.get(
            "/api/v1/assets/assignments/?status=active", headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert all(a["status"] == "active" for a in data)

    def test_get_asset_history(self, client, db_session, sample_asset, auth_headers):
        """Test getting assignment history for an asset"""
        from app.models.assignment import AssetAssignment, AssignmentStatus

        # Create multiple assignments
        for i in range(3):
            assignment = AssetAssignment(
                asset_id=sample_asset.id,
                user_id=i + 2,
                department_id=1,
                assigned_date=date.today(),
                assigned_by=1,
                status=AssignmentStatus.RETURNED if i < 2 else AssignmentStatus.ACTIVE,
            )
            db_session.add(assignment)
        db_session.commit()

        response = client.get(
            f"/api/v1/assets/{sample_asset.id}/history", headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 3


class TestAssignmentValidation:
    """Test assignment data validation"""

    def test_assign_missing_user_id(self, client, sample_asset, auth_headers):
        """Test assigning without user_id"""
        assignment_data = {
            "department_id": 1,
            "assigned_date": str(date.today()),
            # Missing user_id
        }

        response = client.post(
            f"/api/v1/assets/{sample_asset.id}/assign",
            json=assignment_data,
            headers=auth_headers,
        )

        assert response.status_code == 422

    def test_assign_invalid_date(self, client, sample_asset, auth_headers):
        """Test assigning with invalid date"""
        assignment_data = {
            "user_id": 2,
            "department_id": 1,
            "assigned_date": "invalid-date",
        }

        response = client.post(
            f"/api/v1/assets/{sample_asset.id}/assign",
            json=assignment_data,
            headers=auth_headers,
        )

        assert response.status_code == 422

    def test_return_missing_condition(
        self, client, db_session, sample_asset, auth_headers
    ):
        """Test returning without condition"""
        from app.models.assignment import AssetAssignment, AssignmentStatus

        # Create an active assignment
        assignment = AssetAssignment(
            asset_id=sample_asset.id,
            user_id=2,
            department_id=1,
            assigned_date=date.today(),
            assigned_by=1,
            status=AssignmentStatus.ACTIVE,
        )
        db_session.add(assignment)
        db_session.commit()

        return_data = {
            "returned_date": str(date.today())
            # Missing return_condition
        }

        response = client.post(
            f"/api/v1/assets/{sample_asset.id}/return",
            json=return_data,
            headers=auth_headers,
        )

        assert response.status_code == 422
