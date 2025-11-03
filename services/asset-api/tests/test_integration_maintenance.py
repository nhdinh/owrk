"""
Integration tests for Maintenance API endpoints
"""

import pytest
from datetime import date
from decimal import Decimal
from unittest.mock import patch

from app.core.dependencies import get_current_user


@pytest.fixture(autouse=True)
def mock_auth(mock_current_user):
    """Mock authentication for all tests"""
    with patch.object(get_current_user, '__call__', return_value=mock_current_user):
        yield


@pytest.fixture
def sample_maintenance(db_session, sample_asset):
    """Create a sample maintenance record"""
    from app.models.maintenance import MaintenanceRecord

    maintenance = MaintenanceRecord(
        asset_id=sample_asset.id,
        maintenance_type="routine",
        maintenance_date=date.today(),
        cost=Decimal("150.00"),
        technician="John Doe",
        description="Routine maintenance check",
        status="pending"
    )
    db_session.add(maintenance)
    db_session.commit()
    db_session.refresh(maintenance)
    return maintenance


class TestMaintenanceEndpoints:
    """Test Maintenance CRUD endpoints"""

    def test_create_maintenance(self, client, sample_asset, auth_headers):
        """Test creating a new maintenance record"""
        maintenance_data = {
            "asset_id": sample_asset.id,
            "maintenance_type": "preventive",
            "maintenance_date": str(date.today()),
            "cost": "200.50",
            "technician": "Jane Smith",
            "description": "Preventive maintenance",
            "notes": "Checked all components"
        }

        response = client.post(
            "/api/v1/assets/maintenance/",
            json=maintenance_data,
            headers=auth_headers
        )

        assert response.status_code == 201
        data = response.json()
        assert data["asset_id"] == sample_asset.id
        assert data["maintenance_type"] == "preventive"
        assert data["status"] == "pending"
        assert "id" in data
        assert "asset_code" in data

    def test_create_maintenance_invalid_asset(self, client, auth_headers):
        """Test creating maintenance for non-existent asset"""
        maintenance_data = {
            "asset_id": 99999,  # Non-existent
            "maintenance_type": "routine",
            "maintenance_date": str(date.today()),
            "cost": "100.00"
        }

        response = client.post(
            "/api/v1/assets/maintenance/",
            json=maintenance_data,
            headers=auth_headers
        )

        assert response.status_code == 404

    def test_list_maintenance_empty(self, client, auth_headers):
        """Test listing maintenance when none exist"""
        response = client.get(
            "/api/v1/assets/maintenance/",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_list_maintenance(self, client, sample_maintenance, auth_headers):
        """Test listing all maintenance records"""
        response = client.get(
            "/api/v1/assets/maintenance/",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1
        assert data[0]["id"] == sample_maintenance.id
        assert "asset_code" in data[0]
        assert "asset_name" in data[0]

    def test_list_maintenance_filter_by_status(self, client, db_session, sample_asset, auth_headers):
        """Test listing maintenance with status filter"""
        from app.models.maintenance import MaintenanceRecord

        # Create maintenance records with different statuses
        statuses = ["pending", "in_progress", "completed"]
        for status in statuses:
            maintenance = MaintenanceRecord(
                asset_id=sample_asset.id,
                maintenance_type="routine",
                maintenance_date=date.today(),
                cost=Decimal("100.00"),
                status=status
            )
            db_session.add(maintenance)
        db_session.commit()

        # Test filtering
        response = client.get(
            "/api/v1/assets/maintenance/?status=completed",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert all(m["status"] == "completed" for m in data)

    def test_list_maintenance_filter_by_asset(self, client, sample_maintenance, auth_headers):
        """Test listing maintenance for specific asset"""
        response = client.get(
            f"/api/v1/assets/maintenance/?asset_id={sample_maintenance.asset_id}",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert all(m["asset_id"] == sample_maintenance.asset_id for m in data)

    def test_get_maintenance(self, client, sample_maintenance, auth_headers):
        """Test getting a single maintenance record"""
        response = client.get(
            f"/api/v1/assets/maintenance/{sample_maintenance.id}",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == sample_maintenance.id
        assert data["asset_id"] == sample_maintenance.asset_id
        assert data["maintenance_type"] == sample_maintenance.maintenance_type
        assert "asset_code" in data

    def test_get_maintenance_not_found(self, client, auth_headers):
        """Test getting non-existent maintenance record"""
        response = client.get(
            "/api/v1/assets/maintenance/99999",
            headers=auth_headers
        )

        assert response.status_code == 404

    def test_update_maintenance(self, client, sample_maintenance, auth_headers):
        """Test updating a maintenance record"""
        update_data = {
            "status": "completed",
            "completed_date": str(date.today()),
            "cost": "175.00",
            "notes": "Completed successfully"
        }

        response = client.put(
            f"/api/v1/assets/maintenance/{sample_maintenance.id}",
            json=update_data,
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "completed"
        assert data["completed_date"] is not None
        assert Decimal(str(data["cost"])) == Decimal("175.00")

    def test_update_maintenance_partial(self, client, sample_maintenance, auth_headers):
        """Test partial update of maintenance record"""
        update_data = {
            "technician": "Updated Technician"
        }

        response = client.put(
            f"/api/v1/assets/maintenance/{sample_maintenance.id}",
            json=update_data,
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["technician"] == "Updated Technician"
        assert data["maintenance_type"] == sample_maintenance.maintenance_type  # Unchanged

    def test_delete_maintenance(self, client, sample_maintenance, auth_headers):
        """Test deleting a maintenance record"""
        response = client.delete(
            f"/api/v1/assets/maintenance/{sample_maintenance.id}",
            headers=auth_headers
        )

        assert response.status_code == 204

        # Verify deletion
        get_response = client.get(
            f"/api/v1/assets/maintenance/{sample_maintenance.id}",
            headers=auth_headers
        )
        assert get_response.status_code == 404

    def test_delete_maintenance_not_found(self, client, auth_headers):
        """Test deleting non-existent maintenance record"""
        response = client.delete(
            "/api/v1/assets/maintenance/99999",
            headers=auth_headers
        )

        assert response.status_code == 404


class TestMaintenanceValidation:
    """Test maintenance data validation"""

    def test_create_maintenance_missing_required_fields(self, client, auth_headers):
        """Test creating maintenance without required fields"""
        maintenance_data = {
            "maintenance_type": "routine"
            # Missing asset_id, maintenance_date
        }

        response = client.post(
            "/api/v1/assets/maintenance/",
            json=maintenance_data,
            headers=auth_headers
        )

        assert response.status_code == 422

    def test_create_maintenance_invalid_date(self, client, sample_asset, auth_headers):
        """Test creating maintenance with invalid date"""
        maintenance_data = {
            "asset_id": sample_asset.id,
            "maintenance_type": "routine",
            "maintenance_date": "invalid-date"
        }

        response = client.post(
            "/api/v1/assets/maintenance/",
            json=maintenance_data,
            headers=auth_headers
        )

        assert response.status_code == 422

    def test_create_maintenance_negative_cost(self, client, sample_asset, auth_headers):
        """Test creating maintenance with negative cost"""
        maintenance_data = {
            "asset_id": sample_asset.id,
            "maintenance_type": "routine",
            "maintenance_date": str(date.today()),
            "cost": "-100.00"
        }

        response = client.post(
            "/api/v1/assets/maintenance/",
            json=maintenance_data,
            headers=auth_headers
        )

        # Should either reject or handle gracefully
        assert response.status_code in [201, 400, 422]


class TestMaintenanceTypes:
    """Test different maintenance types"""

    def test_create_preventive_maintenance(self, client, sample_asset, auth_headers):
        """Test creating preventive maintenance"""
        maintenance_data = {
            "asset_id": sample_asset.id,
            "maintenance_type": "preventive",
            "maintenance_date": str(date.today()),
            "description": "Scheduled preventive check"
        }

        response = client.post(
            "/api/v1/assets/maintenance/",
            json=maintenance_data,
            headers=auth_headers
        )

        assert response.status_code == 201
        assert response.json()["maintenance_type"] == "preventive"

    def test_create_emergency_maintenance(self, client, sample_asset, auth_headers):
        """Test creating emergency maintenance"""
        maintenance_data = {
            "asset_id": sample_asset.id,
            "maintenance_type": "emergency",
            "maintenance_date": str(date.today()),
            "cost": "500.00",
            "description": "Emergency repair"
        }

        response = client.post(
            "/api/v1/assets/maintenance/",
            json=maintenance_data,
            headers=auth_headers
        )

        assert response.status_code == 201
        assert response.json()["maintenance_type"] == "emergency"

    def test_create_corrective_maintenance(self, client, sample_asset, auth_headers):
        """Test creating corrective maintenance"""
        maintenance_data = {
            "asset_id": sample_asset.id,
            "maintenance_type": "corrective",
            "maintenance_date": str(date.today()),
            "description": "Fix identified issue"
        }

        response = client.post(
            "/api/v1/assets/maintenance/",
            json=maintenance_data,
            headers=auth_headers
        )

        assert response.status_code == 201
        assert response.json()["maintenance_type"] == "corrective"


class TestMaintenanceStatusWorkflow:
    """Test maintenance status workflow"""

    def test_maintenance_status_progression(self, client, sample_maintenance, auth_headers):
        """Test progressing through maintenance statuses"""
        # Start: pending
        assert sample_maintenance.status == "pending"

        # Update to in_progress
        response = client.put(
            f"/api/v1/assets/maintenance/{sample_maintenance.id}",
            json={"status": "in_progress"},
            headers=auth_headers
        )
        assert response.status_code == 200
        assert response.json()["status"] == "in_progress"

        # Update to completed
        response = client.put(
            f"/api/v1/assets/maintenance/{sample_maintenance.id}",
            json={
                "status": "completed",
                "completed_date": str(date.today())
            },
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "completed"
        assert data["completed_date"] is not None

    def test_cancel_maintenance(self, client, sample_maintenance, auth_headers):
        """Test cancelling maintenance"""
        response = client.put(
            f"/api/v1/assets/maintenance/{sample_maintenance.id}",
            json={"status": "cancelled"},
            headers=auth_headers
        )

        assert response.status_code == 200
        assert response.json()["status"] == "cancelled"
