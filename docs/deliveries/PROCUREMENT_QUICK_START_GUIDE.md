# Procurement Module - Quick Start Implementation Guide

**Date**: 2025-11-02
**Status**: 🚀 Ready to Implement
**Estimated Time**: 15 days

---

## Overview

This guide provides step-by-step instructions to implement the Procurement module using the detailed plan in [PROCUREMENT_MODULE_IMPLEMENTATION_PLAN.md](PROCUREMENT_MODULE_IMPLEMENTATION_PLAN.md).

---

## Prerequisites

✅ **Completed**:
- Directory structure created: `services/procurement-api/`
- Core configuration files created:
  - `app/core/config.py`
  - `app/core/database.py`
- Base model created: `app/models/base.py`
- Vendor model created: `app/models/vendor.py`

⏸️ **Pending**:
- Remaining models (purchase_request, framework_contract, quotation, purchase_order)
- Pydantic schemas
- Repositories
- Services
- API endpoints
- Alembic migrations
- Docker configuration

---

## Phase 1: Foundation (Days 1-2)

### Step 1.1: Create Remaining Models

Create the following model files in `services/procurement-api/app/models/`:

**1. Framework Contract Model** (`framework_contract.py`):

```python
from sqlalchemy import Column, Integer, String, DECIMAL, DATE, TIMESTAMP, Text, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.models.base import Base
import enum

class ContractStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    EXPIRED = "EXPIRED"
    TERMINATED = "TERMINATED"

class FrameworkContract(Base):
    __tablename__ = "framework_contracts"
    __table_args__ = {"schema": "procurement_db"}

    id = Column(Integer, primary_key=True, autoincrement=True)
    contract_code = Column(String(50), unique=True, nullable=False, index=True)
    contract_name = Column(String(255), nullable=False)
    vendor_id = Column(Integer, ForeignKey('procurement_db.vendors.id'), nullable=False, index=True)

    # Contract Information
    contract_value = Column(DECIMAL(15, 2), nullable=False)
    start_date = Column(DATE, nullable=False, index=True)
    end_date = Column(DATE, nullable=False, index=True)

    # Terms
    terms_and_conditions = Column(Text)
    payment_terms = Column(Text)
    delivery_terms = Column(Text)

    # Attachments
    contract_file_url = Column(String(500))

    # Status
    status = Column(SQLEnum(ContractStatus), nullable=False, default=ContractStatus.ACTIVE, index=True)

    # Metadata
    created_by = Column(Integer, nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    # Relationships
    vendor = relationship("Vendor", back_populates="contracts")
```

**2. Purchase Request Model** (`purchase_request.py`):

```python
from sqlalchemy import Column, Integer, String, DECIMAL, DATE, TIMESTAMP, Text, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.models.base import Base
import enum

class Priority(str, enum.Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    URGENT = "URGENT"

class ProcurementType(str, enum.Enum):
    FRAMEWORK_CONTRACT = "FRAMEWORK_CONTRACT"
    ONE_TIME = "ONE_TIME"

class ApprovalStatus(str, enum.Enum):
    DRAFT = "DRAFT"
    PENDING = "PENDING"
    LEVEL1_APPROVED = "LEVEL1_APPROVED"
    LEVEL2_APPROVED = "LEVEL2_APPROVED"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    CANCELLED = "CANCELLED"

class PurchaseRequest(Base):
    __tablename__ = "purchase_requests"
    __table_args__ = {"schema": "procurement_db"}

    id = Column(Integer, primary_key=True, autoincrement=True)
    request_code = Column(String(50), unique=True, nullable=False, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text)

    # Request Information
    requested_by = Column(Integer, nullable=False, index=True)
    department_id = Column(Integer, nullable=False, index=True)
    priority = Column(SQLEnum(Priority), nullable=False, index=True)
    request_date = Column(DATE, nullable=False, index=True)
    expected_delivery_date = Column(DATE)

    # Procurement Type
    procurement_type = Column(SQLEnum(ProcurementType), nullable=False)
    framework_contract_id = Column(Integer, ForeignKey('procurement_db.framework_contracts.id'))

    # Estimated Total
    estimated_total = Column(DECIMAL(15, 2))

    # Approval Status
    approval_status = Column(SQLEnum(ApprovalStatus), nullable=False, default=ApprovalStatus.DRAFT, index=True)

    # Level 1 Approval (Department Manager)
    level1_approved_by = Column(Integer)
    level1_approved_at = Column(TIMESTAMP)
    level1_notes = Column(Text)

    # Level 2 Approval (HR Manager)
    level2_approved_by = Column(Integer)
    level2_approved_at = Column(TIMESTAMP)
    level2_notes = Column(Text)

    # Level 3 Approval (Director)
    level3_approved_by = Column(Integer)
    level3_approved_at = Column(TIMESTAMP)
    level3_notes = Column(Text)

    # Rejection
    rejected_by = Column(Integer)
    rejected_at = Column(TIMESTAMP)
    rejection_reason = Column(Text)

    # Timestamps
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    deleted_at = Column(TIMESTAMP)

    # Relationships
    items = relationship("PurchaseRequestItem", back_populates="purchase_request", cascade="all, delete-orphan")
    framework_contract = relationship("FrameworkContract")

class PurchaseRequestItem(Base):
    __tablename__ = "purchase_request_items"
    __table_args__ = {"schema": "procurement_db"}

    id = Column(Integer, primary_key=True, autoincrement=True)
    purchase_request_id = Column(Integer, ForeignKey('procurement_db.purchase_requests.id'), nullable=False, index=True)

    # Product Information
    product_name = Column(String(255), nullable=False)
    product_description = Column(Text)
    specification = Column(Text)
    unit = Column(String(50), nullable=False)
    quantity = Column(Integer, nullable=False)

    # Estimated Pricing
    estimated_unit_price = Column(DECIMAL(15, 2))
    estimated_total = Column(DECIMAL(15, 2))

    # Reason
    reason = Column(Text)

    # Timestamps
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    # Relationships
    purchase_request = relationship("PurchaseRequest", back_populates="items")
```

