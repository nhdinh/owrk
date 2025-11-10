"""
Code generation utilities
Generates unique codes for vendors, contracts, requests, quotations, and orders
"""

from datetime import datetime
from sqlalchemy.orm import Session
from typing import Optional


def generate_vendor_code(db: Session) -> str:
    """
    Generate unique vendor code
    Format: VND{YYYYMMDD}{sequential_number}
    Example: VND202511020001

    Args:
        db: Database session

    Returns:
        str: Unique vendor code
    """
    from app.models.vendor import Vendor

    today = datetime.now().strftime("%Y%m%d")
    prefix = f"VND{today}"

    # Get the latest vendor code for today
    latest = (
        db.query(Vendor)
        .filter(Vendor.vendor_code.like(f"{prefix}%"))
        .order_by(Vendor.vendor_code.desc())
        .first()
    )

    if latest:
        # Extract the sequential number and increment
        seq_num = int(latest.vendor_code[-4:]) + 1
    else:
        seq_num = 1

    return f"{prefix}{seq_num:04d}"


def generate_contract_code(db: Session, vendor_code: str) -> str:
    """
    Generate unique framework contract code
    Format: FC{vendor_code}{YYYYMM}{sequential}
    Example: FCVND202511020001202511001

    Args:
        db: Database session
        vendor_code: Associated vendor code

    Returns:
        str: Unique contract code
    """
    from app.models.framework_contract import FrameworkContract

    year_month = datetime.now().strftime("%Y%m")
    prefix = f"FC{vendor_code}{year_month}"

    # Get the latest contract code for this vendor and month
    latest = (
        db.query(FrameworkContract)
        .filter(FrameworkContract.contract_code.like(f"{prefix}%"))
        .order_by(FrameworkContract.contract_code.desc())
        .first()
    )

    if latest:
        seq_num = int(latest.contract_code[-3:]) + 1
    else:
        seq_num = 1

    return f"{prefix}{seq_num:03d}"


def generate_request_code(db: Session, department_id: Optional[int] = None) -> str:
    """
    Generate unique purchase request code
    Format: PR{YYYYMMDD}{dept_id}{sequential}
    Example: PR20251102005001

    Args:
        db: Database session
        department_id: Department ID (optional)

    Returns:
        str: Unique request code
    """
    from app.models.purchase_request import PurchaseRequest

    today = datetime.now().strftime("%Y%m%d")
    dept_str = f"{department_id:03d}" if department_id else "000"
    prefix = f"PR{today}{dept_str}"

    # Get the latest request code for today and department
    latest = (
        db.query(PurchaseRequest)
        .filter(PurchaseRequest.request_code.like(f"{prefix}%"))
        .order_by(PurchaseRequest.request_code.desc())
        .first()
    )

    if latest:
        seq_num = int(latest.request_code[-3:]) + 1
    else:
        seq_num = 1

    return f"{prefix}{seq_num:03d}"


def generate_quotation_code(db: Session, vendor_code: str, request_code: str) -> str:
    """
    Generate unique quotation code
    Format: QT{request_code}{vendor_code_last4}{sequential}
    Example: QTPR202511020050010001001

    Args:
        db: Database session
        vendor_code: Vendor code
        request_code: Purchase request code

    Returns:
        str: Unique quotation code
    """
    from app.models.quotation import Quotation

    vendor_suffix = vendor_code[-4:]  # Last 4 digits of vendor code
    prefix = f"QT{request_code}{vendor_suffix}"

    # Get the latest quotation code for this request and vendor
    latest = (
        db.query(Quotation)
        .filter(Quotation.quotation_code.like(f"{prefix}%"))
        .order_by(Quotation.quotation_code.desc())
        .first()
    )

    if latest:
        seq_num = int(latest.quotation_code[-3:]) + 1
    else:
        seq_num = 1

    return f"{prefix}{seq_num:03d}"


def generate_order_code(db: Session, quotation_code: str) -> str:
    """
    Generate unique purchase order code
    Format: PO{YYYYMMDD}{quotation_code_last6}{sequential}
    Example: PO20251102001001001

    Args:
        db: Database session
        quotation_code: Selected quotation code

    Returns:
        str: Unique order code
    """
    from app.models.purchase_order import PurchaseOrder

    today = datetime.now().strftime("%Y%m%d")
    quotation_suffix = quotation_code[-6:]  # Last 6 digits of quotation code
    prefix = f"PO{today}{quotation_suffix}"

    # Get the latest order code for today and quotation
    latest = (
        db.query(PurchaseOrder)
        .filter(PurchaseOrder.order_code.like(f"{prefix}%"))
        .order_by(PurchaseOrder.order_code.desc())
        .first()
    )

    if latest:
        seq_num = int(latest.order_code[-3:]) + 1
    else:
        seq_num = 1

    return f"{prefix}{seq_num:03d}"


def generate_purchase_order_code(db: Session, vendor_code: str) -> str:
    """
    Generate unique purchase order code (alternative format)
    Format: PO{vendor_code}{YYYYMMDD}{sequential}
    Example: POVND202511020001202511020001

    Args:
        db: Database session
        vendor_code: Vendor code

    Returns:
        str: Unique order code
    """
    from app.models.purchase_order import PurchaseOrder

    today = datetime.now().strftime("%Y%m%d")
    prefix = f"PO{vendor_code}{today}"

    # Get the latest order code for this vendor and today
    latest = (
        db.query(PurchaseOrder)
        .filter(PurchaseOrder.order_code.like(f"{prefix}%"))
        .order_by(PurchaseOrder.order_code.desc())
        .first()
    )

    if latest:
        seq_num = int(latest.order_code[-4:]) + 1
    else:
        seq_num = 1

    return f"{prefix}{seq_num:04d}"


def generate_item_code(entity_type: str, entity_id: int, item_sequence: int) -> str:
    """
    Generate unique item code for request/quotation/order items
    Format: {entity_type}{entity_id}{sequence}
    Example: PRI0000000001 (Purchase Request Item 1)

    Args:
        entity_type: Type of entity (PRI, QTI, POI)
        entity_id: Parent entity ID
        item_sequence: Item sequence number

    Returns:
        str: Unique item code
    """
    return f"{entity_type}{entity_id:06d}{item_sequence:03d}"
