"""
Framework Contract Repository
Handles database operations for framework contracts
"""

from typing import Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from datetime import datetime, date, timedelta

from app.models.framework_contract import FrameworkContract, ContractStatus


class ContractRepository:
    """Repository for FrameworkContract database operations"""

    def __init__(self, db: Session):
        self.db = db

    def create(self, contract: FrameworkContract) -> FrameworkContract:
        """Create a new framework contract"""
        self.db.add(contract)
        self.db.commit()
        self.db.refresh(contract)
        return contract

    def get_by_id(self, contract_id: int) -> Optional[FrameworkContract]:
        """Get contract by ID"""
        return (
            self.db.query(FrameworkContract)
            .filter(FrameworkContract.id == contract_id)
            .first()
        )

    def get_by_code(self, contract_code: str) -> Optional[FrameworkContract]:
        """Get contract by code"""
        return (
            self.db.query(FrameworkContract)
            .filter(FrameworkContract.contract_code == contract_code)
            .first()
        )

    def get_by_vendor(
        self,
        vendor_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> list[FrameworkContract]:
        """Get contracts by vendor ID"""
        return (
            self.db.query(FrameworkContract)
            .filter(FrameworkContract.vendor_id == vendor_id)
            .order_by(FrameworkContract.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_active_by_vendor(self, vendor_id: int) -> list[FrameworkContract]:
        """Get active contracts for a vendor"""
        return (
            self.db.query(FrameworkContract)
            .filter(
                and_(
                    FrameworkContract.vendor_id == vendor_id,
                    FrameworkContract.status == ContractStatus.ACTIVE
                )
            )
            .order_by(FrameworkContract.end_date.asc())
            .all()
        )

    def get_expiring_contracts(self, days: int) -> list[FrameworkContract]:
        """Get contracts expiring within specified days"""
        expiry_date = date.today() + timedelta(days=days)
        return (
            self.db.query(FrameworkContract)
            .filter(
                and_(
                    FrameworkContract.status == ContractStatus.ACTIVE,
                    FrameworkContract.end_date <= expiry_date,
                    FrameworkContract.end_date >= date.today()
                )
            )
            .order_by(FrameworkContract.end_date.asc())
            .all()
        )

    def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        status: Optional[str] = None,
        vendor_id: Optional[int] = None,
        from_date: Optional[date] = None,
        to_date: Optional[date] = None
    ) -> Tuple[list[FrameworkContract], int]:
        """Get all contracts with filters"""
        query = self.db.query(FrameworkContract)

        # Apply filters
        if status:
            query = query.filter(FrameworkContract.status == status)

        if vendor_id:
            query = query.filter(FrameworkContract.vendor_id == vendor_id)

        if from_date:
            query = query.filter(FrameworkContract.start_date >= from_date)

        if to_date:
            query = query.filter(FrameworkContract.end_date <= to_date)

        # Get total count
        total = query.count()

        # Get paginated results
        contracts = (
            query
            .order_by(FrameworkContract.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

        return contracts, total

    def update(self, contract: FrameworkContract) -> FrameworkContract:
        """Update contract"""
        self.db.commit()
        self.db.refresh(contract)
        return contract

    def delete(self, contract: FrameworkContract) -> None:
        """Delete contract (soft delete by setting status)"""
        contract.status = ContractStatus.TERMINATED
        self.db.commit()