**3. Quotation Model** (`quotation.py`) - Similar structure
**4. Purchase Order Model** (`purchase_order.py`) - Similar structure

### Step 1.2: Create __init__.py for models

```python
# services/procurement-api/app/models/__init__.py
from app.models.base import Base
from app.models.vendor import Vendor, VendorStatus
from app.models.framework_contract import FrameworkContract, ContractStatus
from app.models.purchase_request import (
    PurchaseRequest,
    PurchaseRequestItem,
    Priority,
    ProcurementType,
    ApprovalStatus
)
from app.models.quotation import Quotation, QuotationItem, QuotationStatus
from app.models.purchase_order import (
    PurchaseOrder,
    PurchaseOrderItem,
    OrderStatus,
    PaymentStatus
)

__all__ = [
    "Base",
    "Vendor",
    "VendorStatus",
    "FrameworkContract",
    "ContractStatus",
    "PurchaseRequest",
    "PurchaseRequestItem",
    "Priority",
    "ProcurementType",
    "ApprovalStatus",
    "Quotation",
    "QuotationItem",
    "QuotationStatus",
    "PurchaseOrder",
    "PurchaseOrderItem",
    "OrderStatus",
    "PaymentStatus",
]
```

### Step 1.3: Set Up Alembic

**1. Install Alembic**:
```bash
cd services/procurement-api
pip install alembic
alembic init alembic
```

**2. Configure alembic.ini**:
```ini
[alembic]
script_location = alembic
sqlalchemy.url = mysql+pymysql://admin:secret123@localhost:3306/procurement_db
```

**3. Update alembic/env.py**:
```python
from app.core.config import settings
from app.models import Base

config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)
target_metadata = Base.metadata
```

**4. Create Initial Migration**:
```bash
alembic revision --autogenerate -m "Initial procurement schema"
alembic upgrade head
```

### Step 1.4: Create Dependencies File

**app/core/dependencies.py**:
```python
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from app.core.config import settings
from typing import Dict

security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> Dict:
    """
    Verify JWT token and return current user info
    """
    try:
        token = credentials.credentials
        payload = jwt.decode(
            token,
            settings.JWT_SECRET,
            algorithms=[settings.JWT_ALGORITHM]
        )
        user_id: int = payload.get("sub")
        email: str = payload.get("email")
        role: str = payload.get("role")

        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials"
            )

        return {
            "id": user_id,
            "email": email,
            "role": role
        }
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )

def require_role(required_role: str):
    """
    Dependency to check if user has required role
    """
    def role_checker(current_user: Dict = Depends(get_current_user)):
        user_role = current_user.get("role", "")

        roles_hierarchy = ["Staff", "Manager", "Admin", "Director"]

        if user_role not in roles_hierarchy:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )

        user_level = roles_hierarchy.index(user_role)
        required_level = roles_hierarchy.index(required_role)

        if user_level < required_level:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Required role: {required_role}"
            )

        return current_user

    return role_checker
```

### Step 1.5: Create Event Publishing Utility

