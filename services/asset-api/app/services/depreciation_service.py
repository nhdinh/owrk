"""
Depreciation Service - Calculate asset depreciation
"""

import logging
from datetime import date
from decimal import Decimal
from dateutil.relativedelta import relativedelta

from app.core.unit_of_work import UnitOfWork
from app.models.asset import Asset, DepreciationMethod
from app.models.depreciation import AssetDepreciationRecord

logger = logging.getLogger(__name__)


class DepreciationService:
    """Service for depreciation calculation"""

    @staticmethod
    def calculate_monthly_depreciation(
        asset: Asset, period_month: int
    ) -> AssetDepreciationRecord:
        """
        Calculate depreciation for a specific period

        Args:
            asset: Asset to calculate depreciation for
            period_month: Period in YYYYMM format

        Returns:
            Depreciation record

        Raises:
            ValueError: If asset doesn't have depreciation configured
        """
        if not asset.depreciation_method:
            raise ValueError(
                f"Asset {asset.asset_code} has no depreciation method configured"
            )

        if not asset.useful_life_months:
            raise ValueError(f"Asset {asset.asset_code} has no useful life configured")

        # Get latest depreciation record or use purchase price as opening value
        latest_record = None
        with UnitOfWork() as uow:
            latest_record = uow.depreciations.get_latest_record(asset.id)

        if latest_record:
            opening_value = latest_record.closing_value
            accumulated_depreciation = latest_record.accumulated_depreciation
        else:
            opening_value = asset.purchase_price
            accumulated_depreciation = Decimal("0.00")

        # Calculate depreciation amount based on method
        if asset.depreciation_method == DepreciationMethod.STRAIGHT_LINE:
            # Straight-line: (Cost - Residual) / Useful Life
            depreciable_amount = asset.purchase_price - (
                asset.residual_value or Decimal("0.00")
            )
            monthly_depreciation = depreciable_amount / asset.useful_life_months
        else:
            # Declining balance: (Book Value * Rate) / 12
            if asset.depreciation_rate:
                annual_rate = asset.depreciation_rate / Decimal("100.00")
                monthly_depreciation = opening_value * annual_rate / Decimal("12.00")
            else:
                raise ValueError(
                    f"Asset {asset.asset_code} has no depreciation rate configured"
                )

        # Round to 2 decimal places
        depreciation_amount = round(monthly_depreciation, 2)

        # Ensure depreciation doesn't go below residual value
        residual = asset.residual_value or Decimal("0.00")
        if opening_value - depreciation_amount < residual:
            depreciation_amount = opening_value - residual

        # Ensure non-negative
        if depreciation_amount < 0:
            depreciation_amount = Decimal("0.00")

        closing_value = opening_value - depreciation_amount
        accumulated_depreciation += depreciation_amount

        record = AssetDepreciationRecord(
            asset_id=asset.id,
            period_month=period_month,
            opening_value=opening_value,
            depreciation_amount=depreciation_amount,
            closing_value=closing_value,
            accumulated_depreciation=accumulated_depreciation,
        )

        return record

    @staticmethod
    def calculate_all_depreciation(period_month: int) -> int:
        """
        Calculate depreciation for all applicable assets

        Args:
            period_month: Period in YYYYMM format (e.g., 202501)

        Returns:
            Number of assets processed
        """
        with UnitOfWork() as uow:
            # Get all fixed assets that need depreciation
            assets = uow.assets.get_fixed_assets_for_depreciation()
            count = 0

            for asset in assets:
                try:
                    # Check if already calculated for this period
                    if uow.depreciations.record_exists(asset.id, period_month):
                        logger.info(
                            f"Depreciation already calculated for asset {asset.asset_code} period {period_month}"
                        )
                        continue

                    # Calculate depreciation
                    record = DepreciationService.calculate_monthly_depreciation(
                        asset, period_month
                    )

                    # Save record
                    uow.depreciations.create(record)
                    count += 1

                    logger.info(
                        f"Calculated depreciation for {asset.asset_code}: "
                        f"Opening={record.opening_value}, "
                        f"Depreciation={record.depreciation_amount}, "
                        f"Closing={record.closing_value}"
                    )

                except Exception as e:
                    logger.error(
                        f"Error calculating depreciation for asset {asset.asset_code}: {str(e)}"
                    )
                    continue

            uow.commit()
            logger.info(
                f"Depreciation calculated for {count} assets in period {period_month}"
            )
            return count

    @staticmethod
    def get_current_period() -> int:
        """
        Get current period in YYYYMM format

        Returns:
            Current period
        """
        today = date.today()
        return today.year * 100 + today.month

    @staticmethod
    async def get_asset_depreciation_history(asset_id: int):
        """Get depreciation history for an asset"""
        with UnitOfWork() as uow:
            return uow.depreciations.get_asset_records(asset_id)
