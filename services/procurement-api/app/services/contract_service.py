"""
Framework Contract Service
Business logic for framework contract management
"""

from typing import Optional, Tuple
from datetime import date
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.framework_contract import FrameworkContract, ContractStatus
from app.repositories.contract_repository import ContractRepository
from app.repositories.vendor_repository import VendorRepository
from app.schemas.contract_schema import ContractCreate, ContractUpdate
from app.utils.code_generator import generate_contract_code


class ContractService:
    """Service for framework contract business logic"""

    def __init__(
        self,
        db: Session,
        contract_repo: ContractRepository,
        vendor_repo: VendorRepository
    ):
        self.db = db
        self.contract_repo = contract_repo
        self.vendor_repo = vendor_repo

    def create_contract(
        self,
        contract_data: ContractCreate,
        user_id: int
    ) -> FrameworkContract:
        """Create a new framework contract"""

        # Validate vendor exists
        vendor = self.vendor_repo.get_by_id(contract_data.vendor_id)
        if not vendor:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Vendor not found"
            )

        # Validate dates
        if contract_data.end_date <= contract_data.start_date:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="End date must be after start date"
            )

        # Generate contract code
        contract_code = generate_contract_code(self.db, vendor.vendor_code)

        # Create contract
        contract = FrameworkContract(
            contract_code=contract_code,
            contract_name=contract_data.contract_name,
            vendor_id=contract_data.vendor_id,
            contract_value=contract_data.contract_value,
            start_date=contract_data.start_date,
            end_date=contract_data.end_date,
            terms_and_conditions=contract_data.terms_and_conditions,
            payment_terms=contract_data.payment_terms,
            delivery_terms=contract_data.delivery_terms,
            contract_file_url=contract_data.contract_file_url,
            status=ContractStatus.ACTIVE,
            created_by=user_id
        )

        return self.contract_repo.create(contract)

    def get_contract(self, contract_id: int) -> FrameworkContract:
        """Get contract by ID"""
        contract = self.contract_repo.get_by_id(contract_id)
        if not contract:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Contract not found"
            )
        return contract

    def get_contracts(
        self,
        skip: int = 0,
        limit: int = 100,
        status: Optional[str] = None,
        vendor_id: Optional[int] = None,
        from_date: Optional[date] = None,
        to_date: Optional[date] = None
    ) -> Tuple[list[FrameworkContract], int]:
        """Get contracts with filters"""
        return self.contract_repo.get_all(
            skip=skip,
            limit=limit,
            status=status,
            vendor_id=vendor_id,
            from_date=from_date,
            to_date=to_date
        )

    def get_active_contracts_by_vendor(self, vendor_id: int) -> list[FrameworkContract]:
        """Get all active contracts for a vendor"""
        vendor = self.vendor_repo.get_by_id(vendor_id)
        if not vendor:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Vendor not found"
            )
        return self.contract_repo.get_active_by_vendor(vendor_id)

    def get_expiring_contracts(self, days: int) -> list[FrameworkContract]:
        """Get contracts expiring within specified days"""
        if days < 1 or days > 365:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Days must be between 1 and 365"
            )
        return self.contract_repo.get_expiring_contracts(days)

    def update_contract(
        self,
        contract_id: int,
        contract_data: ContractUpdate,
        user_id: int
    ) -> FrameworkContract:
        """Update framework contract"""
        contract = self.get_contract(contract_id)

        # Only active contracts can be updated
        if contract.status != ContractStatus.ACTIVE:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only active contracts can be updated"
            )

        # Update fields
        if contract_data.contract_name is not None:
            contract.contract_name = contract_data.contract_name
        if contract_data.contract_value is not None:
            contract.contract_value = contract_data.contract_value
        if contract_data.end_date is not None:
            if contract_data.end_date <= contract.start_date:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="End date must be after start date"
                )
            contract.end_date = contract_data.end_date
        if contract_data.terms_and_conditions is not None:
            contract.terms_and_conditions = contract_data.terms_and_conditions
        if contract_data.payment_terms is not None:
            contract.payment_terms = contract_data.payment_terms
        if contract_data.delivery_terms is not None:
            contract.delivery_terms = contract_data.delivery_terms
        if contract_data.contract_file_url is not None:
            contract.contract_file_url = contract_data.contract_file_url

        return self.contract_repo.update(contract)

    def delete_contract(self, contract_id: int, user_id: int) -> None:
        """Delete contract (soft delete)"""
        contract = self.get_contract(contract_id)
        self.contract_repo.delete(contract)

    def activate_contract(self, contract_id: int, user_id: int) -> FrameworkContract:
        """Activate a contract"""
        contract = self.get_contract(contract_id)

        if contract.status == ContractStatus.ACTIVE:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Contract is already active"
            )

        contract.status = ContractStatus.ACTIVE
        return self.contract_repo.update(contract)

    def suspend_contract(self, contract_id: int, user_id: int) -> FrameworkContract:
        """Suspend a contract temporarily"""
        contract = self.get_contract(contract_id)

        if contract.status != ContractStatus.ACTIVE:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only active contracts can be suspended"
            )

        contract.status = ContractStatus.EXPIRED
        return self.contract_repo.update(contract)

    def terminate_contract(
        self,
        contract_id: int,
        reason: str,
        user_id: int
    ) -> FrameworkContract:
        """Terminate a contract permanently"""
        contract = self.get_contract(contract_id)

        if contract.status == ContractStatus.TERMINATED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Contract is already terminated"
            )

        contract.status = ContractStatus.TERMINATED
        # Store termination reason in terms_and_conditions
        termination_note = f"\n\nTERMINATED: {reason}"
        contract.terms_and_conditions = (contract.terms_and_conditions or "") + termination_note

        return self.contract_repo.update(contract)
