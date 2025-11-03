"""
Purchase Request Repository
Data access layer for purchase request operations
"""

from typing import List, Optional
from decimal import Decimal
from datetime import date
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_, desc

from app.models.purchase_request import PurchaseRequest, PurchaseRequestItem, ApprovalStatus, Priority
from app.utils.code_generator import generate_request_code


class PurchaseRequestRepository:
    """Repository for purchase request CRUD operations"""

    def __init__(self, db: Session):
        self.db = db

    def create(self, request_data: dict, items_data: List[dict]) -> PurchaseRequest:
        """
        Create a new purchase request with items

        Args:
            request_data: Dictionary with purchase request information
            items_data: List of dictionaries with item information

        Returns:
            PurchaseRequest: Created purchase request object with items
        """
        # Generate request code
        department_id = request_data.get('department_id')
        request_code = generate_request_code(self.db, department_id)

        # Create purchase request object
        purchase_request = PurchaseRequest(
            request_code=request_code,
            **request_data
        )

        self.db.add(purchase_request)
        self.db.flush()

        # Create items
        for item_data in items_data:
            item = PurchaseRequestItem(
                purchase_request_id=purchase_request.id,
                **item_data
            )
            self.db.add(item)

        self.db.flush()
        self.db.refresh(purchase_request)

        return purchase_request

    def get_by_id(self, request_id: int) -> Optional[PurchaseRequest]:
        """Get purchase request by ID with items"""
        return self.db.query(PurchaseRequest).options(
            joinedload(PurchaseRequest.items)
        ).filter(
            PurchaseRequest.id == request_id
        ).first()

    def get_by_code(self, request_code: str) -> Optional[PurchaseRequest]:
        """Get purchase request by code with items"""
        return self.db.query(PurchaseRequest).options(
            joinedload(PurchaseRequest.items)
        ).filter(
            PurchaseRequest.request_code == request_code
        ).first()

    def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        status: Optional[ApprovalStatus] = None,
        priority: Optional[Priority] = None,
        requested_by: Optional[int] = None,
        department_id: Optional[int] = None,
        from_date: Optional[date] = None,
        to_date: Optional[date] = None
    ) -> List[PurchaseRequest]:
        """
        Get all purchase requests with optional filtering

        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            status: Filter by approval status
            priority: Filter by priority
            requested_by: Filter by requester user ID
            department_id: Filter by department ID
            from_date: Filter by request date (from)
            to_date: Filter by request date (to)

        Returns:
            List[PurchaseRequest]: List of purchase requests
        """
        query = self.db.query(PurchaseRequest).options(
            joinedload(PurchaseRequest.items)
        )

        # Apply filters
        if status:
            query = query.filter(PurchaseRequest.approval_status == status)

        if priority:
            query = query.filter(PurchaseRequest.priority == priority)

        if requested_by:
            query = query.filter(PurchaseRequest.requested_by == requested_by)

        if department_id:
            query = query.filter(PurchaseRequest.department_id == department_id)

        if from_date:
            query = query.filter(PurchaseRequest.request_date >= from_date)

        if to_date:
            query = query.filter(PurchaseRequest.request_date <= to_date)

        return query.order_by(desc(PurchaseRequest.created_at)).offset(skip).limit(limit).all()

    def count(
        self,
        status: Optional[ApprovalStatus] = None,
        priority: Optional[Priority] = None,
        requested_by: Optional[int] = None,
        department_id: Optional[int] = None,
        from_date: Optional[date] = None,
        to_date: Optional[date] = None
    ) -> int:
        """
        Count purchase requests with optional filtering

        Args:
            status: Filter by approval status
            priority: Filter by priority
            requested_by: Filter by requester user ID
            department_id: Filter by department ID
            from_date: Filter by request date (from)
            to_date: Filter by request date (to)

        Returns:
            int: Count of purchase requests
        """
        query = self.db.query(PurchaseRequest)

        if status:
            query = query.filter(PurchaseRequest.approval_status == status)

        if priority:
            query = query.filter(PurchaseRequest.priority == priority)

        if requested_by:
            query = query.filter(PurchaseRequest.requested_by == requested_by)

        if department_id:
            query = query.filter(PurchaseRequest.department_id == department_id)

        if from_date:
            query = query.filter(PurchaseRequest.request_date >= from_date)

        if to_date:
            query = query.filter(PurchaseRequest.request_date <= to_date)

        return query.count()

    def update(self, purchase_request: PurchaseRequest, update_data: dict) -> PurchaseRequest:
        """
        Update purchase request information

        Args:
            purchase_request: PurchaseRequest object to update
            update_data: Dictionary with fields to update

        Returns:
            PurchaseRequest: Updated purchase request object
        """
        for key, value in update_data.items():
            if hasattr(purchase_request, key) and value is not None:
                setattr(purchase_request, key, value)

        self.db.flush()
        self.db.refresh(purchase_request)

        return purchase_request

    def delete(self, purchase_request: PurchaseRequest) -> bool:
        """
        Delete a purchase request (soft delete)

        Args:
            purchase_request: PurchaseRequest object to delete

        Returns:
            bool: True if successful
        """
        purchase_request.approval_status = ApprovalStatus.CANCELLED
        self.db.flush()
        return True

    def exists(self, request_id: int) -> bool:
        """Check if purchase request exists"""
        return self.db.query(PurchaseRequest).filter(
            PurchaseRequest.id == request_id
        ).first() is not None

    def get_pending_approvals(self, approver_level: int = 1) -> List[PurchaseRequest]:
        """
        Get purchase requests pending approval at a specific level

        Args:
            approver_level: Approval level (1, 2, or 3)

        Returns:
            List[PurchaseRequest]: Purchase requests pending approval
        """
        if approver_level == 1:
            status = ApprovalStatus.PENDING
        elif approver_level == 2:
            status = ApprovalStatus.LEVEL1_APPROVED
        elif approver_level == 3:
            status = ApprovalStatus.LEVEL2_APPROVED
        else:
            return []

        return self.db.query(PurchaseRequest).options(
            joinedload(PurchaseRequest.items)
        ).filter(
            PurchaseRequest.approval_status == status
        ).order_by(desc(PurchaseRequest.created_at)).all()