**app/core/events.py**:
```python
import json
import aio_pika
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

async def publish_event(event_type: str, data: dict):
    """
    Publish event to RabbitMQ

    Args:
        event_type: Event type (e.g., "PurchaseRequestCreated")
        data: Event data
    """
    try:
        connection = await aio_pika.connect_robust(settings.RABBITMQ_URL)
        async with connection:
            channel = await connection.channel()

            exchange = await channel.declare_exchange(
                "procurement_events",
                aio_pika.ExchangeType.TOPIC,
                durable=True
            )

            message = aio_pika.Message(
                body=json.dumps(data).encode(),
                content_type="application/json",
                delivery_mode=aio_pika.DeliveryMode.PERSISTENT
            )

            await exchange.publish(
                message,
                routing_key=event_type
            )

            logger.info(f"Published event: {event_type}")
    except Exception as e:
        logger.error(f"Failed to publish event {event_type}: {str(e)}")
```

### Step 1.6: Create Dockerfile

**services/procurement-api/Dockerfile**:
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    default-libmysqlclient-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Expose port
EXPOSE 8004

# Run application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8004", "--reload"]
```

### Step 1.7: Create requirements.txt

**services/procurement-api/requirements.txt**:
```txt
# FastAPI
fastapi==0.104.1
uvicorn[standard]==0.24.0
python-multipart==0.0.6

# Database
sqlalchemy==2.0.23
pymysql==1.1.0
alembic==1.12.1
pymongo==4.6.0

# Authentication
python-jose[cryptography]==3.3.0

# Utilities
python-dotenv==1.0.0
pydantic==2.5.0
pydantic-settings==2.1.0
python-dateutil==2.8.2

# File handling
aiofiles==23.2.1

# Message Queue
aio-pika==9.3.0

# Redis
redis==5.0.1

# Email
aiosmtplib==3.0.1
jinja2==3.1.2
```

---

## Phase 2: Vendor Management (Days 3-4)

### Step 2.1: Create Vendor Schemas

**app/schemas/vendor.py**:
```python
from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional
from datetime import datetime
from decimal import Decimal

class VendorBase(BaseModel):
    vendor_code: str = Field(..., max_length=50)
    vendor_name: str = Field(..., max_length=255)
    contact_person: Optional[str] = Field(None, max_length=255)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=50)
    address: Optional[str] = None
    tax_code: Optional[str] = Field(None, max_length=50)
    business_registration: Optional[str] = Field(None, max_length=100)
    bank_account: Optional[str] = Field(None, max_length=100)
    bank_name: Optional[str] = Field(None, max_length=255)
    rating: Optional[Decimal] = Field(default=Decimal("0.00"), ge=0, le=5)
    notes: Optional[str] = None

class VendorCreate(VendorBase):
    pass

class VendorUpdate(BaseModel):
    vendor_name: Optional[str] = Field(None, max_length=255)
    contact_person: Optional[str] = Field(None, max_length=255)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=50)
    address: Optional[str] = None
    tax_code: Optional[str] = Field(None, max_length=50)
    business_registration: Optional[str] = Field(None, max_length=100)
    bank_account: Optional[str] = Field(None, max_length=100)
    bank_name: Optional[str] = Field(None, max_length=255)
    rating: Optional[Decimal] = Field(None, ge=0, le=5)
    status: Optional[str] = Field(None, pattern="^(ACTIVE|INACTIVE|BLACKLISTED)$")
    notes: Optional[str] = None

class VendorResponse(VendorBase):
    id: int
    status: str
    created_by: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class VendorListResponse(BaseModel):
    vendors: list[VendorResponse]
    total: int
    page: int
    page_size: int
```

### Step 2.2: Create Vendor Repository

**app/repositories/vendor_repository.py**:
```python
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import List, Optional
from app.models.vendor import Vendor, VendorStatus

class VendorRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, vendor: Vendor) -> Vendor:
        self.db.add(vendor)
        self.db.commit()
        self.db.refresh(vendor)
        return vendor

    def get_by_id(self, vendor_id: int) -> Optional[Vendor]:
        return self.db.query(Vendor).filter(
            Vendor.id == vendor_id,
            Vendor.deleted_at.is_(None)
        ).first()

    def get_by_code(self, vendor_code: str) -> Optional[Vendor]:
        return self.db.query(Vendor).filter(
            Vendor.vendor_code == vendor_code,
            Vendor.deleted_at.is_(None)
        ).first()

    def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        status: Optional[VendorStatus] = None,
        search: Optional[str] = None
    ) -> List[Vendor]:
        query = self.db.query(Vendor).filter(Vendor.deleted_at.is_(None))

        if status:
            query = query.filter(Vendor.status == status)

        if search:
            query = query.filter(
                or_(
                    Vendor.vendor_name.ilike(f"%{search}%"),
                    Vendor.vendor_code.ilike(f"%{search}%"),
                    Vendor.email.ilike(f"%{search}%")
                )
            )

        return query.offset(skip).limit(limit).all()

    def update(self, vendor: Vendor) -> Vendor:
        self.db.commit()
        self.db.refresh(vendor)
        return vendor

    def delete(self, vendor: Vendor):
        from datetime import datetime
        vendor.deleted_at = datetime.now()
        self.db.commit()

    def count(self, status: Optional[VendorStatus] = None, search: Optional[str] = None) -> int:
        query = self.db.query(Vendor).filter(Vendor.deleted_at.is_(None))

        if status:
            query = query.filter(Vendor.status == status)

        if search:
            query = query.filter(
                or_(
                    Vendor.vendor_name.ilike(f"%{search}%"),
                    Vendor.vendor_code.ilike(f"%{search}%")
                )
            )

        return query.count()
```

### Step 2.3: Create Vendor Endpoints

**app/api/v1/endpoints/vendors.py**:
```python
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from app.core.database import get_db
from app.core.dependencies import get_current_user, require_role
from app.core.events import publish_event
from app.repositories.vendor_repository import VendorRepository
from app.schemas.vendor import (
    VendorCreate,
    VendorUpdate,
    VendorResponse,
    VendorListResponse
)
from app.models.vendor import Vendor, VendorStatus

router = APIRouter(prefix="/vendors", tags=["Vendors"])

@router.get("/", response_model=VendorListResponse)
async def list_vendors(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    status: Optional[VendorStatus] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """List all vendors with pagination and filtering"""
    repo = VendorRepository(db)

    skip = (page - 1) * page_size
    vendors = repo.get_all(skip=skip, limit=page_size, status=status, search=search)
    total = repo.count(status=status, search=search)

    return VendorListResponse(
        vendors=vendors,
        total=total,
        page=page,
        page_size=page_size
    )

@router.post("/", response_model=VendorResponse, status_code=status.HTTP_201_CREATED)
async def create_vendor(
    vendor_data: VendorCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_role("Admin"))
):
    """Create a new vendor (Admin only)"""
    repo = VendorRepository(db)

    # Check if vendor code already exists
    if repo.get_by_code(vendor_data.vendor_code):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Vendor with code '{vendor_data.vendor_code}' already exists"
        )

    # Create vendor
    vendor = Vendor(
        **vendor_data.model_dump(),
        created_by=current_user["id"],
        status=VendorStatus.ACTIVE
    )

    vendor = repo.create(vendor)

    # Publish event
    await publish_event("VendorCreated", {
        "vendor_id": vendor.id,
        "vendor_code": vendor.vendor_code,
        "vendor_name": vendor.vendor_name,
        "created_by": current_user["id"]
    })

    return vendor

