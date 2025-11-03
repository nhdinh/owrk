# CLAUDE.md - AI Assistant Guide

> **Mục đích**: Tài liệu này cung cấp toàn bộ thông tin cần thiết để Claude AI (hoặc bất kỳ AI assistant nào) có thể hiểu nhanh và làm việc hiệu quả với dự án này.

**Cập nhật lần cuối**: 2025-11-01
**Phiên bản**: 1.2
**Dự án**: Office Equipment Asset Management System (officework)

---

## 📚 MỤC LỤC

1. [Tổng quan hệ thống](#1-Tổng-quan-hệ-thống)
2. [Kiến trúc hệ thống](#2-kiến-trúc-hệ-thống)
3. [API Endpoints](#3-api-endpoints)
4. [Code Style & Conventions](#4-code-style--conventions)
5. [Design Patterns](#5-design-patterns)
6. [Trạng thái hiện tại](#6-trạng-thái-hiện-tại)
7. [Workflow làm việc](#7-workflow-làm-việc)
8. [Common Tasks](#8-common-tasks)
9. [Troubleshooting](#9-troubleshooting)

---

## 1. TỔNG QUAN HỆ THỐNG

- Chi tiết về tổng quan hệ thống được nêu trong [`01. Project_Overview.md`](./docs/01.%20Project_Overview.md)
- Chi tiết về các yêu cầu nghiệp vụ chi tiết được nêu trong[`02. Business_Requirements.md`](./docs/02.%20Business_Requirements.md)
- [`06. User_Stories.md`](./docs/06.%20User_Stories.md): User stories và use cases
- [`07. Implementation_Plan.md`](./docs/07.%20Implementation_Plan.md): Kế hoạch triển khai chi tiết

---

## 2. KIẾN TRÚC HỆ THỐNG

- Chi tiết về kiến trúc hệ thống, bao gồm Kiến trúc tổng thể, Technology Stack, Danh sách các Microservices được nêu trong [`03. System_Architecture.md`](./docs/03.%20System_Architecture.md)
- Chi tiết về các mẫu thiết kế được sử dụng trong dự án được nêu trong [Section 8 - Design Patterns](#8-design-patterns) bên dưới.
- Chi tiết về Database design và schema được nêu trong [`04. Database_Design.md`](./docs/04.%20Database_Design.md)

---

## 3. API ENDPOINTS

- Chi tiết các đặc tả về API được nêu trong [./docs/05. API_Specification.md](./docs/05.%20API_Specification.md)

---

## 4. CODE STYLE & CONVENTIONS

### 4.1. Naming Conventions

- **Classes**: `PascalCase` (e.g., `AuthService`, `UserRepository`)
- **Functions/Methods**: `snake_case` (e.g., `verify_password`, `get_user_by_email`)
- **Constants**: `UPPER_SNAKE_CASE` (e.g., `ACCESS_TOKEN_EXPIRE_MINUTES`)
- **Variables**: `snake_case` (e.g., `user_id`, `access_token`)
- **Private members**: `_underscore_prefix` (e.g., `_validate_token`)

### 4.2. Import Order

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

### 4.3. Type Hints

**REQUIRED** - Luôn sử dụng type hints:

```python
def create_user(email: str, password: str) -> User:
    ...

async def get_user_by_id(user_id: int, db: Session) -> Optional[User]:
    ...
```

### 4.4. Docstrings

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

### 4.5. Logging Format

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

### 4.6. Error Handling

Sử dụng custom exceptions cho các trường hợp phát sinh lỗi:

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

### 4.7. Code Formatting

- **Line length**: Max 88 characters (Black default: 88)
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

## 5. DESIGN PATTERNS

### 5.1. Repository Pattern

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

### 5.2. Service Layer Pattern

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

### 5.3. Dependency Injection (FastAPI)

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

### 5.4. CQRS Pattern

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

### 5.5. Event-Driven Architecture

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

### 5.6. Module Federation (Micro-Frontends)

**Share components across micro-frontends at runtime with YAML-based navigation and authentication state**:

**Host Application** (exposes components):

```typescript
// vite.config.ts in shared-components
federation({
  name: 'shared_components',
  filename: 'remoteEntry.js',
  exposes: {
    './AppSidebar': './src/components/AppSidebar.tsx',
    './AppLayout': './src/components/AppLayout.tsx',
  },
  shared: {
    react: { singleton: true, requiredVersion: '^18.3.1' },
    'react-dom': { singleton: true, requiredVersion: '^18.3.1' },
  },
})
```

**YAML-Based Navigation Configuration** ([navigation.yaml](services/shared-components/src/config/navigation.yaml)):

```yaml
navigation:
  - name: Authentication
    href: /auth/
    icon: Shield
    service: auth
    description: User and role management
    submenu:
      - name: Users
        href: /auth/users
        icon: Users
      - name: Roles
        href: /auth/roles
        icon: ShieldCheck
      - name: Profile
        href: /auth/profile
        icon: User
      - name: MFA Setup
        href: /auth/mfa-setup
        icon: Key
```

**AppSidebar with AuthContext** ([AppSidebar.tsx](services/shared-components/src/components/AppSidebar.tsx)):

```typescript
import yaml from 'js-yaml';
import navigationConfig from '../config/navigation.yaml?raw';

interface User {
  id: number;
  email: string;
  full_name: string;
  role?: { name: string; display_name: string };
}

interface AppSidebarProps {
  currentService?: 'dashboard' | 'auth' | 'assets';
  user?: User | null;
  isLoading?: boolean;
  onLogout?: () => void;
}

export function AppSidebar({ currentService, user, isLoading, onLogout }: AppSidebarProps) {
  // Parse YAML navigation
  const config = yaml.load(navigationConfig) as NavigationConfig;

  // Render menu with expandable submenus
  // Display user info with avatar
  // Show logout button when authenticated
}
```

**Consumer Application** (imports remote components with auth):

```typescript
// vite.config.ts in auth-fe
federation({
  name: 'auth_app',
  remotes: {
    shared_components: 'http://localhost:8000/shared/assets/remoteEntry.js',
  },
  shared: {
    react: { singleton: true, requiredVersion: '^18.3.1' },
    'react-dom': { singleton: true, requiredVersion: '^18.3.1' },
  },
})

// Component usage with AuthContext
// @ts-ignore - Module Federation remote import
import { AppSidebar } from 'shared_components/AppSidebar';
import { useAuth } from '@/lib/auth-context';

export function AppLayout({ children }: AppLayoutProps) {
  const { user, isLoading, logout } = useAuth();

  return (
    <div className="flex h-screen bg-background">
      <AppSidebar
        currentService="auth"
        user={user}
        isLoading={isLoading}
        onLogout={logout}
      />
      <div className="flex-1 overflow-y-auto">{children}</div>
    </div>
  );
}
```

**Benefits**:
- Single source of truth for shared components
- Runtime code sharing between independent apps
- Reduced bundle sizes through shared dependencies (~65% reduction)
- Independent deployments with coordinated runtime integration
- **YAML-based navigation**: Centralized menu configuration with expandable submenus
- **AuthContext integration**: User state shared across all micro-frontends
- **User profile display**: Avatar with initials, email, full name, and role
- **Centralized logout**: Logout functionality available in all apps

**Key Features**:
1. **YAML Navigation System** - [navigation.yaml](services/shared-components/src/config/navigation.yaml)
   - Centralized menu configuration
   - Expandable/collapsible submenus
   - Icon mapping from lucide-react
   - Service-aware highlighting

2. **Authentication State Sharing**
   - User object passed from AuthContext
   - Loading state support
   - Graceful fallback to login prompt
   - Avatar with auto-generated initials

**Build Output**:
- remoteEntry.js: 3.6 KB
- AppSidebar bundle: 126 KB (includes js-yaml parser)
- AppLayout bundle: 508 bytes
- Shared React manifests: 104 bytes total

**Xem thêm**:
- Memory file `design_patterns_and_guidelines`
- **[MODULE_FEDERATION_IMPLEMENTATION.md](docs/deliveries/MODULE_FEDERATION_IMPLEMENTATION.md)** - Complete implementation guide

---

## 6. TRẠNG THÁI HIỆN TẠI

### 6.1. Sprint Progress

| Sprint       | Week  | Focus            | Status          | Progress |
| ------------ | ----- | ---------------- | --------------- | -------- |
| Sprint 1     | 1-2   | Infrastructure   | ✅ Complete     | 100%     |
| **Sprint 2** | **3** | **Auth Service** | ✅ **Complete** | **100%** |
| Sprint 3     | 4-5   | Asset Service    | 🚧 In Progress  | 40%      |
| Sprint 4     | 6-7   | Procurement 1    | ⏸️ Pending      | 0%       |
| Sprint 5     | 8     | Procurement 2    | ⏸️ Pending      | 0%       |
| Sprint 6     | 9-10  | Maintenance      | ⏸️ Pending      | 0%       |
| Sprint 7     | 11    | Reports          | ⏸️ Pending      | 0%       |
| Sprint 8-12  | 12-16 | Admin & Deploy   | ⏸️ Pending      | 0%       |

**Overall Project**: ~22% Complete (updated from ~15-20%)

### 6.2. Services Status

✅ **Completed Services**:

- **Auth API** (37 endpoints - fully complete)
  - User Management: 24 endpoints ✅
  - Role Management: 8 endpoints ✅ (5 new endpoints added 2025-10-29)
  - CQRS demo endpoints: 5 ✅
  - Features: Login, MFA, User/Role Management, CQRS Pattern, Event-Driven
- **Auth Frontend V2** (10 pages - fully functional)
  - Login, Register, Profile, MFA Setup, User Management, Role Management
  - User Create/Edit, Role Create/Edit, Permission Management
  - Built with: React 18 + Vite 5 + TypeScript + Tailwind + shadcn/ui + Module Federation
- **Asset API** (12 endpoints - fully complete)
  - Asset CRUD operations, Category management, Assignment tracking
  - Features: Asset lifecycle management, File attachments, History tracking
- **Asset Frontend V2** (3 pages - fully functional)
  - Assets list with filters/search/pagination, Asset detail view, Create/Edit forms
  - Built with: React 18 + Vite 5 + TypeScript + Tailwind + shadcn/ui + Module Federation
- **Dashboard API** (Basic endpoints - fully functional)
  - System overview, Statistics aggregation
  - Features: Dashboard metrics, Cross-service data aggregation
- **Dashboard Frontend V2** (1 page - fully functional)
  - Main dashboard with service navigation
  - Built with: React 18 + Vite 5 + TypeScript + Tailwind + shadcn/ui + Module Federation
- **Shared Components** (Module Federation Host - fully functional)
  - Exposes: AppSidebar (with YAML navigation + AuthContext), AppLayout
  - Features: Centralized navigation, User authentication display, Expandable submenus
  - Shared dependencies: React 18, ReactDOM
  - Built with: Vite 5 + @originjs/vite-plugin-federation + js-yaml
  - Bundle size: 126 KB (AppSidebar with YAML parser)

🚧 **In Progress**:

- (None - all current sprint tasks completed)

⏸️ **Pending**:

- Procurement Service
- Maintenance Service
- Report Service
- Notification Service

### 6.3. Infrastructure Status

| Component     | Status       | Health  | Port | Access URL |
| ------------- | ------------ | ------- | ---- | ---------- |
| **API Gateway** | ✅ **Running** | **Active** | **8000** | **http://localhost:8000** |
| MySQL 8.0     | ✅ Running   | Healthy | 3306 | - |
| MongoDB 7     | ✅ Running   | Healthy | 27017 | - |
| Redis 7       | ✅ Running   | Healthy | 6379 | - |
| RabbitMQ 3.12 | ✅ Running   | Healthy | 5672, 15672 | http://localhost:15672 |
| **shared-components** | ✅ **Running** | **Active** | **3400** | **http://localhost:8000/shared/** |
| auth-api      | ✅ Running   | Healthy | 8001 | http://localhost:8001 |
| auth-fe    | ✅ Running   | Active  | 3100 | http://localhost:8000/auth/ |
| asset-api     | ✅ Running   | Healthy | 8002 | http://localhost:8002 |
| asset-fe   | ✅ Running   | Active  | 3200 | http://localhost:8000/assets/ |
| dashboard-api | ✅ Running   | Active  | 8003 | http://localhost:8003 |
| dashboard-fe-v2 | ✅ Running | Active  | 3300 | http://localhost:8000/dashboard/ |
| auth-fe (legacy) | ⏸️ Stopped | N/A | 3000 | (Replaced by v2) |
| asset-fe (legacy) | ⏸️ Stopped | N/A | 3001 | (Replaced by v2) |

**Check status**:

```bash
docker ps
docker compose ps
```

### 6.4. Known Issues

#### ✅ RESOLVED

1. **MongoDB Authentication Error** ✅ FIXED (2025-10-28)

   - **Issue**: MongoDB authentication failed with error code 18
   - **Solution**: Created custom entrypoint script to read password from Docker secrets
   - **Status**: MongoDB now uses `.secrets/mongo_passwd.txt` successfully

2. **CQRS Event Data Format Mismatch** ✅ FIXED (2025-10-28)

   - **Issue**: Events published with `user_id` key, but MongoDB expected `id` key
   - **Solution**: Fixed all 5 command handlers to use correct event format
   - **Status**: MongoDB read model now syncs correctly with MySQL write model

3. **RabbitMQ Event Publishing** ✅ FIXED (2025-10-28)
   - **Issue**: Function signature mismatch causing "Max length exceeded" errors
   - **Solution**: Refactored `publish_event()` function signature
   - **Status**: Events now publish and consume successfully

4. **User Update ResponseValidationError** ✅ FIXED (2025-10-29)
   - **Issue**: Multiple user endpoints (update, activate, deactivate, unlock) returned 500 errors
   - **Solution**: Fixed response serialization in 4 endpoints, added address field to schema
   - **Status**: All user management operations working correctly

5. **Roles Showing 0 Permissions** ✅ FIXED (2025-10-29)
   - **Issue**: Roles list displayed "0 permissions" despite database having correct data
   - **Solution**: Added permissions array serialization to GET /roles endpoint
   - **Status**: Permission counts now display correctly

6. **Role CRUD Operations Missing** ✅ FIXED (2025-10-29)
   - **Issue**: POST /roles returned 405 Method Not Allowed
   - **Solution**: Implemented complete role CRUD (create, update, delete) and permission management (add, remove)
   - **Status**: 7 new endpoints added, full role management working

#### ⚠️ ACTIVE

No active critical issues. System running stable.

#### ℹ️ MINOR / NON-BLOCKING

1. **Infrastructure Containers Auto-Start** ℹ️

   - **Issue**: MySQL, MongoDB, Redis, RabbitMQ don't auto-start with docker-compose up
   - **Workaround**: `docker start mysql mongodb redis rabbitmq`
   - **Impact**: Low - one-time manual start needed
   - **Fix**: Update docker-compose restart policies (scheduled for Sprint 3)

2. **Debug Endpoints in Development** ⚠️ SECURITY NOTE
   - `/api/v1/auth/debug/*` endpoints expose sensitive data
   - **Action Required**: Remove/disable before production deployment
   - **Status**: Tracked in deployment checklist

### 6.5. Documentation Status

| Document                       | Status      | Quality   | Last Updated   |
| ------------------------------ | ----------- | --------- | -------------- |
| Project Overview               | ✅ Complete | Excellent | 2025-10-21     |
| Business Requirements          | ✅ Complete | Excellent | 2025-10-21     |
| System Architecture            | ✅ Complete | Excellent | 2025-10-21     |
| Database Design                | ✅ Complete | Excellent | 2025-10-21     |
| API Specification              | ✅ Complete | Excellent | 2025-10-21     |
| User Stories                   | ✅ Complete | Excellent | 2025-10-21     |
| Implementation Plan            | ✅ Complete | Excellent | 2025-10-21     |
| Sprint 1-2 Verification        | ✅ Complete | Excellent | 2025-10-27     |
| CQRS Implementation Report     | ✅ Complete | Excellent | 2025-10-28     |
| Auth Frontend V2 Fixes         | ✅ Complete | Excellent | 2025-10-29     |
| **Module Federation Report**   | ✅ **NEW**  | Excellent | **2025-11-01** |
| CLAUDE.md (this file)          | ✅ Complete | Excellent | **2025-11-01** |

---

## 7. WORKFLOW LÀM VIỆC

### 7.1. Starting Development Environment

**Option 1: Start All Services**

```bash
# Navigate to project root
cd c:\Users\nhdinh\dev\officework

# Start all services
docker start up -d --build

# Wait 10-15 seconds for health checks

# Check status
docker compose ps
```

**Option 2: Start Specific Service**

```bash
# Restart a specific service (for example, auth-api)
docker compose restart auth-api

# View logs
docker compose logs -f auth-api

# Stop a service
docker compose stop auth-api
```

### 7.2. Accessing Services

**⭐ PRIMARY ACCESS (via API Gateway)**:

| Service             | URL                                  | Credentials                      |
| ------------------- | ------------------------------------ | -------------------------------- |
| **Main Portal**     | **http://localhost:8000**            | Redirects to /dashboard/         |
| **Dashboard**       | **http://localhost:8000/dashboard/** | admin@example.com / admin123     |
| **Auth Frontend**   | **http://localhost:8000/auth/**      | admin@example.com / admin123     |
| **Asset Frontend**  | **http://localhost:8000/assets/**    | admin@example.com / admin123     |
| **Shared Components**| **http://localhost:8000/shared/**   | (Module Federation host)         |
| **API Gateway Docs**| **http://localhost:8000/docs**       | -                                |

**Direct Access (Development Only)**:

| Service             | URL                        | Credentials                      |
| ------------------- | -------------------------- | -------------------------------- |
| Shared Components   | http://localhost:3400      | (Module Federation host)         |
| Dashboard API       | http://localhost:8003      | Requires auth token              |
| Dashboard Frontend  | http://localhost:3300      | admin@example.com / admin123     |
| Auth API            | http://localhost:8001      | admin@example.com / admin123     |
| Auth API Docs       | http://localhost:8001/docs | Requires auth token              |
| Auth Frontend V2    | http://localhost:3100      | admin@example.com / admin123     |
| Asset API           | http://localhost:8002      | Requires auth token              |
| Asset API Docs      | http://localhost:8002/docs | Requires auth token              |
| Asset Frontend V2   | http://localhost:3200      | admin@example.com / admin123     |
| RabbitMQ Management | http://localhost:15672     | guest / guest                    |
| MySQL               | localhost:3306             | officework_dbu / (see .secrets/) |
| MongoDB             | localhost:27017            | admin / (see .secrets/)          |
| Redis               | localhost:6379             | (no auth)                        |

**📝 Notes**:
- Legacy frontends (auth-fe at :3000 and asset-fe at :3001) have been stopped. Use the API Gateway URLs instead.
- All three frontends (dashboard, auth, assets) use Module Federation to load shared components from shared-components service.
- remoteEntry.js available at: http://localhost:8000/shared/assets/remoteEntry.js

### 7.3. Database Migrations

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

### 7.4. Testing APIs

**Using curl for logging in and getting tokens**:

```bash

# Login (for example to auth-api) to get temp_token
export TEMP_TOKEN=$(curl -X POST http://localhost:8001/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@example.com", "password": "admin123"}' | grep temp_token | cut -d'"' -f4)

# Use temp_token to verify OTP and get access token
export ACCESS_TOKEN=$(curl -X POST http://localhost:8001/api/v1/auth/verify-otp \
  -H "Content-Type: application/json" \
  -d '{"temp_token": "'"$TEMP_TOKEN"'", "otp_code": "000000"}' | python -m json.tool | grep access_token | cut -d'"' -f4)

# Use access token
curl -X GET http://localhost:8001/api/v1/auth/me -H "Authorization: Bearer $ACCESS_TOKEN"
```

**Using Swagger UI**:

1. Open http://localhost:8001/docs
2. Click "Authorize" button
3. Enter token: `Bearer $ACCESS_TOKEN`
4. Test endpoints

### 7.5. Development Workflow

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
   # Service container auto-reloads on code changes

   # Check logs to make sure container is reloaded without errors on code change
   docker compose logs -f auth-api

   # If the container does not reload, restart it
   docker compose restart auth-api
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

## 8. COMMON TASKS

### 8.1. Adding a New API Endpoint

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
curl -X GET http://localhost:8001/api/v1/users/profile \
  -H "Authorization: Bearer $ACCESS_TOKEN"
```

### 8.2. Adding a New Database Table

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

### 8.3. Adding MFA to a User Account

**Via API**:

```bash
# 1. Login
TOKEN=$(curl -s -X POST http://localhost:8001/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@example.com","password":"admin123"}' \
  | jq -r '.temp_token')

# 2. Setup MFA (get QR code)
curl -X POST http://localhost:8001/api/v1/auth/mfa/setup \
  -H "Authorization: Bearer $TOKEN"

# 3. Scan QR code with Google Authenticator

# 4. Enable MFA with first OTP
curl -X POST http://localhost:8001/api/v1/auth/mfa/enable \
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

### 8.4. Debugging Login Issues

**Check logs**:

```bash
docker compose logs -f auth-api | grep -i "login\|error"
```

**Test login endpoint**:

```bash
curl -v -X POST http://localhost:8001/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@example.com","password":"admin123"}'
```

**Common issues**:

- **401 Unauthorized**: Wrong password or email
- **423 Locked**: Account locked after 5 failed attempts
- **MFA required**: User has MFA enabled, need to verify OTP

### 8.5. Resetting User Password (Admin)

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
curl -X POST http://localhost:8001/api/v1/users/{user_id}/reset-password \
  -H "Authorization: Bearer ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"new_password":"NewPassword123"}'
```

---

## 9. TROUBLESHOOTING

### 9.1. Service Won't Start

**Symptom**: `docker compose up` fails or service unhealthy

**Check**:

```bash
# View logs
docker compose logs auth-api

# Common issues:
# 1. Port already in use
netstat -ano | findstr :8001

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

### 9.2. Database Connection Error

**Symptom**: `Connection refused` or `Access denied`

**Check connection**:

```bash
# Test MySQL connection
docker exec -it mysql mysql -uofficework_dbu -p$(cat .secrets/mysql_user_passwd.txt) -e "SHOW DATABASES;"

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

### 9.3. OTP Not Working

**Symptom**: OTP codes don't match

**Solution**: See [FIX_OTP_GUIDE.md](FIX_OTP_GUIDE.md)

**Quick fix (Development only)**:

```bash
# Disable MFA for user
curl -X POST "http://localhost:8088/api/v1/auth/debug/disable-mfa?email=admin@example.com"
```

### 9.4. Migration Conflicts

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

### 9.5. Frontend Can't Connect to API

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

### 9.6. Docker Out of Space

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

- [README.md](README.md) - Project README
- Các tài liệu liên quan đến việc triển khai hệ thống và báo cáo có trong thư mục `./docs/deliveries`
- [SPRINT_1_2_VERIFICATION_REPORT.md](docs/deliveries/SPRINT_1_2_VERIFICATION_REPORT.md) - Sprint 1-2 verification
- [SPRINT_3_QUICK_REFERENCE.md](docs/deliveries/SPRINT_3_QUICK_REFERENCE.md) - Sprint 3 quick reference
- **[CQRS_AND_MONGODB_INTEGRATION_REPORT.md](docs/deliveries/CQRS_AND_MONGODB_INTEGRATION_REPORT.md)** - **NEW: CQRS implementation details**

### Memory Files (Claude Code)

- `project_overview` - Project summary
- `tech_stack` - Technology stack details
- `code_style_and_conventions` - Coding standards
- `design_patterns_and_guidelines` - Architecture patterns
- `codebase_structure` - Directory structure
- `task_completion_checklist` - Task checklist

### API Documentation (Interactive)

- Auth API: http://localhost:8001/docs
- Asset API: http://localhost:8002/docs

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
   Check current status in Section 6.1"
   ```

3. **Tham khảo các tài liệu cụ thể**:
   - Các tài liệu được nêu trong [📖 TÀI LIỆU THAM KHẢO](#-tài-liệu-tham-khảo) bên trên.
   - Section 7: Code style
   - Section 11: Common tasks

### Cập nhật file này:

**Khi có thay đổi lớn**:

- Sprint mới hoàn thành → Update Section 6.1
- Service mới deploy → Update các tài liệu `03. System_Architecture.md` và `05. API_Specification.md`, và section 6.2
- Breaking changes → Update toàn bộ sections và các tài liệu liên quan
- Bugs mới → Update Section 9

**Ai cập nhật**: Tech Lead hoặc AI assistant (với xác nhận)

---

## ✅ CHECKLIST KHI LÀM VIỆC

### Before Starting Work

- [ ] Đọc CLAUDE.md sections liên quan
- [ ] Check current sprint status (Section 6.1)
- [ ] Verify services are running (`docker compose ps`)
- [ ] Review các tài liệu liên quan
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
