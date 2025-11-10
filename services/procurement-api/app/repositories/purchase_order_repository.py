"""
Purchase Order Repository
Handles database operations for purchase orders
"""

from typing import Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from datetime import datetime, date

from app.models.purchase_order import PurchaseOrder, PurchaseOrderItem, OrderStatus, PaymentStatus


class PurchaseOrderRepository:
    """Repository for PurchaseOrder database operations"""

    def __init__(self, db: Session):
        self.db = db

    def create(self, purchase_order: PurchaseOrder) -> PurchaseOrder:
        """Create a new purchase order"""
        self.db.add(purchase_order)
        self.db.commit()
        self.db.refresh(purchase_order)
        return purchase_order

    def get_by_id(self, order_id: int) -> Optional[PurchaseOrder]:
        """Get purchase order by ID"""
        return (
            self.db.query(PurchaseOrder)
            .filter(PurchaseOrder.id == order_id)
            .first()
        )

    def get_by_code(self, order_code: str) -> Optional[PurchaseOrder]:
        """Get purchase order by code"""
        return (
            self.db.query(PurchaseOrder)
            .filter(PurchaseOrder.order_code == order_code)
            .first()
        )

    def get_by_quotation(self, quotation_id: int) -> Optional[PurchaseOrder]:
        """Get purchase order by quotation ID"""
        return (
            self.db.query(PurchaseOrder)
            .filter(PurchaseOrder.quotation_id == quotation_id)
            .first()
        )

    def get_by_vendor(
        self,
        vendor_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> list[PurchaseOrder]:
        """Get purchase orders by vendor ID"""
        return (
            self.db.query(PurchaseOrder)
            .filter(PurchaseOrder.vendor_id == vendor_id)
            .order_by(PurchaseOrder.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_all(
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
        """Get all purchase orders with filters"""
        query = self.db.query(PurchaseOrder)

        # Apply filters
        if status:
            query = query.filter(PurchaseOrder.status == status)

        if payment_status:
            query = query.filter(PurchaseOrder.payment_status == payment_status)

        if vendor_id:
            query = query.filter(PurchaseOrder.vendor_id == vendor_id)

        if purchase_request_id:
            query = query.filter(PurchaseOrder.purchase_request_id == purchase_request_id)

        if from_date:
            query = query.filter(PurchaseOrder.order_date >= from_date)

        if to_date:
            query = query.filter(PurchaseOrder.order_date <= to_date)

        # Get total count
        total = query.count()

        # Get paginated results
        orders = (
            query
            .order_by(PurchaseOrder.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

        return orders, total

    def update(self, purchase_order: PurchaseOrder) -> PurchaseOrder:
        """Update purchase order"""
        self.db.commit()
        self.db.refresh(purchase_order)
        return purchase_order

    def delete(self, purchase_order: PurchaseOrder) -> None:
        """Delete purchase order (only if pending)"""
        if purchase_order.status != OrderStatus.PENDING:
            raise ValueError("Only pending orders can be deleted")
        self.db.delete(purchase_order)
        self.db.commit()

    def get_by_status(
        self,
        status: OrderStatus,
        skip: int = 0,
        limit: int = 100
    ) -> list[PurchaseOrder]:
        """Get purchase orders by status"""
        return (
            self.db.query(PurchaseOrder)
            .filter(PurchaseOrder.status == status)
            .order_by(PurchaseOrder.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )
