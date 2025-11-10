"""
Purchase Order API Endpoints
RESTful API for purchase order management
"""

from typing import Optional
from datetime import date
from fastapi import APIRouter, Depends, Query, Path
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.purchase_order import OrderStatus, PaymentStatus
from app.schemas.purchase_order_schema import (
    PurchaseOrderCreate,
    PurchaseOrderUpdate,
    PurchaseOrderResponse,
    PurchaseOrderListResponse,
    ConfirmOrderRequest,
    SendOrderRequest,
    ShipOrderRequest,
    ReceiveOrderRequest,
    CompleteOrderRequest,
    CancelOrderRequest,
)

router = APIRouter(prefix="/purchase-orders", tags=["Purchase Orders"])


@router.post("/", response_model=PurchaseOrderResponse, status_code=201)
async def create_purchase_order(
    po_data: PurchaseOrderCreate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create a new purchase order from an accepted quotation"""
    from app.services.purchase_order_service import PurchaseOrderService
    from app.repositories.purchase_order_repository import PurchaseOrderRepository
    from app.repositories.quotation_repository import QuotationRepository
    from app.repositories.purchase_request_repository import PurchaseRequestRepository
    from app.repositories.vendor_repository import VendorRepository

    service = PurchaseOrderService(
        db,
        PurchaseOrderRepository(db),
        QuotationRepository(db),
        PurchaseRequestRepository(db),
        VendorRepository(db),
    )
    return service.create_purchase_order(po_data, current_user["id"])


@router.get("/", response_model=PurchaseOrderListResponse)
async def list_purchase_orders(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    status: Optional[OrderStatus] = Query(None),
    payment_status: Optional[PaymentStatus] = Query(None),
    vendor_id: Optional[int] = Query(None),
    purchase_request_id: Optional[int] = Query(None),
    from_date: Optional[date] = Query(None),
    to_date: Optional[date] = Query(None),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List purchase orders with pagination and filters"""
    from app.services.purchase_order_service import PurchaseOrderService
    from app.repositories.purchase_order_repository import PurchaseOrderRepository
    from app.repositories.quotation_repository import QuotationRepository
    from app.repositories.purchase_request_repository import PurchaseRequestRepository
    from app.repositories.vendor_repository import VendorRepository

    service = PurchaseOrderService(
        db,
        PurchaseOrderRepository(db),
        QuotationRepository(db),
        PurchaseRequestRepository(db),
        VendorRepository(db),
    )

    orders, total = service.get_purchase_orders(
        skip=skip,
        limit=limit,
        status=status.value if status else None,
        payment_status=payment_status.value if payment_status else None,
        vendor_id=vendor_id,
        purchase_request_id=purchase_request_id,
        from_date=from_date,
        to_date=to_date,
    )

    return PurchaseOrderListResponse(
        purchase_orders=orders, total=total, page=skip // limit + 1, page_size=limit
    )


@router.get("/{order_id}", response_model=PurchaseOrderResponse)
async def get_purchase_order(
    order_id: int = Path(..., gt=0),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get purchase order by ID"""
    from app.services.purchase_order_service import PurchaseOrderService
    from app.repositories.purchase_order_repository import PurchaseOrderRepository
    from app.repositories.quotation_repository import QuotationRepository
    from app.repositories.purchase_request_repository import PurchaseRequestRepository
    from app.repositories.vendor_repository import VendorRepository

    service = PurchaseOrderService(
        db,
        PurchaseOrderRepository(db),
        QuotationRepository(db),
        PurchaseRequestRepository(db),
        VendorRepository(db),
    )
    return service.get_purchase_order(order_id)


@router.put("/{order_id}", response_model=PurchaseOrderResponse)
async def update_purchase_order(
    order_id: int,
    po_data: PurchaseOrderUpdate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update purchase order"""
    from app.services.purchase_order_service import PurchaseOrderService
    from app.repositories.purchase_order_repository import PurchaseOrderRepository
    from app.repositories.quotation_repository import QuotationRepository
    from app.repositories.purchase_request_repository import PurchaseRequestRepository
    from app.repositories.vendor_repository import VendorRepository

    service = PurchaseOrderService(
        db,
        PurchaseOrderRepository(db),
        QuotationRepository(db),
        PurchaseRequestRepository(db),
        VendorRepository(db),
    )
    return service.update_purchase_order(order_id, po_data, current_user["id"])


@router.delete("/{order_id}", status_code=204)
async def delete_purchase_order(
    order_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete purchase order (only pending orders)"""
    from app.services.purchase_order_service import PurchaseOrderService
    from app.repositories.purchase_order_repository import PurchaseOrderRepository
    from app.repositories.quotation_repository import QuotationRepository
    from app.repositories.purchase_request_repository import PurchaseRequestRepository
    from app.repositories.vendor_repository import VendorRepository

    service = PurchaseOrderService(
        db,
        PurchaseOrderRepository(db),
        QuotationRepository(db),
        PurchaseRequestRepository(db),
        VendorRepository(db),
    )
    service.delete_purchase_order(order_id, current_user["id"])
    return None


@router.post("/{order_id}/confirm", response_model=PurchaseOrderResponse)
async def confirm_purchase_order(
    order_id: int,
    request: ConfirmOrderRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Confirm a purchase order"""
    from app.services.purchase_order_service import PurchaseOrderService
    from app.repositories.purchase_order_repository import PurchaseOrderRepository
    from app.repositories.quotation_repository import QuotationRepository
    from app.repositories.purchase_request_repository import PurchaseRequestRepository
    from app.repositories.vendor_repository import VendorRepository

    service = PurchaseOrderService(
        db,
        PurchaseOrderRepository(db),
        QuotationRepository(db),
        PurchaseRequestRepository(db),
        VendorRepository(db),
    )
    return service.confirm_purchase_order(order_id, current_user["id"])


@router.post("/{order_id}/send", response_model=PurchaseOrderResponse)
async def send_purchase_order(
    order_id: int,
    request: SendOrderRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Send purchase order to vendor"""
    from app.services.purchase_order_service import PurchaseOrderService
    from app.repositories.purchase_order_repository import PurchaseOrderRepository
    from app.repositories.quotation_repository import QuotationRepository
    from app.repositories.purchase_request_repository import PurchaseRequestRepository
    from app.repositories.vendor_repository import VendorRepository

    service = PurchaseOrderService(
        db,
        PurchaseOrderRepository(db),
        QuotationRepository(db),
        PurchaseRequestRepository(db),
        VendorRepository(db),
    )
    return service.send_purchase_order(order_id, current_user["id"])


@router.post("/{order_id}/ship", response_model=PurchaseOrderResponse)
async def ship_purchase_order(
    order_id: int,
    request: ShipOrderRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Mark purchase order as shipped"""
    from app.services.purchase_order_service import PurchaseOrderService
    from app.repositories.purchase_order_repository import PurchaseOrderRepository
    from app.repositories.quotation_repository import QuotationRepository
    from app.repositories.purchase_request_repository import PurchaseRequestRepository
    from app.repositories.vendor_repository import VendorRepository

    service = PurchaseOrderService(
        db,
        PurchaseOrderRepository(db),
        QuotationRepository(db),
        PurchaseRequestRepository(db),
        VendorRepository(db),
    )
    return service.ship_purchase_order(order_id, current_user["id"])


@router.post("/{order_id}/receive", response_model=PurchaseOrderResponse)
async def receive_purchase_order(
    order_id: int,
    request: ReceiveOrderRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Receive purchase order items"""
    from app.services.purchase_order_service import PurchaseOrderService
    from app.repositories.purchase_order_repository import PurchaseOrderRepository
    from app.repositories.quotation_repository import QuotationRepository
    from app.repositories.purchase_request_repository import PurchaseRequestRepository
    from app.repositories.vendor_repository import VendorRepository

    service = PurchaseOrderService(
        db,
        PurchaseOrderRepository(db),
        QuotationRepository(db),
        PurchaseRequestRepository(db),
        VendorRepository(db),
    )
    return service.receive_purchase_order(order_id, request, current_user["id"])


@router.post("/{order_id}/complete", response_model=PurchaseOrderResponse)
async def complete_purchase_order(
    order_id: int,
    request: CompleteOrderRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Complete purchase order (creates assets)"""
    from app.services.purchase_order_service import PurchaseOrderService
    from app.repositories.purchase_order_repository import PurchaseOrderRepository
    from app.repositories.quotation_repository import QuotationRepository
    from app.repositories.purchase_request_repository import PurchaseRequestRepository
    from app.repositories.vendor_repository import VendorRepository

    service = PurchaseOrderService(
        db,
        PurchaseOrderRepository(db),
        QuotationRepository(db),
        PurchaseRequestRepository(db),
        VendorRepository(db),
    )
    return service.complete_purchase_order(order_id, current_user["id"])


@router.post("/{order_id}/cancel", response_model=PurchaseOrderResponse)
async def cancel_purchase_order(
    order_id: int,
    request: CancelOrderRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Cancel a purchase order"""
    from app.services.purchase_order_service import PurchaseOrderService
    from app.repositories.purchase_order_repository import PurchaseOrderRepository
    from app.repositories.quotation_repository import QuotationRepository
    from app.repositories.purchase_request_repository import PurchaseRequestRepository
    from app.repositories.vendor_repository import VendorRepository

    service = PurchaseOrderService(
        db,
        PurchaseOrderRepository(db),
        QuotationRepository(db),
        PurchaseRequestRepository(db),
        VendorRepository(db),
    )
    return service.cancel_purchase_order(order_id, request.reason, current_user["id"])