@router.get("/{vendor_id}", response_model=VendorResponse)
async def get_vendor(
    vendor_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get vendor by ID"""
    repo = VendorRepository(db)
    vendor = repo.get_by_id(vendor_id)

    if not vendor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Vendor with ID {vendor_id} not found"
        )

    return vendor

@router.put("/{vendor_id}", response_model=VendorResponse)
async def update_vendor(
    vendor_id: int,
    vendor_data: VendorUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_role("Admin"))
):
    """Update vendor (Admin only)"""
    repo = VendorRepository(db)
    vendor = repo.get_by_id(vendor_id)

    if not vendor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Vendor with ID {vendor_id} not found"
        )

    # Update fields
    for field, value in vendor_data.model_dump(exclude_unset=True).items():
        setattr(vendor, field, value)

    vendor = repo.update(vendor)

    # Publish event
    await publish_event("VendorUpdated", {
        "vendor_id": vendor.id,
        "vendor_code": vendor.vendor_code,
        "updated_by": current_user["id"]
    })

    return vendor

@router.delete("/{vendor_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_vendor(
    vendor_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_role("Admin"))
):
    """Delete vendor (Admin only) - soft delete"""
    repo = VendorRepository(db)
    vendor = repo.get_by_id(vendor_id)

    if not vendor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Vendor with ID {vendor_id} not found"
        )

    repo.delete(vendor)

    # Publish event
    await publish_event("VendorDeleted", {
        "vendor_id": vendor.id,
        "vendor_code": vendor.vendor_code,
        "deleted_by": current_user["id"]
    })
```

---

## Phase 3-6: Remaining Modules

Follow the same pattern as Phase 2 for:
- **Phase 3**: Purchase Requests (with approval workflow service)
- **Phase 4**: Framework Contracts
- **Phase 5**: Quotations (with comparison service)
- **Phase 6**: Purchase Orders (with Asset Service integration)

For each phase:
1. Create models (already done in Step 1.1)
2. Create Pydantic schemas
3. Create repository
4. Create service layer (for business logic)
5. Create API endpoints
6. Write tests

---

## Phase 7: Main Application & Testing

### Create Main Application

**app/main.py**:
```python
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.v1.router import api_router

# Configure logging
logging.basicConfig(
    level=logging.INFO if not settings.DEBUG else logging.DEBUG,
    format="%(asctime)s - %(name)s:%(lineno) - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Procurement Management Service",
    description="API for managing procurement requests, vendors, quotations, and purchase orders",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(api_router, prefix=settings.API_PREFIX)

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "procurement-api",
        "version": "1.0.0",
    }

@app.get("/")
async def root():
    return {
        "message": "Procurement Management Service API",
        "docs": "/docs",
        "health": "/health",
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8004,
        reload=settings.DEBUG,
    )
```

### Create API Router

**app/api/v1/router.py**:
```python
from fastapi import APIRouter
from app.api.v1.endpoints import vendors, purchase_requests, framework_contracts, quotations, purchase_orders

api_router = APIRouter()

api_router.include_router(vendors.router)
api_router.include_router(purchase_requests.router)
api_router.include_router(framework_contracts.router)
api_router.include_router(quotations.router)
api_router.include_router(purchase_orders.router)
```

---

## Docker Compose Integration

Add to `docker-compose.yml`:

```yaml
services:
  procurement-api:
    build:
      context: ./services/procurement-api
      dockerfile: Dockerfile
    container_name: procurement-api
    ports:
      - "8004:8004"
    environment:
      - DATABASE_USER=admin
      - DATABASE_PASSWORD_FILE=/run/secrets/mysql_user_passwd
      - DATABASE_HOST=mysql
      - DATABASE_PORT=3306
      - DATABASE_NAME=procurement_db
      - MONGODB_HOST=mongodb
      - MONGODB_PORT=27017
      - MONGO_PASSWD_FILE=/run/secrets/mongo_passwd
      - MONGODB_DB_NAME=procurement_read_db
      - REDIS_HOST=redis
      - REDIS_PORT=6379
      - RABBITMQ_HOST=rabbitmq
      - RABBITMQ_PORT=5672
      - JWT_SECRET_KEY_FILE=/run/secrets/jwt_secret
      - DEBUG=true
    secrets:
      - mysql_user_passwd
      - mongo_passwd
      - jwt_secret
    depends_on:
      - mysql
      - mongodb
      - redis
      - rabbitmq
    volumes:
      - ./services/procurement-api:/app
    networks:
      - officework-network
```

---

## Testing

Create test files in `services/procurement-api/tests/`:

1. `test_vendors.py` - Vendor CRUD tests
2. `test_purchase_requests.py` - Purchase request workflow tests
3. `test_framework_contracts.py` - Contract management tests
4. `test_quotations.py` - Quotation comparison tests
5. `test_purchase_orders.py` - Purchase order tests

Run tests:
```bash
docker compose exec procurement-api pytest tests/ -v
```

---

## Deployment

1. Create database:
```sql
CREATE DATABASE procurement_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

2. Run migrations:
```bash
docker compose exec procurement-api alembic upgrade head
```

3. Start service:
```bash
docker compose up -d procurement-api
```

4. Verify:
```bash
curl http://localhost:8004/health
```

---

## Summary

This quick start guide provides:

✅ **Foundation** - All core files created
✅ **Phase 1** - Database models and migrations ready
✅ **Phase 2** - Complete vendor management example
✅ **Phases 3-6** - Pattern to follow for remaining modules
✅ **Phase 7** - Main application and testing setup
✅ **Docker** - Container configuration
✅ **Deployment** - Steps to deploy

**Next Steps**:
1. Follow this guide to complete Phases 3-6
2. Implement approval workflow service
3. Implement quotation comparison service
4. Add comprehensive testing
5. Deploy and integrate with other services

**Estimated Time**: 15 days with 1-2 developers

---

**Guide Version**: 1.0
**Created By**: Claude AI Assistant
**Date**: 2025-11-02
