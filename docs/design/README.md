# 🏗️ DESIGN - THIẾT KẾ HỆ THỐNG

## Giới thiệu

Thư mục này chứa tất cả tài liệu liên quan đến **thiết kế kiến trúc hệ thống, database và API** của dự án Quản lý Trang thiết bị Văn phòng.

---

## 📚 Danh sách Tài liệu

### 1. [System Architecture](01_System_Architecture.md) ✅
**Mô tả**: Kiến trúc tổng thể của hệ thống - Microservices Architecture

**Nội dung chính**:
- **Kiến trúc Microservices**: 6 services (Auth, Asset, Procurement, Maintenance, Report, Notification)
- **Technology Stack**:
  - Backend: FastAPI (Python 3.11), SQLAlchemy
  - Database: PostgreSQL 14+
  - Cache: Redis 7
  - Message Queue: RabbitMQ 3.12
  - Frontend: React.js / Vue.js
- **Service Communication**: REST API + RabbitMQ events
- **Authentication**: JWT + MFA/OTP (pyotp) + Active Directory (ldap3)
- **Deployment**: Docker Compose, Nginx as API Gateway
- **Security Design**: Encryption, RBAC, Audit logging

**Sơ đồ kiến trúc**:
```
API Gateway (Nginx) → 6 Microservices → PostgreSQL/Redis/RabbitMQ
```

**Đối tượng đọc**: Tech Lead, Solution Architect, Senior Developers

---

### 2. [Database Design](02_Database_Design.md) ✅
**Mô tả**: Thiết kế database chi tiết với 6 schemas, 28+ tables

**Nội dung chính**:

#### Database Schemas:
1. **auth_db** (9 tables):
   - users, roles, permissions, role_permissions
   - departments, mfa_backup_codes
   - refresh_tokens, password_reset_tokens
   - audit_logs

2. **asset_db** (5 tables):
   - assets, asset_categories
   - asset_assignments, asset_attachments
   - asset_depreciation_records

3. **procurement_db** (7 tables):
   - purchase_requests, purchase_request_items
   - framework_contracts, vendors
   - quotations, quotation_items
   - purchase_orders

4. **maintenance_db** (3 tables):
   - maintenance_requests
   - maintenance_schedules
   - maintenance_history

5. **notification_db** (2 tables):
   - notifications, email_queue

6. **report_db** (2 tables):
   - report_templates, report_history

**Features**:
- Full indexing strategy
- Foreign key relationships
- Row-Level Security (RLS)
- Database roles & permissions
- Backup & retention policies

**Đối tượng đọc**: Database Architect, Backend Developers

---

### 3. [API Specification](03_API_Specification.md) ✅
**Mô tả**: Đặc tả API đầy đủ cho 6 microservices

**Nội dung chính**:

#### API Endpoints Summary:
- **Auth Service** (~15 endpoints):
  - Authentication: login, verify-otp, logout
  - MFA: setup, enable, disable, verify-backup-code
  - User Management: CRUD users
  - Role & Permission management
  - Active Directory sync

- **Asset Service** (~20 endpoints):
  - Asset CRUD
  - Categories management
  - Assignment & Return
  - Depreciation calculation
  - QR code generation

- **Procurement Service** (~25 endpoints):
  - Purchase Request CRUD
  - 3-level approval workflow
  - Quotation management
  - Purchase Order CRUD
  - Vendor management
  - Contract management

- **Maintenance Service** (~15 endpoints):
  - Maintenance Request CRUD
  - Assignment to technicians
  - Schedule management
  - History tracking

- **Report Service** (~10 endpoints):
  - Report generation
  - Export PDF/Excel
  - Dashboard data

- **Notification Service** (~8 endpoints):
  - In-app notifications
  - Email queue management

**Format mỗi API**:
```
#### POST /api/v1/[service]/[endpoint]
**Description**
**Request Body**
**Response (200)**
**Errors**
```

**Đối tượng đọc**: Backend Developers, Frontend Developers, QA

---

## 🔗 Tài liệu Liên quan

### Upstream (đầu vào)
- [Business Requirements](../requirements/02_Business_Requirements.md)
- [User Stories](../requirements/03_User_Stories.md)

### Downstream (đầu ra)
- [DEV_README](../development/DEV_README.md) - Implementation từ design
- [Implementation Plan](../development/Implementation_Plan.md) - Development roadmap

---

## 📊 Trạng thái

| Tài liệu | Version | Last Updated | Status |
|----------|---------|--------------|--------|
| System Architecture | 1.0 | 2025-10-18 | ✅ Complete |
| Database Design | 1.0 | 2025-10-17 | ✅ Complete |
| API Specification | 1.0 | 2025-10-17 | ✅ Complete |

**Progress**: 3/3 documents (100%)

---

## 🎨 Design Principles

### 1. Microservices Architecture
- **Single Responsibility**: Mỗi service chịu trách nhiệm một domain
- **Loose Coupling**: Services giao tiếp qua REST API + Events
- **Independent Deployment**: Mỗi service deploy độc lập
- **Database per Service**: Mỗi service có schema riêng

### 2. API Design
- **RESTful**: Tuân thủ REST principles
- **Consistent**: URL naming, response format nhất quán
- **Versioned**: /api/v1, /api/v2 cho backward compatibility
- **Well-documented**: OpenAPI/Swagger specification

### 3. Database Design
- **Normalization**: 3NF cho data integrity
- **Indexing**: Index cho performance
- **Constraints**: Foreign keys, checks, unique constraints
- **Auditing**: Created_at, updated_at, deleted_at (soft delete)

### 4. Security by Design
- **Defense in Depth**: Multiple security layers
- **Least Privilege**: Minimum permissions required
- **Encryption**: Data at rest & in transit
- **Audit Logging**: Track all critical actions

---

## 🔄 Design Review Process

### 1. Architecture Review
- **Frequency**: Before Sprint 1, Major milestones
- **Participants**: Tech Lead, Senior Devs, Architects
- **Output**: Architecture Decision Records (ADR)

### 2. Database Review
- **Frequency**: Before implementation
- **Participants**: Database Architect, Backend Devs
- **Output**: Approved schema migrations

### 3. API Review
- **Frequency**: Per service before implementation
- **Participants**: Backend Lead, Frontend Lead
- **Output**: API contract, Swagger documentation

---

## 📐 Design Tools

### Diagramming
- **Architecture Diagrams**: Draw.io, Lucidchart
- **Database ERD**: dbdiagram.io, MySQL Workbench
- **Sequence Diagrams**: PlantUML, Mermaid

### Documentation
- **API Docs**: Swagger/OpenAPI
- **Database Docs**: Database markdown files
- **Confluence**: Design decisions, ADRs

---

## 🚨 Common Design Patterns

### Backend Patterns
- **Repository Pattern**: Data access abstraction
- **Unit of Work**: Transaction management
- **Dependency Injection**: Loose coupling
- **Factory Pattern**: Object creation
- **Observer Pattern**: Event-driven (RabbitMQ)

### API Patterns
- **Circuit Breaker**: Service resilience
- **Rate Limiting**: API protection
- **Pagination**: Large dataset handling
- **HATEOAS**: Hypermedia links (optional)

---

## 👥 Liên hệ

- **Tech Lead**: tech.lead@assetmanagement.com
- **Solution Architect**: architect@assetmanagement.com
- **Questions**: [Create Issue](https://github.com/your-org/asset-management/issues)

---

[⬅️ Back to Requirements](../requirements/README.md) | [⬅️ Back to Index](../INDEX.md) | [➡️ Next: Development](../development/README.md)
