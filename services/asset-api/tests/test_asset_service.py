"""
Unit tests for Asset Service
"""

import pytest
from decimal import Decimal
from datetime import date, datetime
from unittest.mock import Mock, patch, MagicMock

from app.models.asset import Asset, AssetType, AssetStatus, DepreciationMethod
from app.models.category import AssetCategory
from app.models.assignment import AssetAssignment, AssignmentStatus
from app.services.asset_service import AssetService
from app.schemas.asset_schema import (
    AssetCreate,
    AssetUpdate,
    AssignmentCreate,
    AssignmentReturn,
)


class TestAssetService:
    """Test cases for AssetService"""

    @pytest.fixture
    def sample_asset_data(self):
        """Sample asset creation data"""
        return AssetCreate(
            asset_code="ASSET-001",
            name="Test Laptop",
            category_id=1,
            asset_type=AssetType.FIXED_ASSET,
            description="Test laptop for development",
            manufacturer="Dell",
            model="XPS 15",
            serial_number="SN123456",
            purchase_price=Decimal("25000000"),
            purchase_date=date(2024, 1, 15),
            depreciation_rate=Decimal("20.00"),
            depreciation_method=DepreciationMethod.STRAIGHT_LINE,
            useful_life_months=60,
            residual_value=Decimal("5000000"),
            warranty_months=24,
            warranty_start_date=date(2024, 1, 15),
            created_by=1,
        )

    @pytest.fixture
    def sample_asset(self, sample_asset_data):
        """Sample asset object"""
        asset = Asset(**sample_asset_data.model_dump())
        asset.id = 1
        asset.qr_code = "data:image/png;base64,test"
        asset.warranty_end_date = date(2026, 1, 15)
        return asset

    @pytest.fixture
    def sample_category(self):
        """Sample category object"""
        category = AssetCategory(
            id=1,
            name="IT Equipment",
            code="IT",
            description="Information Technology Equipment",
        )
        return category

    @patch("app.services.asset_service.UnitOfWork")
    @patch("app.services.asset_service.generate_qr_code")
    def test_create_asset_success(
        self, mock_qr_code, mock_uow, sample_asset_data, sample_category, sample_asset
    ):
        """Test successful asset creation"""
        # Setup mocks
        mock_qr_code.return_value = "data:image/png;base64,test"
        mock_uow_instance = MagicMock()
        mock_uow.return_value.__enter__.return_value = mock_uow_instance

        mock_uow_instance.assets.get_by_code.return_value = None
        mock_uow_instance.categories.get_by_id.return_value = sample_category
        mock_uow_instance.assets.create.return_value = sample_asset

        # Execute
        import asyncio

        result = asyncio.run(AssetService.create_asset(sample_asset_data))

        # Verify
        assert result.asset_code == "ASSET-001"
        assert result.name == "Test Laptop"
        assert result.qr_code == "data:image/png;base64,test"
        mock_uow_instance.assets.create.assert_called_once()
        mock_uow_instance.commit.assert_called_once()

    @patch("app.services.asset_service.UnitOfWork")
    def test_create_asset_duplicate_code(
        self, mock_uow, sample_asset_data, sample_asset
    ):
        """Test asset creation with duplicate code"""
        # Setup mocks
        mock_uow_instance = MagicMock()
        mock_uow.return_value.__enter__.return_value = mock_uow_instance
        mock_uow_instance.assets.get_by_code.return_value = sample_asset

        # Execute & Verify
        import asyncio

        with pytest.raises(ValueError, match="already exists"):
            asyncio.run(AssetService.create_asset(sample_asset_data))

    @patch("app.services.asset_service.UnitOfWork")
    def test_create_asset_invalid_category(self, mock_uow, sample_asset_data):
        """Test asset creation with invalid category"""
        # Setup mocks
        mock_uow_instance = MagicMock()
        mock_uow.return_value.__enter__.return_value = mock_uow_instance
        mock_uow_instance.assets.get_by_code.return_value = None
        mock_uow_instance.categories.get_by_id.return_value = None

        # Execute & Verify
        import asyncio

        with pytest.raises(ValueError, match="not found"):
            asyncio.run(AssetService.create_asset(sample_asset_data))

    @patch("app.services.asset_service.UnitOfWork")
    def test_update_asset_success(self, mock_uow, sample_asset):
        """Test successful asset update"""
        # Setup mocks
        mock_uow_instance = MagicMock()
        mock_uow.return_value.__enter__.return_value = mock_uow_instance
        mock_uow_instance.assets.get_by_id.return_value = sample_asset

        updated_asset = sample_asset
        updated_asset.name = "Updated Laptop"
        mock_uow_instance.assets.update.return_value = updated_asset

        # Execute
        update_data = AssetUpdate(name="Updated Laptop")
        import asyncio

        result = asyncio.run(AssetService.update_asset(1, update_data))

        # Verify
        assert result.name == "Updated Laptop"
        mock_uow_instance.assets.update.assert_called_once()
        mock_uow_instance.commit.assert_called_once()

    @patch("app.services.asset_service.UnitOfWork")
    def test_update_asset_not_found(self, mock_uow):
        """Test update of non-existent asset"""
        # Setup mocks
        mock_uow_instance = MagicMock()
        mock_uow.return_value.__enter__.return_value = mock_uow_instance
        mock_uow_instance.assets.get_by_id.return_value = None

        # Execute & Verify
        update_data = AssetUpdate(name="Updated Laptop")
        import asyncio

        with pytest.raises(ValueError, match="not found"):
            asyncio.run(AssetService.update_asset(999, update_data))

    @patch("app.services.asset_service.UnitOfWork")
    def test_delete_asset_success(self, mock_uow, sample_asset):
        """Test successful asset deletion (soft delete)"""
        # Setup mocks
        mock_uow_instance = MagicMock()
        mock_uow.return_value.__enter__.return_value = mock_uow_instance
        mock_uow_instance.assets.get_by_id.return_value = sample_asset

        # Execute
        import asyncio

        asyncio.run(AssetService.delete_asset(1))

        # Verify
        mock_uow_instance.assets.update.assert_called_once()
        mock_uow_instance.commit.assert_called_once()

    @patch("app.services.asset_service.UnitOfWork")
    def test_assign_asset_success(self, mock_uow, sample_asset):
        """Test successful asset assignment"""
        # Setup mocks
        sample_asset.status = AssetStatus.AVAILABLE
        sample_asset.current_user_id = None

        mock_uow_instance = MagicMock()
        mock_uow.return_value.__enter__.return_value = mock_uow_instance
        mock_uow_instance.assets.get_by_id.return_value = sample_asset

        assignment = AssetAssignment(
            id=1,
            asset_id=1,
            user_id=2,
            assigned_by=1,
            assigned_at=datetime.now(),
            status=AssignmentStatus.ACTIVE,
        )
        mock_uow_instance.assignments.create.return_value = assignment

        # Execute
        assignment_data = AssignmentCreate(
            asset_id=1, user_id=2, assigned_by=1, notes="Assignment for testing"
        )
        import asyncio

        result = asyncio.run(AssetService.assign_asset(assignment_data))

        # Verify
        assert result.status == AssignmentStatus.ACTIVE
        assert sample_asset.status == AssetStatus.IN_USE
        assert sample_asset.current_user_id == 2
        mock_uow_instance.assignments.create.assert_called_once()
        mock_uow_instance.commit.assert_called_once()

    @patch("app.services.asset_service.UnitOfWork")
    def test_assign_asset_already_assigned(self, mock_uow, sample_asset):
        """Test assigning already assigned asset"""
        # Setup mocks
        sample_asset.status = AssetStatus.IN_USE
        sample_asset.current_user_id = 3

        mock_uow_instance = MagicMock()
        mock_uow.return_value.__enter__.return_value = mock_uow_instance
        mock_uow_instance.assets.get_by_id.return_value = sample_asset

        # Execute & Verify
        assignment_data = AssignmentCreate(
            asset_id=1, user_id=2, assigned_by=1, notes="Assignment for testing"
        )
        import asyncio

        with pytest.raises(ValueError, match="already assigned"):
            asyncio.run(AssetService.assign_asset(assignment_data))

    @patch("app.services.asset_service.UnitOfWork")
    def test_return_asset_success(self, mock_uow, sample_asset):
        """Test successful asset return"""
        # Setup mocks
        sample_asset.status = AssetStatus.IN_USE
        sample_asset.current_user_id = 2

        active_assignment = AssetAssignment(
            id=1,
            asset_id=1,
            user_id=2,
            assigned_by=1,
            assigned_at=datetime.now(),
            status=AssignmentStatus.ACTIVE,
        )

        mock_uow_instance = MagicMock()
        mock_uow.return_value.__enter__.return_value = mock_uow_instance
        mock_uow_instance.assets.get_by_id.return_value = sample_asset
        mock_uow_instance.assignments.get_active_assignment.return_value = (
            active_assignment
        )

        # Execute
        return_data = AssignmentReturn(
            returned_by=1, return_notes="Asset returned in good condition"
        )
        import asyncio

        result = asyncio.run(AssetService.return_asset(1, return_data))

        # Verify
        assert result.status == AssignmentStatus.RETURNED
        assert sample_asset.status == AssetStatus.AVAILABLE
        assert sample_asset.current_user_id is None
        mock_uow_instance.commit.assert_called_once()

    @patch("app.services.asset_service.UnitOfWork")
    def test_search_assets_with_filters(self, mock_uow, sample_asset):
        """Test asset search with filters"""
        # Setup mocks
        mock_uow_instance = MagicMock()
        mock_uow.return_value.__enter__.return_value = mock_uow_instance
        mock_uow_instance.assets.search.return_value = ([sample_asset], 1)

        # Execute
        import asyncio

        assets, total = asyncio.run(
            AssetService.search_assets(
                search="laptop",
                category_id=1,
                status=AssetStatus.AVAILABLE,
                page=1,
                page_size=20,
            )
        )

        # Verify
        assert len(assets) == 1
        assert total == 1
        assert assets[0].asset_code == "ASSET-001"

    @patch("app.services.asset_service.UnitOfWork")
    def test_get_statistics(self, mock_uow):
        """Test getting asset statistics"""
        # Setup mocks
        mock_uow_instance = MagicMock()
        mock_uow.return_value.__enter__.return_value = mock_uow_instance

        stats_data = {
            "total_assets": 100,
            "available_assets": 60,
            "in_use_assets": 30,
            "maintenance_assets": 5,
            "broken_assets": 3,
            "disposed_assets": 2,
            "total_value": Decimal("5000000000"),
        }
        mock_uow_instance.assets.get_statistics.return_value = stats_data

        # Execute
        import asyncio

        stats = asyncio.run(AssetService.get_statistics())

        # Verify
        assert stats["total_assets"] == 100
        assert stats["available_assets"] == 60
        assert stats["total_value"] == Decimal("5000000000")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
