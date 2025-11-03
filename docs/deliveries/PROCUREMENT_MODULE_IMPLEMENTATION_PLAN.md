# Procurement Module - Complete Implementation Plan

**Date**: 2025-11-02
**Module**: Procurement Management Service
**Status**: 📋 Planning Complete - Ready for Implementation
**Priority**: Sprint 4-5 (Weeks 6-8)

---

## Executive Summary

This document provides a complete implementation plan for the Procurement Management module, covering purchase requests, vendor management, quotations, framework contracts, and purchase orders with a multi-level approval workflow.

**Scope**:
- Purchase Request Management with 3-level approval workflow
- Vendor and Framework Contract Management
- Quotation Management and Comparison
- Purchase Order Creation and Tracking
- Integration with Asset Management Service
- Event-driven architecture using RabbitMQ
- CQRS pattern for read/write optimization

---

## Table of Contents

1. [Module Overview](#module-overview)
2. [Database Schema](#database-schema)
3. [API Endpoints Specification](#api-endpoints-specification)
4. [Business Logic & Workflows](#business-logic--workflows)
5. [Implementation Phases](#implementation-phases)
6. [File Structure](#file-structure)
7. [Key Features](#key-features)
8. [Integration Points](#integration-points)
9. [Testing Strategy](#testing-strategy)
10. [Deployment Checklist](#deployment-checklist)

---

## Module Overview

### Purpose

The Procurement module manages the entire procurement lifecycle from purchase request creation through approval, quotation comparison, and final purchase order execution.

### Key Entities

1. **Purchase Requests** - Employee requests for equipment/supplies
2. **Vendors** - Supplier information and management
3. **Framework Contracts** - Long-term agreements with vendors
4. **Quotations** - Price quotes from vendors
5. **Purchase Orders** - Final orders placed with vendors

### Approval Workflow

```
[Employee] → [Department Manager] → [HR Manager] → [Director] → [Procurement]
   Draft         Level 1 Approval      Level 2         Level 3      Execution
```

---

## Database Schema

### 1. Vendors Table

```sql
CREATE TABLE procurement_db.vendors (
    id SERIAL PRIMARY KEY,
    vendor_code VARCHAR(50) UNIQUE NOT NULL,
    vendor_name VARCHAR(255) NOT NULL,

    -- Contact Information
    contact_person VARCHAR(255),
    email VARCHAR(255),
    phone VARCHAR(50),
    address TEXT,

    -- Tax Information
    tax_code VARCHAR(50),

    -- Business Information
    business_registration VARCHAR(100),
    bank_account VARCHAR(100),
    bank_name VARCHAR(255),

    -- Rating & Status
    rating DECIMAL(3, 2),  -- 0.00 to 5.00
    status VARCHAR(20) NOT NULL DEFAULT 'ACTIVE' CHECK (status IN ('ACTIVE', 'INACTIVE', 'BLACKLISTED')),

    -- Metadata
    notes TEXT,
    created_by INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP,

    CONSTRAINT uk_vendor_code UNIQUE (vendor_code),
    CONSTRAINT uk_vendor_tax_code UNIQUE (tax_code)
);

CREATE INDEX idx_vendors_vendor_code ON procurement_db.vendors(vendor_code);
CREATE INDEX idx_vendors_status ON procurement_db.vendors(status);
CREATE INDEX idx_vendors_vendor_name ON procurement_db.vendors(vendor_name);
```

### 2. Purchase Requests Table

```sql
CREATE TABLE procurement_db.purchase_requests (
    id SERIAL PRIMARY KEY,
    request_code VARCHAR(50) UNIQUE NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT,

    -- Request Information
    requested_by INT NOT NULL,
    department_id INT NOT NULL,
    priority VARCHAR(20) NOT NULL CHECK (priority IN ('LOW', 'MEDIUM', 'HIGH', 'URGENT')),
    request_date DATE NOT NULL,
    expected_delivery_date DATE,

    -- Procurement Type
    procurement_type VARCHAR(50) NOT NULL CHECK (procurement_type IN ('FRAMEWORK_CONTRACT', 'ONE_TIME')),
    framework_contract_id INT,

    -- Estimated Total
    estimated_total DECIMAL(15, 2),

    -- Approval Status
    approval_status VARCHAR(50) NOT NULL DEFAULT 'DRAFT' CHECK (
        approval_status IN ('DRAFT', 'PENDING', 'LEVEL1_APPROVED', 'LEVEL2_APPROVED', 'APPROVED', 'REJECTED', 'CANCELLED')
    ),

    -- Level 1 Approval (Department Manager)
    level1_approved_by INT,
    level1_approved_at TIMESTAMP,
    level1_notes TEXT,

    -- Level 2 Approval (HR Manager)
    level2_approved_by INT,
    level2_approved_at TIMESTAMP,
    level2_notes TEXT,

    -- Level 3 Approval (Director)
    level3_approved_by INT,
    level3_approved_at TIMESTAMP,
    level3_notes TEXT,

    -- Rejection
    rejected_by INT,
    rejected_at TIMESTAMP,
    rejection_reason TEXT,

    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP,

    CONSTRAINT fk_purchase_requests_framework_contract
        FOREIGN KEY (framework_contract_id)
        REFERENCES procurement_db.framework_contracts(id)
);

CREATE INDEX idx_purchase_requests_request_code ON procurement_db.purchase_requests(request_code);
CREATE INDEX idx_purchase_requests_requested_by ON procurement_db.purchase_requests(requested_by);
CREATE INDEX idx_purchase_requests_department_id ON procurement_db.purchase_requests(department_id);
CREATE INDEX idx_purchase_requests_approval_status ON procurement_db.purchase_requests(approval_status);
CREATE INDEX idx_purchase_requests_request_date ON procurement_db.purchase_requests(request_date);
CREATE INDEX idx_purchase_requests_priority ON procurement_db.purchase_requests(priority);
```

### 3. Purchase Request Items Table

```sql
CREATE TABLE procurement_db.purchase_request_items (
    id SERIAL PRIMARY KEY,
    purchase_request_id INT NOT NULL,

    -- Product Information
    product_name VARCHAR(255) NOT NULL,
    product_description TEXT,
    specification TEXT,
    unit VARCHAR(50) NOT NULL,
    quantity INT NOT NULL,

    -- Estimated Pricing
    estimated_unit_price DECIMAL(15, 2),
    estimated_total DECIMAL(15, 2),

    -- Reason
    reason TEXT,

    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_purchase_request_items_request
        FOREIGN KEY (purchase_request_id)
        REFERENCES procurement_db.purchase_requests(id)
        ON DELETE CASCADE
);

CREATE INDEX idx_purchase_request_items_request_id ON procurement_db.purchase_request_items(purchase_request_id);
```

### 4. Framework Contracts Table

```sql
CREATE TABLE procurement_db.framework_contracts (
    id SERIAL PRIMARY KEY,
    contract_code VARCHAR(50) UNIQUE NOT NULL,
    contract_name VARCHAR(255) NOT NULL,
    vendor_id INT NOT NULL,

    -- Contract Information
    contract_value DECIMAL(15, 2) NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,

    -- Terms
    terms_and_conditions TEXT,
    payment_terms TEXT,
    delivery_terms TEXT,

    -- Attachments
    contract_file_url VARCHAR(500),

    -- Status
    status VARCHAR(20) NOT NULL DEFAULT 'ACTIVE' CHECK (status IN ('ACTIVE', 'EXPIRED', 'TERMINATED')),

    -- Metadata
    created_by INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_framework_contracts_vendor
        FOREIGN KEY (vendor_id)
        REFERENCES procurement_db.vendors(id)
);

CREATE INDEX idx_framework_contracts_contract_code ON procurement_db.framework_contracts(contract_code);
CREATE INDEX idx_framework_contracts_vendor_id ON procurement_db.framework_contracts(vendor_id);
CREATE INDEX idx_framework_contracts_status ON procurement_db.framework_contracts(status);
CREATE INDEX idx_framework_contracts_dates ON procurement_db.framework_contracts(start_date, end_date);
```

### 5. Quotations Table

```sql
CREATE TABLE procurement_db.quotations (
    id SERIAL PRIMARY KEY,
    quotation_code VARCHAR(50) UNIQUE NOT NULL,
    purchase_request_id INT NOT NULL,
    vendor_id INT NOT NULL,

    -- Quotation Information
    quotation_date DATE NOT NULL,
    valid_until DATE,
    total_amount DECIMAL(15, 2) NOT NULL,

    -- Attachments
    quotation_file_url VARCHAR(500),

    -- Notes
    notes TEXT,

    -- Status
    status VARCHAR(20) NOT NULL DEFAULT 'PENDING' CHECK (status IN ('PENDING', 'APPROVED', 'REJECTED')),

    -- Metadata
    created_by INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_quotations_purchase_request
        FOREIGN KEY (purchase_request_id)
        REFERENCES procurement_db.purchase_requests(id)
        ON DELETE CASCADE,
    CONSTRAINT fk_quotations_vendor
        FOREIGN KEY (vendor_id)
        REFERENCES procurement_db.vendors(id)
);

CREATE INDEX idx_quotations_quotation_code ON procurement_db.quotations(quotation_code);
CREATE INDEX idx_quotations_purchase_request_id ON procurement_db.quotations(purchase_request_id);
CREATE INDEX idx_quotations_vendor_id ON procurement_db.quotations(vendor_id);
CREATE INDEX idx_quotations_status ON procurement_db.quotations(status);
```

### 6. Quotation Items Table

```sql
CREATE TABLE procurement_db.quotation_items (
    id SERIAL PRIMARY KEY,
    quotation_id INT NOT NULL,
    purchase_request_item_id INT,

    -- Product Information
    product_name VARCHAR(255) NOT NULL,
    product_description TEXT,
    unit VARCHAR(50) NOT NULL,
    quantity INT NOT NULL,
    unit_price DECIMAL(15, 2) NOT NULL,
    total_price DECIMAL(15, 2) NOT NULL,

    -- Additional Information
    delivery_time VARCHAR(100),
    warranty_period VARCHAR(100),

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_quotation_items_quotation
        FOREIGN KEY (quotation_id)
        REFERENCES procurement_db.quotations(id)
        ON DELETE CASCADE,
    CONSTRAINT fk_quotation_items_request_item
        FOREIGN KEY (purchase_request_item_id)
        REFERENCES procurement_db.purchase_request_items(id)
        ON DELETE SET NULL
);

CREATE INDEX idx_quotation_items_quotation_id ON procurement_db.quotation_items(quotation_id);
CREATE INDEX idx_quotation_items_request_item_id ON procurement_db.quotation_items(purchase_request_item_id);
```

### 7. Purchase Orders Table

```sql
CREATE TABLE procurement_db.purchase_orders (
    id SERIAL PRIMARY KEY,
    order_code VARCHAR(50) UNIQUE NOT NULL,
    purchase_request_id INT NOT NULL,
    quotation_id INT NOT NULL,
    vendor_id INT NOT NULL,

    -- Order Information
    order_date DATE NOT NULL,
    expected_delivery_date DATE,
    actual_delivery_date DATE,

    -- Financial Information
    subtotal DECIMAL(15, 2) NOT NULL,
    tax_amount DECIMAL(15, 2) DEFAULT 0,
    discount_amount DECIMAL(15, 2) DEFAULT 0,
    total_amount DECIMAL(15, 2) NOT NULL,

    -- Delivery Information
    delivery_address TEXT,
    delivery_contact VARCHAR(255),
    delivery_phone VARCHAR(50),

    -- Payment Information
    payment_terms TEXT,
    payment_status VARCHAR(20) DEFAULT 'PENDING' CHECK (payment_status IN ('PENDING', 'PARTIAL', 'PAID')),

    -- Order Status
    status VARCHAR(20) NOT NULL DEFAULT 'PENDING' CHECK (
        status IN ('PENDING', 'CONFIRMED', 'PROCESSING', 'SHIPPED', 'DELIVERED', 'CANCELLED', 'COMPLETED')
    ),

    -- Notes
    notes TEXT,

    -- Metadata
    created_by INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_purchase_orders_purchase_request
        FOREIGN KEY (purchase_request_id)
        REFERENCES procurement_db.purchase_requests(id),
    CONSTRAINT fk_purchase_orders_quotation
        FOREIGN KEY (quotation_id)
        REFERENCES procurement_db.quotations(id),
    CONSTRAINT fk_purchase_orders_vendor
        FOREIGN KEY (vendor_id)
        REFERENCES procurement_db.vendors(id)
);

CREATE INDEX idx_purchase_orders_order_code ON procurement_db.purchase_orders(order_code);
CREATE INDEX idx_purchase_orders_purchase_request_id ON procurement_db.purchase_orders(purchase_request_id);
CREATE INDEX idx_purchase_orders_vendor_id ON procurement_db.purchase_orders(vendor_id);
CREATE INDEX idx_purchase_orders_status ON procurement_db.purchase_orders(status);
CREATE INDEX idx_purchase_orders_order_date ON procurement_db.purchase_orders(order_date);
```

### 8. Purchase Order Items Table

```sql
CREATE TABLE procurement_db.purchase_order_items (
    id SERIAL PRIMARY KEY,
    purchase_order_id INT NOT NULL,
    quotation_item_id INT,

    -- Product Information
    product_name VARCHAR(255) NOT NULL,
    product_description TEXT,
    unit VARCHAR(50) NOT NULL,
    quantity INT NOT NULL,
    unit_price DECIMAL(15, 2) NOT NULL,
    total_price DECIMAL(15, 2) NOT NULL,

    -- Received Quantity
    received_quantity INT DEFAULT 0,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_purchase_order_items_purchase_order
        FOREIGN KEY (purchase_order_id)
        REFERENCES procurement_db.purchase_orders(id)
        ON DELETE CASCADE,
    CONSTRAINT fk_purchase_order_items_quotation_item
        FOREIGN KEY (quotation_item_id)
        REFERENCES procurement_db.quotation_items(id)
        ON DELETE SET NULL
);

CREATE INDEX idx_purchase_order_items_purchase_order_id ON procurement_db.purchase_order_items(purchase_order_id);
```

---

## API Endpoints Specification

### Vendor Management

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/api/v1/vendors/` | List all vendors | Yes (Staff+) |
| POST | `/api/v1/vendors/` | Create new vendor | Yes (Admin+) |
| GET | `/api/v1/vendors/{id}` | Get vendor details | Yes (Staff+) |
| PUT | `/api/v1/vendors/{id}` | Update vendor | Yes (Admin+) |
| DELETE | `/api/v1/vendors/{id}` | Delete vendor | Yes (Admin) |
| GET | `/api/v1/vendors/{id}/contracts` | List vendor contracts | Yes (Staff+) |
| GET | `/api/v1/vendors/{id}/quotations` | List vendor quotations | Yes (Staff+) |

### Purchase Request Management

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/api/v1/purchase-requests/` | List purchase requests | Yes (Staff+) |
| POST | `/api/v1/purchase-requests/` | Create request | Yes (Staff+) |
| GET | `/api/v1/purchase-requests/{id}` | Get request details | Yes (Staff+) |
| PUT | `/api/v1/purchase-requests/{id}` | Update request (DRAFT only) | Yes (Creator) |
| DELETE | `/api/v1/purchase-requests/{id}` | Delete request | Yes (Creator/Admin) |
| POST | `/api/v1/purchase-requests/{id}/submit` | Submit for approval | Yes (Creator) |
| POST | `/api/v1/purchase-requests/{id}/approve-level1` | Level 1 approval | Yes (Dept Manager) |
| POST | `/api/v1/purchase-requests/{id}/approve-level2` | Level 2 approval | Yes (HR Manager) |
| POST | `/api/v1/purchase-requests/{id}/approve-level3` | Level 3 approval | Yes (Director) |
| POST | `/api/v1/purchase-requests/{id}/reject` | Reject request | Yes (Approver) |
| POST | `/api/v1/purchase-requests/{id}/cancel` | Cancel request | Yes (Creator/Admin) |
| GET | `/api/v1/purchase-requests/{id}/history` | Get approval history | Yes (Staff+) |

### Framework Contract Management

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/api/v1/framework-contracts/` | List contracts | Yes (Staff+) |
| POST | `/api/v1/framework-contracts/` | Create contract | Yes (Admin+) |
| GET | `/api/v1/framework-contracts/{id}` | Get contract details | Yes (Staff+) |
| PUT | `/api/v1/framework-contracts/{id}` | Update contract | Yes (Admin+) |
| DELETE | `/api/v1/framework-contracts/{id}` | Delete contract | Yes (Admin) |
| POST | `/api/v1/framework-contracts/{id}/terminate` | Terminate contract | Yes (Admin) |
| GET | `/api/v1/framework-contracts/active` | List active contracts | Yes (Staff+) |
| GET | `/api/v1/framework-contracts/expiring` | List expiring contracts | Yes (Admin+) |

### Quotation Management

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/api/v1/quotations/` | List quotations | Yes (Staff+) |
| POST | `/api/v1/quotations/` | Create quotation | Yes (Admin+) |
| GET | `/api/v1/quotations/{id}` | Get quotation details | Yes (Staff+) |
| PUT | `/api/v1/quotations/{id}` | Update quotation | Yes (Admin+) |
| DELETE | `/api/v1/quotations/{id}` | Delete quotation | Yes (Admin) |
| POST | `/api/v1/quotations/{id}/approve` | Approve quotation | Yes (Admin+) |
| POST | `/api/v1/quotations/{id}/reject` | Reject quotation | Yes (Admin+) |
| GET | `/api/v1/quotations/compare` | Compare quotations | Yes (Admin+) |

### Purchase Order Management

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/api/v1/purchase-orders/` | List purchase orders | Yes (Staff+) |
| POST | `/api/v1/purchase-orders/` | Create purchase order | Yes (Admin+) |
| GET | `/api/v1/purchase-orders/{id}` | Get order details | Yes (Staff+) |
| PUT | `/api/v1/purchase-orders/{id}` | Update order | Yes (Admin+) |
| DELETE | `/api/v1/purchase-orders/{id}` | Delete order | Yes (Admin) |
| POST | `/api/v1/purchase-orders/{id}/confirm` | Confirm order | Yes (Admin+) |
| POST | `/api/v1/purchase-orders/{id}/receive` | Mark as received | Yes (Admin+) |
| POST | `/api/v1/purchase-orders/{id}/cancel` | Cancel order | Yes (Admin) |
| GET | `/api/v1/purchase-orders/{id}/items` | Get order items | Yes (Staff+) |

---

## Business Logic & Workflows

### 1. Purchase Request Approval Workflow

```python
class ApprovalWorkflow:
    """
    Multi-level approval workflow for purchase requests

    States:
    - DRAFT: Created but not submitted
    - PENDING: Awaiting Level 1 approval
    - LEVEL1_APPROVED: Department Manager approved
    - LEVEL2_APPROVED: HR Manager approved
    - APPROVED: Director approved (final approval)
    - REJECTED: Rejected at any level
    - CANCELLED: Cancelled by creator or admin
    """

    def submit_request(self, request_id: int, user_id: int):
        """
        Submit draft request for approval
        - Change status: DRAFT → PENDING
        - Notify department manager
        - Publish event: PurchaseRequestSubmitted
        """
        pass

    def approve_level1(self, request_id: int, approver_id: int, notes: str):
        """
        Department Manager approval
        - Verify approver is department manager
        - Change status: PENDING → LEVEL1_APPROVED
        - Notify HR manager
        - Publish event: PurchaseRequestLevel1Approved
        """
        pass

    def approve_level2(self, request_id: int, approver_id: int, notes: str):
        """
        HR Manager approval
        - Verify approver is HR manager
        - Change status: LEVEL1_APPROVED → LEVEL2_APPROVED
        - Notify director
        - Publish event: PurchaseRequestLevel2Approved
        """
        pass

    def approve_level3(self, request_id: int, approver_id: int, notes: str):
        """
        Director approval (final)
        - Verify approver is director
        - Change status: LEVEL2_APPROVED → APPROVED
        - Notify procurement team
        - Publish event: PurchaseRequestApproved
        """
        pass

    def reject_request(self, request_id: int, rejector_id: int, reason: str):
        """
        Reject request at any level
        - Change status: * → REJECTED
        - Record rejection reason
        - Notify requester
        - Publish event: PurchaseRequestRejected
        """
        pass
```

### 2. Quotation Comparison Logic

```python
class QuotationComparison:
    """
    Compare quotations from multiple vendors
    """

    def compare_quotations(self, purchase_request_id: int):
        """
        Compare all quotations for a purchase request

        Returns:
        - List of quotations sorted by total_amount
        - Comparison table with price breakdown
        - Recommended vendor (lowest price or best value)
        """
        pass

    def calculate_best_value(self, quotations: List[Quotation]):
        """
        Calculate best value based on:
        - Price
        - Delivery time
        - Warranty period
        - Vendor rating
        """
        pass
```

### 3. Purchase Order Creation

```python
class PurchaseOrderService:
    """
    Create and manage purchase orders
    """

    def create_from_quotation(self, quotation_id: int, user_id: int):
        """
        Create purchase order from approved quotation
        - Verify quotation is approved
        - Verify purchase request is fully approved
        - Copy items from quotation
        - Calculate totals (subtotal, tax, discount)
        - Assign order code (PO-YYYYMMDD-XXXX)
        - Publish event: PurchaseOrderCreated
        """
        pass

    def confirm_order(self, order_id: int):
        """
        Confirm purchase order
        - Change status: PENDING → CONFIRMED
        - Send to vendor (email/API)
        - Publish event: PurchaseOrderConfirmed
        """
        pass

    def mark_as_received(self, order_id: int, items_received: Dict[int, int]):
        """
        Mark items as received
        - Update received_quantity for each item
        - If all items received: status → DELIVERED
        - Create assets in Asset Service
        - Publish event: PurchaseOrderReceived
        """
        pass
```

---

## Implementation Phases

### Phase 1: Foundation (Week 6, Day 1-2)

**Objective**: Set up basic infrastructure

**Tasks**:
- ✅ Create directory structure
- ✅ Configure database connection
- ⏸️ Create all database models
- ⏸️ Create Alembic migrations
- ⏸️ Set up Docker configuration
- ⏸️ Configure RabbitMQ event publishing

**Deliverables**:
- Database schema created
- Models defined
- Migrations ready
- Service containerized

### Phase 2: Vendor Management (Week 6, Day 3-4)

**Objective**: Implement vendor CRUD operations

**Tasks**:
- Implement Vendor model and repository
- Create vendor Pydantic schemas
- Implement vendor API endpoints
- Add vendor search and filtering
- Implement vendor rating system

**Deliverables**:
- 7 vendor endpoints functional
- Vendor CRUD operations working
- Basic integration tests

### Phase 3: Purchase Requests (Week 6, Day 5 - Week 7, Day 2)

**Objective**: Implement purchase request lifecycle

**Tasks**:
- Implement PurchaseRequest and PurchaseRequestItem models
- Create request schemas
- Implement request repository
- Implement approval workflow service
- Create request API endpoints
- Add email notifications for approvals

**Deliverables**:
- 11 purchase request endpoints
- Multi-level approval workflow
- Notification system

### Phase 4: Framework Contracts (Week 7, Day 3)

**Objective**: Contract management

**Tasks**:
- Implement FrameworkContract model
- Create contract schemas
- Implement contract repository
- Create contract API endpoints
- Add contract expiration checks

**Deliverables**:
- 8 contract endpoints
- Contract status management
- Expiration alerts

### Phase 5: Quotations (Week 7, Day 4-5)

**Objective**: Quotation management and comparison

**Tasks**:
- Implement Quotation and QuotationItem models
- Create quotation schemas
- Implement quotation repository
- Create quotation API endpoints
- Implement quotation comparison logic

**Deliverables**:
- 8 quotation endpoints
- Quotation comparison feature
- Price analysis

### Phase 6: Purchase Orders (Week 8, Day 1-3)

**Objective**: Purchase order creation and tracking

**Tasks**:
- Implement PurchaseOrder and PurchaseOrderItem models
- Create order schemas
- Implement order repository
- Create order API endpoints
- Implement order confirmation workflow
- Add integration with Asset Service

**Deliverables**:
- 9 purchase order endpoints
- Order tracking
- Asset creation integration

### Phase 7: Testing & Documentation (Week 8, Day 4-5)

**Objective**: Comprehensive testing and documentation

**Tasks**:
- Write integration tests for all endpoints
- Test approval workflows
- Test quotation comparison
- Test order creation
- Create API documentation
- Create user guide

**Deliverables**:
- 100+ integration tests
- Complete API documentation
- User guide
- Deployment guide

---

## File Structure

```
services/procurement-api/
├── app/
│   ├── __init__.py
│   ├── main.py                          # FastAPI application
│   ├── api/
│   │   ├── __init__.py
│   │   └── v1/
│   │       ├── __init__.py
│   │       ├── router.py                # Main API router
│   │       └── endpoints/
│   │           ├── __init__.py
│   │           ├── vendors.py           # Vendor endpoints
│   │           ├── purchase_requests.py # Purchase request endpoints
│   │           ├── framework_contracts.py
│   │           ├── quotations.py
│   │           └── purchase_orders.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py                    # ✅ Configuration
│   │   ├── database.py                  # ✅ Database connection
│   │   ├── dependencies.py              # Authentication dependencies
│   │   └── events.py                    # Event publishing
│   ├── models/
│   │   ├── __init__.py
│   │   ├── base.py                      # Base model
│   │   ├── vendor.py                    # Vendor model
│   │   ├── purchase_request.py          # Purchase request models
│   │   ├── framework_contract.py
│   │   ├── quotation.py
│   │   └── purchase_order.py
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── vendor.py                    # Vendor schemas
│   │   ├── purchase_request.py          # Purchase request schemas
│   │   ├── framework_contract.py
│   │   ├── quotation.py
│   │   └── purchase_order.py
│   ├── repositories/
│   │   ├── __init__.py
│   │   ├── vendor_repository.py
│   │   ├── purchase_request_repository.py
│   │   ├── framework_contract_repository.py
│   │   ├── quotation_repository.py
│   │   └── purchase_order_repository.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── approval_service.py          # Approval workflow
│   │   ├── quotation_service.py         # Quotation comparison
│   │   ├── purchase_order_service.py    # Order management
│   │   └── notification_service.py      # Email notifications
│   └── utils/
│       ├── __init__.py
│       ├── code_generator.py            # Generate codes (PR-XXX, PO-XXX)
│       └── validators.py                # Custom validators
├── alembic/
│   ├── versions/                        # Migration files
│   ├── env.py
│   └── script.py.mako
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_vendors.py
│   ├── test_purchase_requests.py
│   ├── test_framework_contracts.py
│   ├── test_quotations.py
│   └── test_purchase_orders.py
├── Dockerfile
├── requirements.txt
├── requirements-test.txt
├── pytest.ini
├── alembic.ini
└── README.md
```

---

## Key Features

### 1. Multi-Level Approval Workflow

- **3-level approval** chain
- **Email notifications** at each level
- **Rejection** capability at any level
- **Approval history** tracking
- **Parallel approval** paths (for different request types)

### 2. Vendor Management

- **Vendor profiles** with contact info
- **Vendor rating** system (0-5 stars)
- **Vendor status** (Active/Inactive/Blacklisted)
- **Framework contracts** per vendor
- **Performance tracking**

### 3. Quotation Comparison

- **Side-by-side comparison** of quotations
- **Price breakdown** per item
- **Best value calculation** (not just lowest price)
- **Recommendation engine** based on:
  - Price
  - Delivery time
  - Warranty
  - Vendor rating

### 4. Purchase Order Tracking

- **Order status** progression
- **Delivery tracking**
- **Partial receipt** support
- **Payment status** tracking
- **Integration with Asset Service** (auto-create assets on receipt)

### 5. CQRS Pattern

- **Write operations**: MySQL
- **Read operations**: MongoDB (for fast queries)
- **Event-driven sync**: RabbitMQ
- **Read model** optimized for:
  - Dashboard statistics
  - Approval queues
  - Vendor comparisons

---

## Integration Points

### 1. Auth Service Integration

```python
# Authentication
- Verify user JWT tokens
- Check user roles (Staff, Manager, Admin, Director)
- Department assignment validation
- Approval authority checks
```

### 2. Asset Service Integration

```python
# Asset Creation
- Create assets from received purchase orders
- Link assets to purchase order items
- Copy warranty information
- Set initial asset status (NEW)
```

### 3. Notification Service Integration

```python
# Email Notifications
- Purchase request submitted
- Approval required (at each level)
- Approval granted/rejected
- Order confirmed
- Order delivered
```

### 4. Event Publishing

```python
# RabbitMQ Events
- PurchaseRequestCreated
- PurchaseRequestSubmitted
- PurchaseRequestApproved
- PurchaseRequestRejected
- QuotationCreated
- QuotationApproved
- PurchaseOrderCreated
- PurchaseOrderConfirmed
- PurchaseOrderDelivered
```

---

## Testing Strategy

### Unit Tests

```python
# Test coverage for:
- Repository methods
- Service business logic
- Approval workflow state transitions
- Quotation comparison algorithms
- Code generation utilities
```

### Integration Tests

```python
# Test coverage for:
- All API endpoints (GET, POST, PUT, DELETE)
- Approval workflow end-to-end
- Quotation creation and comparison
- Purchase order lifecycle
- File upload/download
- Event publishing
```

### E2E Tests

```python
# Complete workflows:
1. Create purchase request → Submit → Approve (3 levels) → Create quotations → Compare → Create PO
2. Vendor registration → Create framework contract → Use in purchase request
3. Purchase order creation → Confirmation → Delivery → Asset creation
```

---

## Deployment Checklist

### Pre-Deployment

- [ ] All database migrations created and tested
- [ ] All API endpoints documented in OpenAPI
- [ ] Integration tests passing (100% coverage)
- [ ] Docker image built and tagged
- [ ] Environment variables configured
- [ ] RabbitMQ queues created
- [ ] MongoDB read models initialized

### Deployment Steps

1. [ ] Create `procurement_db` database in MySQL
2. [ ] Create `procurement_read_db` database in MongoDB
3. [ ] Run Alembic migrations
4. [ ] Start procurement-api service
5. [ ] Verify health endpoint
6. [ ] Test sample purchase request workflow
7. [ ] Configure nginx routes
8. [ ] Update API gateway configuration

### Post-Deployment

- [ ] Monitor logs for errors
- [ ] Verify event publishing to RabbitMQ
- [ ] Test approval email notifications
- [ ] Verify integration with Auth Service
- [ ] Verify integration with Asset Service
- [ ] Load test approval workflow
- [ ] Create seed data (vendors, sample contracts)

---

## Dependencies

### Python Packages

```txt
# Core
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

# Testing
pytest==7.4.3
pytest-asyncio==0.21.1
pytest-cov==4.1.0
httpx==0.25.2
```

---

## Estimated Effort

| Phase | Tasks | Estimated Time | Priority |
|-------|-------|----------------|----------|
| Phase 1: Foundation | 6 tasks | 2 days | High |
| Phase 2: Vendors | 5 tasks | 2 days | High |
| Phase 3: Purchase Requests | 6 tasks | 3 days | Critical |
| Phase 4: Contracts | 5 tasks | 1 day | Medium |
| Phase 5: Quotations | 5 tasks | 2 days | High |
| Phase 6: Purchase Orders | 6 tasks | 3 days | Critical |
| Phase 7: Testing & Docs | 7 tasks | 2 days | High |
| **TOTAL** | **40 tasks** | **15 days** | - |

**Team Size**: 1-2 developers
**Timeline**: Sprint 4-5 (3 weeks with buffer)

---

## Success Criteria

### Functional Requirements

- ✅ All 43 API endpoints implemented and tested
- ✅ Multi-level approval workflow functioning correctly
- ✅ Quotation comparison providing accurate recommendations
- ✅ Purchase orders creating assets automatically
- ✅ Email notifications sent at all workflow steps

### Non-Functional Requirements

- ✅ Response time < 200ms for list endpoints
- ✅ Response time < 100ms for single entity endpoints
- ✅ Support 100+ concurrent approval requests
- ✅ 99.9% uptime during business hours
- ✅ All data encrypted in transit and at rest

### Quality Metrics

- ✅ Code coverage > 80%
- ✅ All critical paths tested
- ✅ Zero high-severity security vulnerabilities
- ✅ API documentation complete and accurate
- ✅ User acceptance testing passed

---

## Next Steps

1. **Review and approve** this implementation plan
2. **Assign resources** (developers, testers)
3. **Set up project tracking** (Jira/GitHub issues)
4. **Create development environment**
5. **Begin Phase 1**: Foundation implementation
6. **Weekly progress reviews** during Sprint 4-5

---

**Document Version**: 1.0
**Prepared By**: Claude AI Assistant
**Date**: 2025-11-02
**Status**: Ready for Implementation

---

## References

- [Business Requirements](../02.%20Business_Requirements.md#34-quy-trình-mua-sắm-và-cấp-phát)
- [Database Design](../04.%20Database_Design.md#4-procurement-service-schema-procurement_db)
- [API Specification](../05.%20API_Specification.md) (to be created)
- [Implementation Plan](../07.%20Implementation_Plan.md)
