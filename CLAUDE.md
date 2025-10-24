# CLAUDE.md - AI Assistant Guide

> **Mục đích**: Tài liệu này cung cấp toàn bộ thông tin cần thiết để Claude AI (hoặc bất kỳ AI assistant nào) có thể hiểu nhanh và làm việc hiệu quả với dự án này.

**Cập nhật lần cuối**: 2025-10-21
**Phiên bản**: 1.0
**Dự án**: Office Equipment Asset Management System (officework)

---

## 📚 MỤC LỤC

1. [Tổng quan dự án](#1-tổng-quan-dự-án)
2. [Kiến trúc hệ thống](#2-kiến-trúc-hệ-thống)
3. [Tech stack](#3-tech-stack)
4. [Cấu trúc thư mục](#4-cấu-trúc-thư-mục)
5. [Database schema](#5-database-schema)
6. [API endpoints](#6-api-endpoints)
7. [Code style & conventions](#7-code-style--conventions)
8. [Design patterns](#8-design-patterns)
9. [Trạng thái hiện tại](#9-trạng-thái-hiện-tại)
10. [Workflow làm việc](#10-workflow-làm-việc)
11. [Common tasks](#11-common-tasks)
12. [Troubleshooting](#12-troubleshooting)

---

## 1. TỔNG QUAN DỰ ÁN

### 1.1. Mục đích
Hệ thống quản lý trang thiết bị văn phòng toàn diện, số hóa quy trình từ đề xuất mua sắm → phê duyệt → mua hàng → cấp phát → bảo trì → thanh lý.

### 1.2. Đối tượng sử dụng
- **Admin**: Quản trị hệ thống, cấu hình
- **Ban Giám đốc**: Phê duyệt cấp 3
- **Trưởng phòng HCNS**: Phê duyệt cấp 2, quản lý nhân sự
- **Trưởng phòng**: Phê duyệt cấp 1
- **Quản lý thiết bị**: Quản lý tài sản, cấp phát, thu hồi
- **Kỹ thuật viên**: Xử lý bảo trì, sửa chữa
- **Nhân viên**: Đề xuất mua sắm, yêu cầu bảo trì

### 1.3. Tính năng chính
1. **Authentication & Authorization** ✅ (Hoàn thành)
   - Đăng nhập 2 bước (email/password → OTP)
   - MFA/TOTP với Google Authenticator
   - Tích hợp Active Directory (chuẩn bị sẵn)
   - Role-based access control (RBAC)
   - Password reset flow
   - Audit logging

2. **Asset Management** 🚧 (40% - Đang triển khai)
   - CRUD tài sản với phân loại
   - Cấp phát & thu hồi
   - Tính khấu hao tự động
   - QR code generation
   - File đính kèm (hóa đơn, bảo hành)
   - Lịch sử cấp phát/thu hồi

3. **Procurement** ⏸️ (Chưa bắt đầu)
   - Đề xuất mua sắm
   - Phê duyệt 3 cấp
   - Quản lý nhà cung cấp & hợp đồng khung
   - Thu thập & so sánh báo giá
   - Purchase Order & theo dõi giao hàng

4. **Maintenance** ⏸️ (Chưa bắt đầu)
   - Yêu cầu bảo trì (preventive, corrective, emergency)
   - Phân công kỹ thuật viên
   - Lịch bảo trì định kỳ
   - Theo dõi chi phí & linh kiện

5. **Reporting** ⏸️ (Chưa bắt đầu)
   - Báo cáo tài sản, khấu hao
   - Báo cáo mua sắm, bảo trì
   - Export PDF/Excel
   - Dashboard với biểu đồ

6. **Notification** ⏸️ (Chưa bắt đầu)
   - In-app notifications
   - Email notifications
   - Notification center

### 1.4. Timeline
- **Tổng thời gian**: 16 tuần (4 tháng)
- **Phương pháp**: Agile/Scrum, Sprint 2 tuần
- **Tiến độ hiện tại**: Sprint 2-3 (~15-20% hoàn thành)

---

## 2. KIẾN TRÚC HỆ THỐNG

### 2.1. Architectural Style
**Microservices + CQRS + Event-Driven**

```
┌─────────────────────────────────────────────┐
│           CLIENT (Browser)                  │
└────────────────┬────────────────────────────┘
                 │ HTTPS
                 ↓
┌─────────────────────────────────────────────┐
│      API GATEWAY (Nginx) - Port 80/443      │
│      Route: /api/v1/{service}/*             │
└────────────────┬────────────────────────────┘
                 │
        ┌────────┼────────┐
        ↓        ↓        ↓
   ┌────────┐ ┌────────┐ ┌────────┐
   │ Auth   │ │ Asset  │ │Procure │
   │ :8088  │ │ :8089  │ │ :TBD   │
   └───┬────┘ └───┬────┘ └───┬────┘
       │          │          │
       └──────────┼──────────┘
                  ↓
   ┌──────────────────────────────────┐
   │    SHARED INFRASTRUCTURE         │
   │  ┌─────────┐  ┌─────────────┐    │
   │  │  MySQL  │  │  MongoDB    │    │
   │  │  :3306  │  │  :27017     │    │
   │  │ (Write) │  │  (Read)     │    │
   │  └─────────┘  └─────────────┘    │
   │  ┌─────────┐  ┌─────────────┐    │
   │  │  Redis  │  │  RabbitMQ   │    │
   │  │  :6379  │  │  :5672      │    │
   │  └─────────┘  └─────────────┘    │
   └──────────────────────────────────┘
```

### 2.2. Microservices List

| Service | Port | Status | Description |
|---------|------|--------|-------------|
| **auth-api** | 8088 | ✅ Running | Authentication, user management, roles |
| **auth-fe** | 3000 | ✅ Running | Auth frontend (Jinja2 templates) |
| **asset-api** | 8089 | ✅ Running | Asset management APIs |
| **asset-fe** | 3001 | ✅ Running | Asset frontend |
| procurement-api | TBD | ⏸️ Pending | Procurement workflows |
| maintenance-api | TBD | ⏸️ Pending | Maintenance management |
| report-api | TBD | ⏸️ Pending | Report generation |
| notification-api | TBD | ⏸️ Pending | Notifications |

### 2.3. CQRS Pattern

**Write Side (Commands)** → MySQL
- Create, Update, Delete operations
- Strong consistency
- Transaction support
- Uses SQLAlchemy ORM

**Read Side (Queries)** → MongoDB
- Fast queries on denormalized data
- Eventually consistent
- Updated via RabbitMQ events
- Uses Motor (async MongoDB driver)

**Event Flow**:
```
User Action → Write to MySQL → Publish Event to RabbitMQ
→ Consumer updates MongoDB → Fast reads from MongoDB
```

### 2.4. Database Architecture

**MySQL 8.0** (Write Database):
- `auth_db` - Auth service schema
- `asset_db` - Asset service schema
- `procurement_db` - Procurement schema
- `maintenance_db` - Maintenance schema
- `notification_db` - Notification schema

**MongoDB 7** (Read Database):
- Denormalized collections per service
- Optimized for queries
- Updated via events

**Redis 7** (Cache & Session):
- User sessions
- Temporary tokens
- API rate limiting
- Frequently accessed data

**RabbitMQ 3.12** (Message Queue):
- CQRS event publishing
- Inter-service communication
- Background jobs

---

## 3. TECH STACK

### 3.1. Backend
- **Framework**: FastAPI 0.104.1
- **Language**: Python 3.11+
- **ASGI Server**: Uvicorn 0.24.0
- **ORM**: SQLAlchemy 2.0.23 (MySQL: PyMySQL 1.1.0)
- **Migrations**: Alembic 1.12.1
- **MongoDB Driver**: Motor 3.3.2 (async), PyMongo 4.6.1
- **Cache**: Redis 5.0.1
- **Message Queue**: aio-pika 9.3.1 (RabbitMQ client)

### 3.2. Security & Auth
- **JWT**: python-jose 3.3.0
- **Password Hashing**: passlib 1.7.4 + bcrypt 4.1.0
- **MFA/TOTP**: pyotp 2.9.0
- **QR Code**: qrcode 7.4.2
- **Active Directory**: ldap3 2.9.1
- **Encryption**: cryptography 41.0.7

### 3.3. Frontend
- **Framework**: FastAPI (Python-based server-side rendering)
- **Template Engine**: Jinja2 3.1.2
- **Styling**: Bootstrap CSS (via static files)
- **JavaScript**: Vanilla JS + Fetch API

### 3.4. DevOps
- **Containerization**: Docker + Docker Compose
- **API Gateway**: Nginx (Alpine)
- **CI/CD**: GitHub Actions (planned)
- **Monitoring**: Prometheus + Grafana (planned)

### 3.5. Development Tools
- **Testing**: pytest 7.4.3, pytest-asyncio, pytest-cov, faker
- **Formatting**: Black 23.11.0
- **Linting**: Flake8 6.1.0
- **Type Checking**: mypy 1.7.1

---

## 4. CẤU TRÚC THƯ MỤC

```
officework/
├── .claude/                  # Claude Code config
├── .secrets/                 # Docker secrets (NOT in git)
│   ├── jwt_secret_key.txt
│   ├── mongo_passwd.txt
│   └── mysql_passwd.txt
├── docs/                     # Comprehensive documentation
│   ├── 01. Project_Overview.md
│   ├── 02. Business_Requirements.md
│   ├── 03. System_Architecture.md
│   ├── 04. Database_Design.md
│   ├── 05. API_Specification.md
│   ├── 06. User_Stories.md
│   └── 07. Implementation_Plan.md
├── nginx/                    # Nginx config (API Gateway)
│   └── nginx.conf
├── scripts/                  # Utility scripts
│   ├── init-mysql.sh        # MySQL initialization
│   └── .init.sql            # Database schemas
├── services/                 # Microservices
│   ├── auth-api/            # ✅ Auth Backend
│   │   ├── app/
│   │   │   ├── api/v1/endpoints/   # API routes
│   │   │   ├── core/               # Config, DB, dependencies
│   │   │   ├── models/             # SQLAlchemy models
│   │   │   ├── schemas/            # Pydantic schemas
│   │   │   ├── repositories/       # Data access layer
│   │   │   ├── services/           # Business logic
│   │   │   └── main.py             # App entry point
│   │   ├── Dockerfile
│   │   └── requirements.txt
│   ├── auth-frontend/       # ✅ Auth Frontend (Jinja2)
│   │   ├── app/
│   │   │   ├── templates/          # Jinja2 templates
│   │   │   ├── static/             # CSS, JS, images
│   │   │   ├── routers/            # Route handlers
│   │   │   └── main.py
│   │   ├── Dockerfile
│   │   └── requirements.txt
│   ├── asset-api/           # 🚧 Asset Backend (in progress)
│   ├── asset-frontend/      # 🚧 Asset Frontend (in progress)
│   └── ...                  # Other services (pending)
├── tests/                    # Test scripts
├── .env                      # Environment variables
├── .gitignore
├── docker-compose.yml        # ✅ Orchestration config
├── README.md                 # Project README
├── CLAUDE.md                 # This file (AI Assistant Guide)
├── FIX_OTP_GUIDE.md         # OTP troubleshooting guide
└── SPRINT_1_2_VERIFICATION_REPORT.md  # Verification report
```

### 4.1. Service Structure Pattern
Mỗi microservice (backend) tuân theo cấu trúc:

```
service-api/
├── app/
│   ├── api/
│   │   └── v1/
│   │       ├── endpoints/      # Route handlers
│   │       │   ├── auth.py
│   │       │   └── users.py
│   │       └── router.py       # Router aggregation
│   ├── core/
│   │   ├── config.py           # Settings (Pydantic)
│   │   ├── database.py         # DB session factory
│   │   ├── security.py         # Auth utilities
│   │   └── dependencies.py     # FastAPI dependencies
│   ├── models/                 # SQLAlchemy models (Write DB)
│   │   ├── base.py
│   │   ├── user.py
│   │   └── role.py
│   ├── schemas/                # Pydantic schemas
│   │   ├── user.py
│   │   └── auth.py
│   ├── repositories/           # Data access layer
│   │   ├── user_repository.py  # Write repository (MySQL)
│   │   └── user_read_repo.py   # Read repository (MongoDB)
│   ├── services/               # Business logic
│   │   └── auth_service.py
│   └── main.py                 # FastAPI app
├── Dockerfile
├── requirements.txt
└── alembic/                    # Database migrations
    └── versions/
```

---

## 5. DATABASE SCHEMA

### 5.1. Auth Service (auth_db)

**Table: users**
```sql
CREATE TABLE auth_db.users (
    id INT PRIMARY KEY AUTO_INCREMENT,
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(100) UNIQUE,
    full_name VARCHAR(255) NOT NULL,
    hashed_password VARCHAR(255),  -- NULL for AD users

    -- User Type
    user_type VARCHAR(20) DEFAULT 'local',  -- 'local' | 'active_directory'
    ad_sync_id VARCHAR(255) UNIQUE,         -- AD user ID

    -- Status
    is_active BOOLEAN DEFAULT TRUE,
    is_superuser BOOLEAN DEFAULT FALSE,
    email_verified BOOLEAN DEFAULT FALSE,

    -- MFA/Security
    mfa_enabled BOOLEAN DEFAULT FALSE,
    mfa_secret VARCHAR(255),                -- Encrypted TOTP secret
    backup_codes TEXT,                      -- JSON array

    -- Security Tracking
    failed_login_attempts INT DEFAULT 0,
    locked_until DATETIME,
    last_login_at DATETIME,
    last_login_ip VARCHAR(45),

    -- Password Management
    password_changed_at DATETIME,
    require_password_change BOOLEAN DEFAULT FALSE,

    -- Department & Contact
    department_id INT,
    phone_number VARCHAR(20),
    address TEXT,
    position VARCHAR(100),

    -- Foreign Keys
    role_id INT,
    FOREIGN KEY (role_id) REFERENCES auth_db.roles(id),

    -- Timestamps
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
```

**Table: roles**
```sql
CREATE TABLE auth_db.roles (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    permissions JSON,  -- Array of permission codes
    is_active BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
```

**Table: refresh_tokens**
```sql
CREATE TABLE auth_db.refresh_tokens (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    token VARCHAR(500) UNIQUE NOT NULL,
    expires_at DATETIME NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES auth_db.users(id) ON DELETE CASCADE
);
```

**Table: password_reset_tokens**
```sql
CREATE TABLE auth_db.password_reset_tokens (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    token VARCHAR(255) UNIQUE NOT NULL,
    expires_at DATETIME NOT NULL,
    used BOOLEAN DEFAULT FALSE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES auth_db.users(id) ON DELETE CASCADE
);
```

### 5.2. Asset Service (asset_db)

**Table: assets**
```sql
CREATE TABLE asset_db.assets (
    id INT PRIMARY KEY AUTO_INCREMENT,
    asset_code VARCHAR(50) UNIQUE NOT NULL,  -- Auto-generated
    name VARCHAR(255) NOT NULL,
    description TEXT,

    -- Classification
    category_id INT NOT NULL,
    asset_type VARCHAR(20) NOT NULL,  -- 'fixed' | 'tool'

    -- Financial
    purchase_price DECIMAL(15,2) NOT NULL,
    current_value DECIMAL(15,2),
    depreciation_rate DECIMAL(5,2),   -- Percentage
    depreciation_method VARCHAR(20),  -- 'straight_line' | 'declining_balance'

    -- Status
    status VARCHAR(20) NOT NULL,  -- 'available', 'assigned', 'maintenance', 'retired'
    condition VARCHAR(20),        -- 'new', 'good', 'fair', 'poor'

    -- Assignment
    assigned_to INT,              -- User ID
    assigned_at DATETIME,

    -- Location
    location VARCHAR(255),
    department_id INT,

    -- Purchase Info
    purchase_date DATE NOT NULL,
    warranty_expiry DATE,
    supplier VARCHAR(255),
    invoice_number VARCHAR(100),

    -- QR Code
    qr_code VARCHAR(500),

    -- Timestamps
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    FOREIGN KEY (category_id) REFERENCES asset_db.categories(id),
    INDEX idx_asset_code (asset_code),
    INDEX idx_status (status),
    INDEX idx_assigned_to (assigned_to)
);
```

**Table: categories**
```sql
CREATE TABLE asset_db.categories (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) UNIQUE NOT NULL,
    code VARCHAR(50) UNIQUE NOT NULL,
    description TEXT,
    parent_id INT,  -- For hierarchical categories
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (parent_id) REFERENCES asset_db.categories(id)
);
```

**Table: asset_history**
```sql
CREATE TABLE asset_db.asset_history (
    id INT PRIMARY KEY AUTO_INCREMENT,
    asset_id INT NOT NULL,
    action VARCHAR(50) NOT NULL,  -- 'created', 'assigned', 'returned', 'maintenance', etc.
    description TEXT,
    performed_by INT,  -- User ID
    performed_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    metadata JSON,     -- Additional data specific to action
    FOREIGN KEY (asset_id) REFERENCES asset_db.assets(id) ON DELETE CASCADE
);
```

**Xem thêm**: [docs/04. Database_Design.md](docs/04. Database_Design.md)

---

## 6. API ENDPOINTS

### 6.1. Auth Service APIs (Port 8088)

#### Authentication
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/api/v1/auth/login` | Login (Step 1: email/password) | No |
| POST | `/api/v1/auth/verify-otp` | Verify OTP (Step 2) | Temp token |
| POST | `/api/v1/auth/refresh` | Refresh access token | Refresh token |
| POST | `/api/v1/auth/logout` | Logout | Yes |
| GET | `/api/v1/auth/me` | Get current user info | Yes |

#### MFA Management
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/api/v1/auth/mfa/setup` | Generate QR code for MFA | Yes |
| POST | `/api/v1/auth/mfa/enable` | Enable MFA with verification | Yes |
| POST | `/api/v1/auth/mfa/disable` | Disable MFA | Yes |

#### Password Management
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/api/v1/auth/forgot-password` | Request password reset | No |
| POST | `/api/v1/auth/reset-password` | Reset password with token | No |

#### User Management
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/api/v1/users` | List users (paginated) | Yes |
| POST | `/api/v1/users` | Create user | Yes |
| GET | `/api/v1/users/{user_id}` | Get user details | Yes |
| PUT | `/api/v1/users/{user_id}` | Update user | Yes |
| DELETE | `/api/v1/users/{user_id}` | Delete user | Yes |
| POST | `/api/v1/users/{user_id}/activate` | Activate user | Yes |
| POST | `/api/v1/users/{user_id}/deactivate` | Deactivate user | Yes |
| POST | `/api/v1/users/change-password` | Change own password | Yes |

#### Role Management
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/api/v1/roles` | List roles | Yes |
| POST | `/api/v1/roles` | Create role | Yes |
| GET | `/api/v1/roles/{role_id}` | Get role details | Yes |
| PUT | `/api/v1/roles/{role_id}` | Update role | Yes |
| DELETE | `/api/v1/roles/{role_id}` | Delete role | Yes |

#### Admin
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/api/v1/auth/sync-ad` | Sync users from Active Directory | Yes (Admin) |

### 6.2. Asset Service APIs (Port 8089)

#### Assets
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/api/v1/assets/` | List assets (with filters) | Yes |
| POST | `/api/v1/assets/` | Create asset | Yes |
| GET | `/api/v1/assets/{asset_id}` | Get asset details | Yes |
| PUT | `/api/v1/assets/{asset_id}` | Update asset | Yes |
| DELETE | `/api/v1/assets/{asset_id}` | Delete asset | Yes |
| POST | `/api/v1/assets/{asset_id}/assign` | Assign asset to user | Yes |
| POST | `/api/v1/assets/{asset_id}/return` | Return asset | Yes |
| GET | `/api/v1/assets/{asset_id}/history` | Get asset history | Yes |
| GET | `/api/v1/assets/{asset_id}/depreciation` | Get depreciation info | Yes |

#### Categories
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/api/v1/categories/` | List categories | Yes |
| POST | `/api/v1/categories/` | Create category | Yes |
| GET/PUT/DELETE | `/api/v1/categories/{id}` | Category operations | Yes |

#### Attachments
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/api/v1/assets/{id}/attachments` | Upload attachment | Yes |
| GET | `/api/v1/assets/attachments/{id}` | Download attachment | Yes |

#### Statistics
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/api/v1/assets/statistics/summary` | Get asset statistics | Yes |

**API Documentation**:
- Auth: http://localhost:8088/docs
- Asset: http://localhost:8089/docs

**Xem thêm**: [docs/05. API_Specification.md](docs/05. API_Specification.md)

---

## 7. CODE STYLE & CONVENTIONS

### 7.1. Naming Conventions
- **Classes**: `PascalCase` (e.g., `AuthService`, `UserRepository`)
- **Functions/Methods**: `snake_case` (e.g., `verify_password`, `get_user_by_email`)
- **Constants**: `UPPER_SNAKE_CASE` (e.g., `ACCESS_TOKEN_EXPIRE_MINUTES`)
- **Variables**: `snake_case` (e.g., `user_id`, `access_token`)
- **Private members**: `_underscore_prefix` (e.g., `_validate_token`)

### 7.2. Import Order
1. Standard library
2. Third-party libraries
3. Local application imports
4. Blank line between groups

```python
import logging
from datetime import datetime, timedelta
from typing import Optional

from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.user import User
from app.schemas.auth import LoginRequest
```

### 7.3. Type Hints
**REQUIRED** - Luôn sử dụng type hints:

```python
def create_user(email: str, password: str) -> User:
    ...

async def get_user_by_id(user_id: int, db: Session) -> Optional[User]:
    ...
```

### 7.4. Docstrings
Sử dụng docstrings cho modules, classes, và functions:

```python
"""
Auth Service - User Authentication
Handles login, MFA, and token management
"""

async def verify_otp(temp_token: str, otp_code: str) -> dict:
    """
    Verify OTP code and return access tokens

    Args:
        temp_token: Temporary token from step 1 login
        otp_code: 6-digit TOTP code

    Returns:
        dict: Access token, refresh token, and user info

    Raises:
        HTTPException: If OTP is invalid or expired
    """
    ...
```

### 7.5. Logging Format
```python
import logging

logger = logging.getLogger(__name__)

# Good
logger.info("User login successful", extra={
    "user_id": user.id,
    "email": user.email,
    "ip": client_ip
})

# Don't log sensitive data
logger.error("Login failed")  # ✅ Good
logger.error(f"Password {password} invalid")  # ❌ BAD
```

### 7.6. Error Handling
```python
from fastapi import HTTPException, status

# Custom exceptions
class InvalidCredentialsError(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

# Usage
if not verify_password(password, user.hashed_password):
    raise InvalidCredentialsError()
```

### 7.7. Code Formatting
- **Line length**: Max 100 characters (Black default: 88)
- **Indentation**: 4 spaces
- **Strings**: Use double quotes `"..."` for consistency
- **Trailing commas**: Use in multi-line structures

**Tools**:
```bash
# Format code
black .

# Lint
flake8 .

# Type check
mypy app/
```

**Xem thêm**: Memory file `code_style_and_conventions`

---

## 8. DESIGN PATTERNS

### 8.1. Repository Pattern
**Tách biệt logic truy cập dữ liệu**:

```python
# repositories/user_repository.py
class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, user_id: int) -> Optional[User]:
        return self.db.query(User).filter(User.id == user_id).first()

    def get_by_email(self, email: str) -> Optional[User]:
        return self.db.query(User).filter(User.email == email).first()

    def create(self, user: User) -> User:
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user
```

### 8.2. Service Layer Pattern
**Encapsulate business logic**:

```python
# services/auth_service.py
class AuthService:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    async def login(self, email: str, password: str) -> dict:
        # Business logic
        user = self.user_repo.get_by_email(email)
        if not user:
            raise InvalidCredentialsError()

        if not verify_password(password, user.hashed_password):
            raise InvalidCredentialsError()

        # Generate tokens
        access_token = create_access_token(user.id)
        return {"access_token": access_token, "user": user}
```

### 8.3. Dependency Injection (FastAPI)
```python
# core/dependencies.py
def get_db() -> Generator:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    # Decode token and get user
    ...

# endpoints/users.py
@router.get("/users/me")
async def get_me(current_user: User = Depends(get_current_user)):
    return current_user
```

### 8.4. CQRS Pattern
**Command (Write)**:
```python
# Write to MySQL
class UserWriteRepository:
    def create_user(self, user_data: dict) -> User:
        user = User(**user_data)
        self.db.add(user)
        self.db.commit()

        # Publish event
        publish_event("UserCreated", user.to_dict())
        return user
```

**Query (Read)**:
```python
# Read from MongoDB
class UserReadRepository:
    async def find_by_email(self, email: str) -> dict:
        return await self.mongo_db.users.find_one({"email": email})
```

### 8.5. Event-Driven Architecture
```python
# Event publishing
def publish_event(event_type: str, data: dict):
    channel.basic_publish(
        exchange='events',
        routing_key=event_type,
        body=json.dumps(data)
    )

# Event consumer
async def on_user_created(message):
    user_data = json.loads(message.body)
    # Update read model in MongoDB
    await mongo_db.users.insert_one(user_data)
```

**Xem thêm**: Memory file `design_patterns_and_guidelines`

---

## 9. TRẠNG THÁI HIỆN TẠI

### 9.1. Sprint Progress

| Sprint | Week | Focus | Status | Progress |
|--------|------|-------|--------|----------|
| Sprint 1 | 1-2 | Infrastructure | ✅ Complete | 100% |
| Sprint 2 | 3 | Auth Service | ✅ Complete | 95% |
| **Sprint 3** | **4-5** | **Asset Service** | 🚧 **In Progress** | **40%** |
| Sprint 4 | 6-7 | Procurement 1 | ⏸️ Pending | 0% |
| Sprint 5 | 8 | Procurement 2 | ⏸️ Pending | 0% |
| Sprint 6 | 9-10 | Maintenance | ⏸️ Pending | 0% |
| Sprint 7 | 11 | Reports | ⏸️ Pending | 0% |
| Sprint 8-12 | 12-16 | Admin & Deploy | ⏸️ Pending | 0% |

**Overall Project**: ~15-20% Complete

### 9.2. Services Status

✅ **Completed Services**:
- Auth API (24 endpoints)
- Auth Frontend (8 pages)

🚧 **In Progress**:
- Asset API (12 endpoints - implemented, testing pending)
- Asset Frontend (3 pages - basic UI complete)

⏸️ **Pending**:
- Procurement Service
- Maintenance Service
- Report Service
- Notification Service

### 9.3. Infrastructure Status

| Component | Status | Health |
|-----------|--------|--------|
| MySQL 8.0 | ✅ Running | Healthy |
| MongoDB 7 | ✅ Running | Healthy |
| Redis 7 | ✅ Running | Healthy |
| RabbitMQ 3.12 | ✅ Running | Healthy |
| auth-api | ✅ Running | Healthy |
| auth-fe | ✅ Running | Healthy |
| asset-api | ✅ Running | Healthy |
| asset-fe | ✅ Running | Healthy |
| Nginx Gateway | ⏸️ Commented | N/A |

**Check status**:
```bash
docker ps
docker compose ps
```

### 9.4. Known Issues

1. **OTP Sync Issue** ⚠️
   - **Symptom**: OTP codes from authenticator app don't match server
   - **Cause**: Secret key mismatch
   - **Solution**: See [FIX_OTP_GUIDE.md](FIX_OTP_GUIDE.md)
   - **Workaround**: Debug endpoints available for development

2. **Infrastructure Containers Not Auto-Start** ℹ️
   - **Issue**: MySQL, MongoDB, Redis, RabbitMQ don't auto-start
   - **Workaround**: `docker start mysql mongodb redis rabbitmq`
   - **Fix**: Update docker-compose restart policies

3. **Debug Endpoints in Production** ⚠️
   - `/api/v1/auth/debug/*` endpoints expose sensitive data
   - **Action Required**: Remove/disable before production

### 9.5. Documentation Status

| Document | Status | Quality |
|----------|--------|---------|
| Project Overview | ✅ Complete | Excellent |
| Business Requirements | ✅ Complete | Excellent |
| System Architecture | ✅ Complete | Excellent |
| Database Design | ✅ Complete | Excellent |
| API Specification | ✅ Complete | Excellent |
| User Stories | ✅ Complete | Excellent |
| Implementation Plan | ✅ Complete | Excellent |
| Sprint 1-2 Verification | ✅ Complete | Excellent |
| OTP Fix Guide | ✅ Complete | Good |
| CLAUDE.md (this file) | ✅ Complete | Excellent |

---

## 10. WORKFLOW LÀM VIỆC

### 10.1. Starting Development Environment

**Option 1: Start All Services**
```bash
# Navigate to project root
cd c:\Users\nhdinh\dev\officework

# Start infrastructure
docker start mysql mongodb redis rabbitmq

# Wait 10-15 seconds for health checks

# Start application services
docker compose up -d auth-api auth-fe asset-api asset-fe

# Check status
docker compose ps
```

**Option 2: Start Specific Service**
```bash
# Restart a specific service
docker compose restart auth-api

# View logs
docker compose logs -f auth-api

# Stop a service
docker compose stop auth-api
```

### 10.2. Accessing Services

| Service | URL | Credentials |
|---------|-----|-------------|
| Auth API Docs | http://localhost:8088/docs | N/A |
| Auth Frontend | http://localhost:3000 | admin@example.com / admin123 |
| Asset API Docs | http://localhost:8089/docs | N/A |
| Asset Frontend | http://localhost:3001 | Requires auth token |
| RabbitMQ Management | http://localhost:15672 | guest / guest |
| MySQL | localhost:3306 | officework_dbu / (see .secrets/) |
| MongoDB | localhost:27017 | admin / secret123 |
| Redis | localhost:6379 | (no auth) |

### 10.3. Database Migrations

**Create a new migration**:
```bash
# Enter service container
docker compose exec auth-api bash

# Generate migration
alembic revision --autogenerate -m "Add new column"

# Review the migration file in alembic/versions/

# Apply migration
alembic upgrade head

# Rollback
alembic downgrade -1
```

### 10.4. Testing APIs

**Using curl**:
```bash
# Login
curl -X POST http://localhost:8088/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@example.com", "password": "admin123"}'

# Use access token
curl -X GET http://localhost:8088/api/v1/auth/me \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**Using Swagger UI**:
1. Open http://localhost:8088/docs
2. Click "Authorize" button
3. Enter token: `Bearer YOUR_ACCESS_TOKEN`
4. Test endpoints

### 10.5. Development Workflow

1. **Create a feature branch**:
   ```bash
   git checkout -b feature/user-profile
   ```

2. **Make changes**:
   - Edit code in `services/{service}/app/`
   - Follow code style conventions
   - Add type hints
   - Write docstrings

3. **Test changes**:
   ```bash
   # Restart service to apply changes
   docker compose restart auth-api

   # Check logs
   docker compose logs -f auth-api
   ```

4. **Format & lint**:
   ```bash
   docker compose exec auth-api black app/
   docker compose exec auth-api flake8 app/
   ```

5. **Commit changes**:
   ```bash
   git add .
   git commit -m "Add user profile endpoint"
   ```

6. **Push & create PR**:
   ```bash
   git push origin feature/user-profile
   # Create Pull Request on GitHub
   ```

---

## 11. COMMON TASKS

### 11.1. Adding a New API Endpoint

**Example: Add GET /api/v1/users/profile endpoint**

1. **Create Pydantic schema** (`app/schemas/user.py`):
```python
class UserProfile(BaseModel):
    id: int
    email: str
    full_name: str
    phone_number: Optional[str]
    department_id: Optional[int]

    class Config:
        from_attributes = True
```

2. **Add repository method** (`app/repositories/user_repository.py`):
```python
def get_user_profile(self, user_id: int) -> Optional[User]:
    return self.db.query(User).filter(User.id == user_id).first()
```

3. **Add service method** (`app/services/user_service.py`):
```python
async def get_profile(self, user_id: int) -> UserProfile:
    user = self.user_repo.get_user_profile(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return UserProfile.from_orm(user)
```

4. **Add endpoint** (`app/api/v1/endpoints/users.py`):
```python
@router.get("/profile", response_model=UserProfile)
async def get_my_profile(
    current_user: User = Depends(get_current_user)
):
    """Get current user's profile"""
    return current_user
```

5. **Test the endpoint**:
```bash
docker compose restart auth-api
curl -X GET http://localhost:8088/api/v1/users/profile \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 11.2. Adding a New Database Table

1. **Create SQLAlchemy model** (`app/models/department.py`):
```python
from sqlalchemy import Column, String, Integer
from app.models.base import Base

class Department(Base):
    __tablename__ = "departments"
    __table_args__ = {'schema': 'auth_db'}

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    code = Column(String(50), unique=True, nullable=False)
    description = Column(String(500))
    parent_id = Column(Integer, ForeignKey('auth_db.departments.id'))
```

2. **Generate migration**:
```bash
docker compose exec auth-api alembic revision --autogenerate -m "Add departments table"
```

3. **Review migration file** in `alembic/versions/`

4. **Apply migration**:
```bash
docker compose exec auth-api alembic upgrade head
```

### 11.3. Adding MFA to a User Account

**Via API**:
```bash
# 1. Login
TOKEN=$(curl -s -X POST http://localhost:8088/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@example.com","password":"admin123"}' \
  | jq -r '.temp_token')

# 2. Setup MFA (get QR code)
curl -X POST http://localhost:8088/api/v1/auth/mfa/setup \
  -H "Authorization: Bearer $TOKEN"

# 3. Scan QR code with Google Authenticator

# 4. Enable MFA with first OTP
curl -X POST http://localhost:8088/api/v1/auth/mfa/enable \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"otp_code":"123456"}'
```

**Via Frontend**:
1. Login at http://localhost:3000
2. Go to Profile → Security Settings
3. Click "Thiết lập MFA"
4. Scan QR code with Google Authenticator
5. Enter OTP to enable

### 11.4. Debugging Login Issues

**Check logs**:
```bash
docker compose logs -f auth-api | grep -i "login\|error"
```

**Test login endpoint**:
```bash
curl -v -X POST http://localhost:8088/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@example.com","password":"admin123"}'
```

**Common issues**:
- **401 Unauthorized**: Wrong password or email
- **423 Locked**: Account locked after 5 failed attempts
- **MFA required**: User has MFA enabled, need to verify OTP

### 11.5. Resetting User Password (Admin)

**Via Database**:
```bash
docker exec -it mysql mysql -uofficework_dbu -p

USE auth_db;
-- Hash for "NewPassword123"
UPDATE users
SET hashed_password = '$2b$12$...'
WHERE email = 'user@example.com';
```

**Via API (Admin)**:
```bash
curl -X POST http://localhost:8088/api/v1/users/{user_id}/reset-password \
  -H "Authorization: Bearer ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"new_password":"NewPassword123"}'
```

---

## 12. TROUBLESHOOTING

### 12.1. Service Won't Start

**Symptom**: `docker compose up` fails or service unhealthy

**Check**:
```bash
# View logs
docker compose logs auth-api

# Common issues:
# 1. Port already in use
netstat -ano | findstr :8088

# 2. Database connection failed
# Check MySQL is running
docker ps | grep mysql

# 3. Missing secrets file
ls -la .secrets/
```

**Fix**:
```bash
# Rebuild service
docker compose build auth-api

# Remove old containers
docker compose down
docker compose up -d
```

### 12.2. Database Connection Error

**Symptom**: `Connection refused` or `Access denied`

**Check connection**:
```bash
# Test MySQL connection
docker exec -it mysql mysql -uofficework_dbu -p$(cat .secrets/mysql_passwd.txt) -e "SHOW DATABASES;"

# Check environment variables
docker compose exec auth-api env | grep DATABASE
```

**Fix**:
```bash
# Recreate MySQL container
docker compose down mysql
docker compose up -d mysql

# Wait for health check
docker compose ps mysql
```

### 12.3. OTP Not Working

**Symptom**: OTP codes don't match

**Solution**: See [FIX_OTP_GUIDE.md](FIX_OTP_GUIDE.md)

**Quick fix (Development only)**:
```bash
# Disable MFA for user
curl -X POST "http://localhost:8088/api/v1/auth/debug/disable-mfa?email=admin@example.com"
```

### 12.4. Migration Conflicts

**Symptom**: `alembic upgrade head` fails with conflicts

**Check current version**:
```bash
docker compose exec auth-api alembic current
docker compose exec auth-api alembic history
```

**Fix**:
```bash
# Rollback to specific version
docker compose exec auth-api alembic downgrade <revision>

# Or reset to base
docker compose exec auth-api alembic downgrade base

# Re-apply migrations
docker compose exec auth-api alembic upgrade head
```

### 12.5. Frontend Can't Connect to API

**Symptom**: Frontend shows connection errors

**Check**:
```bash
# 1. API is running
curl http://localhost:8088/health

# 2. Frontend environment variables
docker compose exec auth-fe env | grep API_BASE

# 3. CORS configuration
docker compose logs auth-api | grep CORS
```

**Fix CORS**:
```python
# In auth-api/app/main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 12.6. Docker Out of Space

**Symptom**: `no space left on device`

**Clean up**:
```bash
# Remove unused containers, images, volumes
docker system prune -a

# Remove specific volumes
docker volume ls
docker volume rm officework_mysql_data

# Check disk usage
docker system df
```

---

## 📖 TÀI LIỆU THAM KHẢO

### Documentation Files
1. [docs/01. Project_Overview.md](docs/01.%20Project_Overview.md) - Tổng quan dự án
2. [docs/02. Business_Requirements.md](docs/02.%20Business_Requirements.md) - Yêu cầu nghiệp vụ
3. [docs/03. System_Architecture.md](docs/03.%20System_Architecture.md) - Kiến trúc hệ thống
4. [docs/04. Database_Design.md](docs/04.%20Database_Design.md) - Thiết kế database
5. [docs/05. API_Specification.md](docs/05.%20API_Specification.md) - Đặc tả API
6. [docs/06. User_Stories.md](docs/06.%20User_Stories.md) - User stories
7. [docs/07. Implementation_Plan.md](docs/07.%20Implementation_Plan.md) - Kế hoạch triển khai

### Verification & Guides
- [SPRINT_1_2_VERIFICATION_REPORT.md](SPRINT_1_2_VERIFICATION_REPORT.md) - Báo cáo xác nhận Sprint 1-2
- [FIX_OTP_GUIDE.md](FIX_OTP_GUIDE.md) - Hướng dẫn khắc phục lỗi OTP
- [README.md](README.md) - Project README

### Memory Files (Claude Code)
- `project_overview` - Project summary
- `tech_stack` - Technology stack details
- `code_style_and_conventions` - Coding standards
- `design_patterns_and_guidelines` - Architecture patterns
- `codebase_structure` - Directory structure
- `task_completion_checklist` - Task checklist

### API Documentation (Interactive)
- Auth API: http://localhost:8088/docs
- Asset API: http://localhost:8089/docs

---

## 🎯 HƯỚNG DẪN SỬ DỤNG FILE NÀY

### Khi bắt đầu conversation mới với Claude:

1. **Yêu cầu Claude đọc file này**:
   ```
   "Please read CLAUDE.md to understand the project context"
   ```

2. **Cho context cụ thể**:
   ```
   "We're working on Sprint 3 - Asset Management.
   Check current status in Section 9.1"
   ```

3. **Tham khảo sections cụ thể**:
   - Section 4: Cấu trúc thư mục
   - Section 5: Database schema
   - Section 6: API endpoints
   - Section 7: Code style
   - Section 11: Common tasks

### Cập nhật file này:

**Khi có thay đổi lớn**:
- Sprint mới hoàn thành → Update Section 9.1
- Service mới deploy → Update Section 2.2, 9.2
- Breaking changes → Update toàn bộ sections liên quan
- Bugs mới → Update Section 12

**Ai cập nhật**: Tech Lead hoặc AI assistant (với xác nhận)

---

## ✅ CHECKLIST KHI LÀM VIỆC

### Before Starting Work
- [ ] Đọc CLAUDE.md sections liên quan
- [ ] Check current sprint status (Section 9.1)
- [ ] Verify services are running (`docker compose ps`)
- [ ] Review API docs nếu làm việc với APIs

### During Development
- [ ] Follow code style conventions (Section 7)
- [ ] Apply design patterns (Section 8)
- [ ] Add type hints và docstrings
- [ ] Test locally before commit
- [ ] Update relevant documentation

### Before Committing
- [ ] Run Black formatter
- [ ] Run Flake8 linter
- [ ] Test endpoints (if API changes)
- [ ] Update CLAUDE.md if needed
- [ ] Update API docs if endpoints changed

---

**Phiên bản**: 1.0
**Tác giả**: Generated by Claude AI
**Maintained by**: Hung Dinh (Tech Lead)
**Last updated**: 2025-10-21

---

## 📞 CONTACT & SUPPORT

**Team Lead**: Hung Dinh
**Repository**: https://github.com/nhdinh/owrk
**Documentation**: [docs/](docs/)

For questions about this guide or the project, refer to:
- Implementation Plan: [docs/07. Implementation_Plan.md](docs/07.%20Implementation_Plan.md)
- Verification Report: [SPRINT_1_2_VERIFICATION_REPORT.md](SPRINT_1_2_VERIFICATION_REPORT.md)
