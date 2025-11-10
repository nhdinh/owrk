"""
Purchase Order Service
Business logic for purchase order management
"""

from typing import Optional, Tuple
from datetime import datetime, date
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.purchase_order import PurchaseOrder, PurchaseOrderItem, OrderStatus, PaymentStatus
from app.models.quotation import QuotationStatus
from app.repositories.purchase_order_repository import PurchaseOrderRepository
from app.repositories.quotation_repository import QuotationRepository
from app.repositories.vendor_repository import VendorRepository
from app.schemas.purchase_order_schema import (
    PurchaseOrderCreate,
    PurchaseOrderUpdate,
    ReceiveOrderRequest
)
from app.utils.code_generator import generate_purchase_order_code


class PurchaseOrderService:
    """Service for purchase order business logic"""

    def __init__(
        self,
        db: Session,
        order_repo: PurchaseOrderRepository,
        quotation_repo: QuotationRepository,
        purchase_request_repo,  # PurchaseRequestRepository
        vendor_repo: VendorRepository
    ):
        self.db = db
        self.order_repo = order_repo
        self.quotation_repo = quotation_repo
        self.purchase_request_repo = purchase_request_repo
        self.vendor_repo = vendor_repo

    def create_purchase_order(
        self,
        po_data: PurchaseOrderCreate,
        user_id: int
    ) -> PurchaseOrder:
        """Create a new purchase order from accepted quotation"""

        # Validate quotation exists and is accepted
        quotation = self.quotation_repo.get_by_id(po_data.quotation_id)
        if not quotation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Quotation not found"
            )

        if quotation.status != QuotationStatus.ACCEPTED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only accepted quotations can be converted to purchase orders"
            )

        # Check if quotation already has a purchase order
        existing_po = self.order_repo.get_by_quotation(quotation.id)
        if existing_po:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Purchase order already exists for this quotation: {existing_po.order_code}"
            )

        # Validate vendor exists
        vendor = self.vendor_repo.get_by_id(quotation.vendor_id)
        if not vendor:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Vendor not found"
            )

        # Generate order code
        order_code = generate_purchase_order_code(self.db, vendor.vendor_code)

        # Create purchase order
        purchase_order = PurchaseOrder(
            order_code=order_code,
            purchase_request_id=quotation.purchase_request_id,
            quotation_id=quotation.id,
            vendor_id=quotation.vendor_id,
            order_date=po_data.order_date or date.today(),
            expected_delivery_date=po_data.expected_delivery_date,
            subtotal=quotation.total_amount,
            tax_amount=quotation.tax_amount or 0,
            discount_amount=quotation.discount_amount or 0,
            total_amount=quotation.final_amount,
            delivery_address=po_data.delivery_address,
            delivery_contact=po_data.delivery_contact,
            delivery_phone=po_data.delivery_phone,
            payment_terms=quotation.payment_terms,
            payment_status=PaymentStatus.PENDING,
            status=OrderStatus.PENDING,
            notes=po_data.notes,
            created_by=user_id
        )

        # Copy quotation items to purchase order items
        for q_item in quotation.items:
            po_item = PurchaseOrderItem(
                purchase_order=purchase_order,
                quotation_item_id=q_item.id,
                product_name=q_item.product_name,
                product_description=q_item.product_description,
                unit=q_item.unit,
                quantity=q_item.quantity,
                unit_price=q_item.unit_price,
                total_price=q_item.total_price,
                received_quantity=0
            )
            purchase_order.items.append(po_item)

        return self.order_repo.create(purchase_order)

    def get_purchase_order(self, order_id: int) -> PurchaseOrder:
        """Get purchase order by ID"""
        order = self.order_repo.get_by_id(order_id)
        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Purchase order not found"
            )
        return order

    def get_purchase_orders(
        self,
        skip: int = 0,
        limit: int = 100,
        status: Optional[str] = None,
        payment_status: Optional[str] = None,
        vendor_id: Optional[int] = None,
        purchase_request_id: Optional[int] = None,
        from_date: Optional[date] = None,
        to_date: Optional[date] = None
    ) -> Tuple[list[PurchaseOrder], int]:
        """Get purchase orders with filters"""
        return self.order_repo.get_all(
            skip=skip,
            limit=limit,
            status=status,
            payment_status=payment_status,
            vendor_id=vendor_id,
            purchase_request_id=purchase_request_id,
            from_date=from_date,
            to_date=to_date
        )

    def update_purchase_order(
        self,
        order_id: int,
        po_data: PurchaseOrderUpdate,
        user_id: int
    ) -> PurchaseOrder:
        """Update purchase order"""
        order = self.get_purchase_order(order_id)

        # Only pending orders can be updated
        if order.status != OrderStatus.PENDING:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only pending orders can be updated"
            )

        # Update fields
        if po_data.expected_delivery_date is not None:
            order.expected_delivery_date = po_data.expected_delivery_date
        if po_data.delivery_address is not None:
            order.delivery_address = po_data.delivery_address
        if po_data.delivery_contact is not None:
            order.delivery_contact = po_data.delivery_contact
        if po_data.delivery_phone is not None:
            order.delivery_phone = po_data.delivery_phone
        if po_data.payment_terms is not None:
            order.payment_terms = po_data.payment_terms
        if po_data.notes is not None:
            order.notes = po_data.notes

        return self.order_repo.update(order)

    def delete_purchase_order(self, order_id: int, user_id: int) -> None:
        """Delete purchase order (only pending)"""
        order = self.get_purchase_order(order_id)

        if order.status != OrderStatus.PENDING:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only pending orders can be deleted"
            )

        self.order_repo.delete(order)

    def confirm_purchase_order(self, order_id: int, user_id: int) -> PurchaseOrder:
        """Confirm purchase order"""
        order = self.get_purchase_order(order_id)

        if order.status != OrderStatus.PENDING:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only pending orders can be confirmed"
            )

        order.status = OrderStatus.CONFIRMED
        return self.order_repo.update(order)

    def send_purchase_order(self, order_id: int, user_id: int) -> PurchaseOrder:
        """Send purchase order to vendor"""
        order = self.get_purchase_order(order_id)

        if order.status != OrderStatus.CONFIRMED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only confirmed orders can be sent"
            )

        order.status = OrderStatus.PROCESSING
        return self.order_repo.update(order)

    def ship_purchase_order(self, order_id: int, user_id: int) -> PurchaseOrder:
        """Mark purchase order as shipped"""
        order = self.get_purchase_order(order_id)

        if order.status != OrderStatus.PROCESSING:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only processing orders can be marked as shipped"
            )

        order.status = OrderStatus.SHIPPED
        return self.order_repo.update(order)

    def receive_purchase_order(
        self,
        order_id: int,
        request: ReceiveOrderRequest,
        user_id: int
    ) -> PurchaseOrder:
        """Receive items from purchase order"""
        order = self.get_purchase_order(order_id)

        if order.status not in [OrderStatus.SHIPPED, OrderStatus.PROCESSING]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only shipped or processing orders can be received"
            )

        # Update received quantities
        for item_data in request.items:
            item = next((i for i in order.items if i.id == item_data.item_id), None)
            if not item:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Order item {item_data.item_id} not found"
                )
            item.received_quantity = item_data.received_quantity

        order.status = OrderStatus.DELIVERED
        order.actual_delivery_date = date.today()

        if request.notes:
            order.notes = f"{order.notes}\n\nReceiving notes: {request.notes}" if order.notes else f"Receiving notes: {request.notes}"

        return self.order_repo.update(order)

    def complete_purchase_order(self, order_id: int, user_id: int) -> PurchaseOrder:
        """Complete purchase order"""
        order = self.get_purchase_order(order_id)

        if order.status != OrderStatus.DELIVERED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only delivered orders can be completed"
            )

        order.status = OrderStatus.COMPLETED
        order.payment_status = PaymentStatus.PAID
        return self.order_repo.update(order)

    def cancel_purchase_order(
        self,
        order_id: int,
        reason: str,
        user_id: int
    ) -> PurchaseOrder:
        """Cancel purchase order"""
        order = self.get_purchase_order(order_id)

        if order.status in [OrderStatus.COMPLETED, OrderStatus.CANCELLED]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Completed or already cancelled orders cannot be cancelled"
            )

        order.status = OrderStatus.CANCELLED
        order.notes = f"{order.notes}\n\nCancellation reason: {reason}" if order.notes else f"Cancellation reason: {reason}"

        return self.order_repo.update(order)
