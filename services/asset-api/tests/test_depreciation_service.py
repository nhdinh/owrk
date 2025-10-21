"""
Unit tests for Depreciation Service
"""

import pytest
from decimal import Decimal
from datetime import date
from unittest.mock import Mock, patch, MagicMock

from app.models.asset import Asset, AssetType, DepreciationMethod
from app.models.depreciation import AssetDepreciationRecord
from app.services.depreciation_service import DepreciationService


class TestDepreciationService:
    """Test cases for DepreciationService"""

    @pytest.fixture
    def sample_straight_line_asset(self):
        """Sample asset with straight-line depreciation"""
        asset = Asset(
            id=1,
            asset_code="ASSET-001",
            name="Test Equipment",
            asset_type=AssetType.FIXED_ASSET,
            purchase_price=Decimal("12000000"),  # 12M VND
            purchase_date=date(2024, 1, 1),
            depreciation_method=DepreciationMethod.STRAIGHT_LINE,
            useful_life_months=60,  # 5 years
            residual_value=Decimal("2000000"),  # 2M VND
            depreciation_rate=None,
        )
        return asset

    @pytest.fixture
    def sample_declining_balance_asset(self):
        """Sample asset with declining balance depreciation"""
        asset = Asset(
            id=2,
            asset_code="ASSET-002",
            name="Test Vehicle",
            asset_type=AssetType.FIXED_ASSET,
            purchase_price=Decimal("500000000"),  # 500M VND
            purchase_date=date(2024, 1, 1),
            depreciation_method=DepreciationMethod.DECLINING_BALANCE,
            useful_life_months=60,
            residual_value=Decimal("50000000"),
            depreciation_rate=Decimal("20.00"),  # 20% per year
        )
        return asset

    def test_straight_line_depreciation_calculation(self, sample_straight_line_asset):
        """Test straight-line depreciation calculation"""
        # Expected calculation:
        # Depreciable amount = 12M - 2M = 10M
        # Monthly depreciation = 10M / 60 = 166,666.67

        with patch('app.services.depreciation_service.UnitOfWork') as mock_uow:
            mock_uow_instance = MagicMock()
            mock_uow.return_value.__enter__.return_value = mock_uow_instance
            mock_uow_instance.depreciations.get_latest_record.return_value = None

            record = DepreciationService.calculate_monthly_depreciation(
                sample_straight_line_asset,
                202401
            )

            # Verify calculations
            assert record.opening_value == Decimal("12000000")
            assert record.depreciation_amount == Decimal("166666.67")
            assert record.closing_value == Decimal("11833333.33")
            assert record.accumulated_depreciation == Decimal("166666.67")

    def test_declining_balance_depreciation_calculation(self, sample_declining_balance_asset):
        """Test declining balance depreciation calculation"""
        # Expected calculation:
        # Annual rate = 20%
        # Monthly depreciation = 500M * 0.20 / 12 = 8,333,333.33

        with patch('app.services.depreciation_service.UnitOfWork') as mock_uow:
            mock_uow_instance = MagicMock()
            mock_uow.return_value.__enter__.return_value = mock_uow_instance
            mock_uow_instance.depreciations.get_latest_record.return_value = None

            record = DepreciationService.calculate_monthly_depreciation(
                sample_declining_balance_asset,
                202401
            )

            # Verify calculations
            assert record.opening_value == Decimal("500000000")
            assert record.depreciation_amount == Decimal("8333333.33")
            assert record.closing_value == Decimal("491666666.67")
            assert record.accumulated_depreciation == Decimal("8333333.33")

    def test_depreciation_with_previous_record(self, sample_straight_line_asset):
        """Test depreciation calculation with previous record"""
        previous_record = AssetDepreciationRecord(
            asset_id=1,
            period_month=202312,
            opening_value=Decimal("12000000"),
            depreciation_amount=Decimal("166666.67"),
            closing_value=Decimal("11833333.33"),
            accumulated_depreciation=Decimal("166666.67")
        )

        with patch('app.services.depreciation_service.UnitOfWork') as mock_uow:
            mock_uow_instance = MagicMock()
            mock_uow.return_value.__enter__.return_value = mock_uow_instance
            mock_uow_instance.depreciations.get_latest_record.return_value = previous_record

            record = DepreciationService.calculate_monthly_depreciation(
                sample_straight_line_asset,
                202401
            )

            # Opening value should be previous closing value
            assert record.opening_value == Decimal("11833333.33")
            assert record.accumulated_depreciation == Decimal("333333.34")

    def test_depreciation_stops_at_residual_value(self, sample_straight_line_asset):
        """Test that depreciation doesn't go below residual value"""
        # Set previous record very close to residual value
        previous_record = AssetDepreciationRecord(
            asset_id=1,
            period_month=202312,
            opening_value=Decimal("2100000"),  # Close to residual
            depreciation_amount=Decimal("166666.67"),
            closing_value=Decimal("1933333.33"),
            accumulated_depreciation=Decimal("9900000")
        )

        with patch('app.services.depreciation_service.UnitOfWork') as mock_uow:
            mock_uow_instance = MagicMock()
            mock_uow.return_value.__enter__.return_value = mock_uow_instance
            mock_uow_instance.depreciations.get_latest_record.return_value = previous_record

            record = DepreciationService.calculate_monthly_depreciation(
                sample_straight_line_asset,
                202401
            )

            # Should not depreciate below residual value
            assert record.closing_value >= sample_straight_line_asset.residual_value

    def test_depreciation_no_method_configured(self):
        """Test error when no depreciation method is configured"""
        asset = Asset(
            id=1,
            asset_code="ASSET-001",
            purchase_price=Decimal("10000000"),
            depreciation_method=None,
            useful_life_months=60
        )

        with pytest.raises(ValueError, match="no depreciation method"):
            DepreciationService.calculate_monthly_depreciation(asset, 202401)

    def test_depreciation_no_useful_life(self, sample_straight_line_asset):
        """Test error when no useful life is configured"""
        sample_straight_line_asset.useful_life_months = None

        with pytest.raises(ValueError, match="no useful life"):
            DepreciationService.calculate_monthly_depreciation(sample_straight_line_asset, 202401)

    def test_declining_balance_no_rate(self, sample_declining_balance_asset):
        """Test error when declining balance has no rate"""
        sample_declining_balance_asset.depreciation_rate = None

        with patch('app.services.depreciation_service.UnitOfWork') as mock_uow:
            mock_uow_instance = MagicMock()
            mock_uow.return_value.__enter__.return_value = mock_uow_instance
            mock_uow_instance.depreciations.get_latest_record.return_value = None

            with pytest.raises(ValueError, match="no depreciation rate"):
                DepreciationService.calculate_monthly_depreciation(
                    sample_declining_balance_asset,
                    202401
                )

    @patch('app.services.depreciation_service.UnitOfWork')
    def test_calculate_all_depreciation(self, mock_uow, sample_straight_line_asset):
        """Test batch depreciation calculation for all assets"""
        mock_uow_instance = MagicMock()
        mock_uow.return_value.__enter__.return_value = mock_uow_instance

        # Setup mock data
        assets = [sample_straight_line_asset]
        mock_uow_instance.assets.get_fixed_assets_for_depreciation.return_value = assets
        mock_uow_instance.depreciations.record_exists.return_value = False
        mock_uow_instance.depreciations.get_latest_record.return_value = None

        # Execute
        count = DepreciationService.calculate_all_depreciation(202401)

        # Verify
        assert count == 1
        mock_uow_instance.depreciations.create.assert_called_once()
        mock_uow_instance.commit.assert_called_once()

    @patch('app.services.depreciation_service.UnitOfWork')
    def test_calculate_all_depreciation_skip_existing(self, mock_uow, sample_straight_line_asset):
        """Test that existing depreciation records are skipped"""
        mock_uow_instance = MagicMock()
        mock_uow.return_value.__enter__.return_value = mock_uow_instance

        assets = [sample_straight_line_asset]
        mock_uow_instance.assets.get_fixed_assets_for_depreciation.return_value = assets
        mock_uow_instance.depreciations.record_exists.return_value = True  # Already exists

        # Execute
        count = DepreciationService.calculate_all_depreciation(202401)

        # Verify - should not create any records
        assert count == 0
        mock_uow_instance.depreciations.create.assert_not_called()

    def test_get_current_period(self):
        """Test getting current period in YYYYMM format"""
        period = DepreciationService.get_current_period()

        # Verify format
        assert isinstance(period, int)
        assert period >= 202401  # Should be >= January 2024
        assert period <= 999912  # Valid YYYYMM format

        # Verify calculation
        today = date.today()
        expected = today.year * 100 + today.month
        assert period == expected

    @patch('app.services.depreciation_service.UnitOfWork')
    def test_get_asset_depreciation_history(self, mock_uow):
        """Test retrieving depreciation history for an asset"""
        mock_uow_instance = MagicMock()
        mock_uow.return_value.__enter__.return_value = mock_uow_instance

        # Setup mock records
        records = [
            AssetDepreciationRecord(
                id=1,
                asset_id=1,
                period_month=202401,
                opening_value=Decimal("12000000"),
                depreciation_amount=Decimal("166666.67"),
                closing_value=Decimal("11833333.33"),
                accumulated_depreciation=Decimal("166666.67")
            ),
            AssetDepreciationRecord(
                id=2,
                asset_id=1,
                period_month=202402,
                opening_value=Decimal("11833333.33"),
                depreciation_amount=Decimal("166666.67"),
                closing_value=Decimal("11666666.66"),
                accumulated_depreciation=Decimal("333333.34")
            )
        ]
        mock_uow_instance.depreciations.get_asset_records.return_value = records

        # Execute
        import asyncio
        result = asyncio.run(DepreciationService.get_asset_depreciation_history(1))

        # Verify
        assert len(result) == 2
        assert result[0].period_month == 202401
        assert result[1].period_month == 202402


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
