"""
Purchase Request Service
Business logic layer for purchase request operations with multi-level approval workflow
"""

import logging
from typing import List, Optional
from decimal import Decimal
from datetime import date, datetime
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.purchase_request import PurchaseRequest, ApprovalStatus, Priority
from app.repositories.purchase_request_repository import PurchaseRequestRepository
from app.schemas.purchase_request_schema import (
    PurchaseRequestCreate,
    PurchaseRequestUpdate,
    PurchaseRequestResponse,
    PurchaseRequestListResponse,
    ApprovalRequest,
    RejectionRequest,
)
from app.core.events import publish_event, EventTypes

logger = logging.getLogger(__name__)


class PurchaseRequestService:
    """Service for purchase request business logic and approval workflow"""

    def __init__(self, db: Session):
        self.db = db
        self.repository = PurchaseRequestRepository(db)

    def create_purchase_request(
        self, request_data: PurchaseRequestCreate, requested_by: int
    ) -> PurchaseRequestResponse:
        """
        Create a new purchase request in DRAFT status

        Args:
            request_data: Purchase request creation data
            requested_by: User ID creating the request

        Returns:
            PurchaseRequestResponse: Created purchase request

        Raises:
            HTTPException: If validation fails
        """
        # Prepare request data
        request_dict = request_data.model_dump(exclude={"items"}, exclude_unset=True)
        request_dict["requested_by"] = requested_by
        request_dict["approval_status"] = ApprovalStatus.DRAFT

        # Prepare items data
        items_data = [
            item.model_dump(exclude_unset=True) for item in request_data.items
        ]

        try:
            purchase_request = self.repository.create(request_dict, items_data)
            self.db.commit()

            # Publish event
            publish_event(
                EventTypes.PURCHASE_REQUEST_CREATED,
                {
                    "id": purchase_request.id,
                    "request_code": purchase_request.request_code,
                    "title": purchase_request.title,
                    "requested_by": requested_by,
                    "approval_status": purchase_request.approval_status.value,
                    "created_at": str(purchase_request.created_at),
                },
            )

            logger.info(
                f"Purchase request created: {purchase_request.request_code} by user {requested_by}"
            )

            return PurchaseRequestResponse.model_validate(purchase_request)

        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating purchase request: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create purchase request",
            )

    def get_purchase_request(self, request_id: int) -> PurchaseRequestResponse:
        """
        Get purchase request by ID

        Args:
            request_id: Purchase request ID

        Returns:
            PurchaseRequestResponse: Purchase request details

        Raises:
            HTTPException: If purchase request not found
        """
        purchase_request = self.repository.get_by_id(request_id)

        if not purchase_request:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Purchase request with ID {request_id} not found",
            )

        return PurchaseRequestResponse.model_validate(purchase_request)

    def list_purchase_requests(
        self,
        skip: int = 0,
        limit: int = 100,
        status: Optional[ApprovalStatus] = None,
        priority: Optional[Priority] = None,
        requested_by: Optional[int] = None,
        department_id: Optional[int] = None,
        from_date: Optional[date] = None,
        to_date: Optional[date] = None,
    ) -> PurchaseRequestListResponse:
        """
        List purchase requests with pagination and filters

        Args:
            skip: Number of records to skip
            limit: Maximum number of records
            status: Filter by approval status
            priority: Filter by priority
            requested_by: Filter by requester user ID
            department_id: Filter by department ID
            from_date: Filter by request date (from)
            to_date: Filter by request date (to)

        Returns:
            PurchaseRequestListResponse: Paginated purchase request list
        """
        requests = self.repository.get_all(
            skip=skip,
            limit=limit,
            status=status,
            priority=priority,
            requested_by=requested_by,
            department_id=department_id,
            from_date=from_date,
            to_date=to_date,
        )

        total = self.repository.count(
            status=status,
            priority=priority,
            requested_by=requested_by,
            department_id=department_id,
            from_date=from_date,
            to_date=to_date,
        )

        request_responses = [
            PurchaseRequestResponse.model_validate(r) for r in requests
        ]

        return PurchaseRequestListResponse(
            requests=request_responses,
            total=total,
            page=skip // limit + 1 if limit > 0 else 1,
            page_size=limit,
        )

    def update_purchase_request(
        self, request_id: int, request_data: PurchaseRequestUpdate, updated_by: int
    ) -> PurchaseRequestResponse:
        """
        Update purchase request (only allowed in DRAFT status)

        Args:
            request_id: Purchase request ID
            request_data: Update data
            updated_by: User ID performing update

        Returns:
            PurchaseRequestResponse: Updated purchase request

        Raises:
            HTTPException: If purchase request not found or not in DRAFT status
        """
        purchase_request = self.repository.get_by_id(request_id)

        if not purchase_request:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Purchase request with ID {request_id} not found",
            )

        # Only allow updates for DRAFT requests
        if purchase_request.approval_status != ApprovalStatus.DRAFT:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot update purchase request in {purchase_request.approval_status.value} status",
            )

        try:
            update_dict = request_data.model_dump(exclude_unset=True)
            purchase_request = self.repository.update(purchase_request, update_dict)
            self.db.commit()

            logger.info(
                f"Purchase request updated: {purchase_request.request_code} by user {updated_by}"
            )

            return PurchaseRequestResponse.model_validate(purchase_request)

        except Exception as e:
            self.db.rollback()
            logger.error(f"Error updating purchase request: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update purchase request",
            )

    def submit_for_approval(
        self, request_id: int, submitted_by: int
    ) -> PurchaseRequestResponse:
        """
        Submit purchase request for approval (DRAFT -> PENDING)

        Args:
            request_id: Purchase request ID
            submitted_by: User ID submitting the request

        Returns:
            PurchaseRequestResponse: Updated purchase request

        Raises:
            HTTPException: If purchase request not found or not in DRAFT status
        """
        purchase_request = self.repository.get_by_id(request_id)

        if not purchase_request:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Purchase request with ID {request_id} not found",
            )

        if purchase_request.approval_status != ApprovalStatus.DRAFT:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot submit purchase request in {purchase_request.approval_status.value} status",
            )

        # Verify requester is submitting their own request
        if purchase_request.requested_by != submitted_by:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only submit your own purchase requests",
            )

        try:
            purchase_request.approval_status = ApprovalStatus.PENDING
            self.db.commit()

            # Publish event
            publish_event(
                EventTypes.PURCHASE_REQUEST_SUBMITTED,
                {
                    "id": purchase_request.id,
                    "request_code": purchase_request.request_code,
                    "submitted_by": submitted_by,
                    "status": ApprovalStatus.PENDING.value,
                },
            )

            logger.info(
                f"Purchase request submitted: {purchase_request.request_code} by user {submitted_by}"
            )

            return PurchaseRequestResponse.model_validate(purchase_request)

        except Exception as e:
            self.db.rollback()
            logger.error(f"Error submitting purchase request: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to submit purchase request",
            )

    def approve_level1(
        self, request_id: int, approval_data: ApprovalRequest, approved_by: int
    ) -> PurchaseRequestResponse:
        """
        Level 1 approval (Department Manager) - PENDING -> LEVEL1_APPROVED

        Args:
            request_id: Purchase request ID
            approval_data: Approval notes
            approved_by: User ID approving the request

        Returns:
            PurchaseRequestResponse: Updated purchase request

        Raises:
            HTTPException: If purchase request not found or not in PENDING status
        """
        purchase_request = self.repository.get_by_id(request_id)

        if not purchase_request:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Purchase request with ID {request_id} not found",
            )

        if purchase_request.approval_status != ApprovalStatus.PENDING:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Purchase request is in {purchase_request.approval_status.value} status, expected PENDING",
            )

        try:
            purchase_request.approval_status = ApprovalStatus.LEVEL1_APPROVED
            purchase_request.level1_approved_by = approved_by
            purchase_request.level1_approved_at = datetime.now()
            purchase_request.level1_notes = approval_data.notes

            self.db.commit()

            # Publish event
            publish_event(
                EventTypes.PURCHASE_REQUEST_LEVEL1_APPROVED,
                {
                    "id": purchase_request.id,
                    "request_code": purchase_request.request_code,
                    "approved_by": approved_by,
                    "status": ApprovalStatus.LEVEL1_APPROVED.value,
                },
            )

            logger.info(
                f"Purchase request Level 1 approved: {purchase_request.request_code} by user {approved_by}"
            )

            return PurchaseRequestResponse.model_validate(purchase_request)

        except Exception as e:
            self.db.rollback()
            logger.error(f"Error approving purchase request (Level 1): {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to approve purchase request",
            )

    def approve_level2(
        self, request_id: int, approval_data: ApprovalRequest, approved_by: int
    ) -> PurchaseRequestResponse:
        """
        Level 2 approval (HR Manager) - LEVEL1_APPROVED -> LEVEL2_APPROVED

        Args:
            request_id: Purchase request ID
            approval_data: Approval notes
            approved_by: User ID approving the request

        Returns:
            PurchaseRequestResponse: Updated purchase request

        Raises:
            HTTPException: If purchase request not found or not in LEVEL1_APPROVED status
        """
        purchase_request = self.repository.get_by_id(request_id)

        if not purchase_request:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Purchase request with ID {request_id} not found",
            )

        if purchase_request.approval_status != ApprovalStatus.LEVEL1_APPROVED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Purchase request is in {purchase_request.approval_status.value} status, expected LEVEL1_APPROVED",
            )

        try:
            purchase_request.approval_status = ApprovalStatus.LEVEL2_APPROVED
            purchase_request.level2_approved_by = approved_by
            purchase_request.level2_approved_at = datetime.now()
            purchase_request.level2_notes = approval_data.notes

            self.db.commit()

            # Publish event
            publish_event(
                EventTypes.PURCHASE_REQUEST_LEVEL2_APPROVED,
                {
                    "id": purchase_request.id,
                    "request_code": purchase_request.request_code,
                    "approved_by": approved_by,
                    "status": ApprovalStatus.LEVEL2_APPROVED.value,
                },
            )

            logger.info(
                f"Purchase request Level 2 approved: {purchase_request.request_code} by user {approved_by}"
            )

            return PurchaseRequestResponse.model_validate(purchase_request)

        except Exception as e:
            self.db.rollback()
            logger.error(f"Error approving purchase request (Level 2): {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to approve purchase request",
            )

    def approve_level3(
        self, request_id: int, approval_data: ApprovalRequest, approved_by: int
    ) -> PurchaseRequestResponse:
        """
        Level 3 approval (Director) - LEVEL2_APPROVED -> APPROVED (Final approval)

        Args:
            request_id: Purchase request ID
            approval_data: Approval notes
            approved_by: User ID approving the request

        Returns:
            PurchaseRequestResponse: Updated purchase request

        Raises:
            HTTPException: If purchase request not found or not in LEVEL2_APPROVED status
        """
        purchase_request = self.repository.get_by_id(request_id)

        if not purchase_request:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Purchase request with ID {request_id} not found",
            )

        if purchase_request.approval_status != ApprovalStatus.LEVEL2_APPROVED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Purchase request is in {purchase_request.approval_status.value} status, expected LEVEL2_APPROVED",
            )

        try:
            purchase_request.approval_status = ApprovalStatus.APPROVED
            purchase_request.level3_approved_by = approved_by
            purchase_request.level3_approved_at = datetime.now()
            purchase_request.level3_notes = approval_data.notes

            self.db.commit()

            # Publish event
            publish_event(
                EventTypes.PURCHASE_REQUEST_APPROVED,
                {
                    "id": purchase_request.id,
                    "request_code": purchase_request.request_code,
                    "approved_by": approved_by,
                    "status": ApprovalStatus.APPROVED.value,
                    "approved_at": str(purchase_request.level3_approved_at),
                },
            )

            logger.info(
                f"Purchase request FULLY APPROVED: {purchase_request.request_code} by user {approved_by}"
            )

            return PurchaseRequestResponse.model_validate(purchase_request)

        except Exception as e:
            self.db.rollback()
            logger.error(f"Error approving purchase request (Level 3): {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to approve purchase request",
            )

    def reject_purchase_request(
        self, request_id: int, rejection_data: RejectionRequest, rejected_by: int
    ) -> PurchaseRequestResponse:
        """
        Reject purchase request at any approval level

        Args:
            request_id: Purchase request ID
            rejection_data: Rejection reason
            rejected_by: User ID rejecting the request

        Returns:
            PurchaseRequestResponse: Updated purchase request

        Raises:
            HTTPException: If purchase request not found or already in terminal status
        """
        purchase_request = self.repository.get_by_id(request_id)

        if not purchase_request:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Purchase request with ID {request_id} not found",
            )

        # Cannot reject if already approved, rejected, or cancelled
        if purchase_request.approval_status in [
            ApprovalStatus.APPROVED,
            ApprovalStatus.REJECTED,
            ApprovalStatus.CANCELLED,
        ]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot reject purchase request in {purchase_request.approval_status.value} status",
            )

        try:
            purchase_request.approval_status = ApprovalStatus.REJECTED
            purchase_request.rejected_by = rejected_by
            purchase_request.rejected_at = datetime.now()
            purchase_request.rejection_reason = rejection_data.reason

            self.db.commit()

            # Publish event
            publish_event(
                EventTypes.PURCHASE_REQUEST_REJECTED,
                {
                    "id": purchase_request.id,
                    "request_code": purchase_request.request_code,
                    "rejected_by": rejected_by,
                    "reason": rejection_data.reason,
                    "rejected_at": str(purchase_request.rejected_at),
                },
            )

            logger.warning(
                f"Purchase request rejected: {purchase_request.request_code} by user {rejected_by}"
            )

            return PurchaseRequestResponse.model_validate(purchase_request)

        except Exception as e:
            self.db.rollback()
            logger.error(f"Error rejecting purchase request: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to reject purchase request",
            )

    def cancel_purchase_request(
        self, request_id: int, cancelled_by: int
    ) -> PurchaseRequestResponse:
        """
        Cancel purchase request (only by requester, only in DRAFT or PENDING status)

        Args:
            request_id: Purchase request ID
            cancelled_by: User ID cancelling the request

        Returns:
            PurchaseRequestResponse: Updated purchase request

        Raises:
            HTTPException: If purchase request not found or cannot be cancelled
        """
        purchase_request = self.repository.get_by_id(request_id)

        if not purchase_request:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Purchase request with ID {request_id} not found",
            )

        # Only requester can cancel
        if purchase_request.requested_by != cancelled_by:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only cancel your own purchase requests",
            )

        # Can only cancel DRAFT or PENDING requests
        if purchase_request.approval_status not in [
            ApprovalStatus.DRAFT,
            ApprovalStatus.PENDING,
        ]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot cancel purchase request in {purchase_request.approval_status.value} status",
            )

        try:
            purchase_request.approval_status = ApprovalStatus.CANCELLED
            self.db.commit()

            # Publish event
            publish_event(
                EventTypes.PURCHASE_REQUEST_CANCELLED,
                {
                    "id": purchase_request.id,
                    "request_code": purchase_request.request_code,
                    "cancelled_by": cancelled_by,
                },
            )

            logger.info(
                f"Purchase request cancelled: {purchase_request.request_code} by user {cancelled_by}"
            )

            return PurchaseRequestResponse.model_validate(purchase_request)

        except Exception as e:
            self.db.rollback()
            logger.error(f"Error cancelling purchase request: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to cancel purchase request",
            )

    def get_pending_approvals(
        self, approver_level: int = 1
    ) -> List[PurchaseRequestResponse]:
        """
        Get purchase requests pending approval at a specific level

        Args:
            approver_level: Approval level (1, 2, or 3)

        Returns:
            List[PurchaseRequestResponse]: Purchase requests pending approval
        """
        requests = self.repository.get_pending_approvals(approver_level)
        return [PurchaseRequestResponse.model_validate(r) for r in requests]
