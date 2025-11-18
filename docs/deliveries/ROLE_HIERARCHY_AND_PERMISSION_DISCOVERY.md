# Role Hierarchy & Permission Discovery Implementation

**Date**: 2025-11-18
**Status**: ✅ Implemented (Role Hierarchy) | 🚧 Planned (Permission Discovery)
**Services**: auth-api, all microservices

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Role Hierarchy Protection](#role-hierarchy-protection)
3. [Permission Discovery Architecture](#permission-discovery-architecture)
4. [Database Changes](#database-changes)
5. [API Changes](#api-changes)
6. [Implementation Status](#implementation-status)
7. [Testing Guide](#testing-guide)

---

## 1. Overview

### Problem Statement

**Security Concerns:**
1. Lower-privilege users (e.g., Manager) could modify higher-privilege users (e.g., Admin)
2. Users could assign roles with higher privileges than their own
3. Permissions were hardcoded in auth-api without service ownership

**Solution:**
1. **Role Hierarchy Protection**: Prevent lower-privilege users from manipulating higher-privilege users
2. **Permission Discovery**: Each microservice declares its own permissions, auth-api aggregates them

---

## 2. Role Hierarchy Protection

### Architecture

**Hierarchy Levels:**
- `Super Admin`: 100 (highest)
- `Admin`: 90
- `Manager`: 50
- `User`: 10 (default)
- Custom roles: 10 (default, can be customized)

**Protection Rules:**
1. Users can only modify users with **strictly lower** hierarchy levels
2. Users can only assign roles with **lower or equal** hierarchy levels
3. Superusers (`is_superuser=True`) bypass all hierarchy checks

### Implementation

**New Model Fields:**

```python
# services/auth-api/app/models/role.py

class Role(Base):
    # ... existing fields ...

    # Hierarchy level for role-based access control
    # Higher level = more privileged
    hierarchy_level = Column(Integer, default=10, nullable=False)
```

**Authorization Helper Functions:**

```python
# services/auth-api/app/core/authorization.py

def check_role_hierarchy(current_user: User, target_user: User, operation: str) -> None:
    """
    Check if current_user has sufficient role hierarchy to perform operation on target_user.

    Raises HTTPException 403 if:
    - Current user's hierarchy level <= Target user's hierarchy level
    - Current user has no role assigned
    """

def check_role_assignment_hierarchy(current_user: User, new_role_id: str, uow) -> None:
    """
    Check if current_user can assign a specific role to another user.
    Users can only assign roles with lower or equal hierarchy to their own.

    Raises HTTPException 403 if:
    - Current user's hierarchy level <= Role's hierarchy level
    """
```

**Protected Endpoints:**

| Endpoint | Method | Operation | Hierarchy Check |
|----------|--------|-----------|-----------------|
| `/api/v1/users/{user_id}` | PUT | Update user | `check_role_hierarchy()` + `check_role_assignment_hierarchy()` (if role changes) |
| `/api/v1/users/{user_id}` | DELETE | Delete user | `check_role_hierarchy()` |
| `/api/v1/users/{user_id}/activate` | POST | Activate user | `check_role_hierarchy()` |
| `/api/v1/users/{user_id}/deactivate` | POST | Deactivate user | `check_role_hierarchy()` |

### Example Scenarios

**Scenario 1: Manager tries to edit Admin**
```
Manager (hierarchy: 50) → Edit → Admin (hierarchy: 90)
Result: ❌ 403 Forbidden
Message: "Insufficient privileges to update user with role 'Admin'.
         Your role hierarchy level (50) must be higher than theirs (90)."
```

**Scenario 2: Admin edits Manager**
```
Admin (hierarchy: 90) → Edit → Manager (hierarchy: 50)
Result: ✅ Allowed
```

**Scenario 3: Manager assigns Admin role**
```
Manager (hierarchy: 50) → Assign "Admin" role (hierarchy: 90) → User
Result: ❌ 403 Forbidden
Message: "Insufficient privileges to assign role 'Admin'.
         Your role hierarchy level (50) must be higher than the role you're assigning (90)."
```

**Scenario 4: Superuser bypasses checks**
```
Superuser → Any operation → Any user
Result: ✅ Always allowed
```

---

## 3. Permission Discovery Architecture

### Design Overview

**Distributed Permission Management:**
- Each microservice owns and declares its permissions
- Auth service discovers services via service-registry
- Auth service periodically syncs permissions from all services
- Background task runs every 5 minutes (configurable)

### Permission Format

**Each service exposes `/permissions` endpoint:**

```json
{
  "service": "asset-api",
  "version": "1.0.0",
  "permissions": [
    {
      "code": "asset:create",
      "name": "Create Assets",
      "resource": "asset",
      "action": "create",
      "description": "Create new assets in the system"
    },
    {
      "code": "asset:read",
      "name": "View Assets",
      "resource": "asset",
      "action": "read",
      "description": "View asset details"
    },
    {
      "code": "asset:update",
      "name": "Update Assets",
      "resource": "asset",
      "action": "update",
      "description": "Modify existing assets"
    },
    {
      "code": "asset:delete",
      "name": "Delete Assets",
      "resource": "asset",
      "action": "delete",
      "description": "Remove assets from the system"
    }
  ]
}
```

### Sync Flow

```
1. Auth Service Background Task (every 5 min)
   ↓
2. Fetch registered services from Service Registry
   ↓
3. For each service with `/permissions` endpoint:
   ↓
4. HTTP GET http://{service}/permissions
   ↓
5. Compare with existing permissions in database
   ↓
6. Insert new permissions, mark missing as inactive
   ↓
7. Log sync results
```

### Implementation Plan (Pending)

**Phase 1: Service Endpoints** (Each service)
- [ ] Add `/permissions` endpoint to asset-api
- [ ] Add `/permissions` endpoint to procurement-api
- [ ] Add `/permissions` endpoint to admin-api
- [ ] Add `/permissions` endpoint to dashboard-api

**Phase 2: Sync Mechanism** (auth-api)
- [ ] Create `PermissionSyncService` class
- [ ] Implement background task with APScheduler
- [ ] Add service discovery integration
- [ ] Implement permission comparison logic
- [ ] Add logging and error handling

**Phase 3: Schema Updates**
- [ ] Add `service` field to Permission model ✅ (Already done)
- [ ] Add `last_synced_at` field to Permission model
- [ ] Add `sync_status` enum field (active, inactive, deprecated)

---

## 4. Database Changes

### Migration: `0a1ccbf63ebf_add_hierarchy_level_and_service_to_`

**New Columns:**

```sql
-- Add hierarchy_level to roles
ALTER TABLE auth_db.roles
ADD COLUMN hierarchy_level INTEGER NOT NULL DEFAULT 10;

-- Add service to permissions
ALTER TABLE auth_db.permissions
ADD COLUMN service VARCHAR(50);

-- Update system roles with hierarchy levels
UPDATE auth_db.roles
SET hierarchy_level = CASE
    WHEN name = 'super_admin' THEN 100
    WHEN name = 'admin' THEN 90
    WHEN name = 'manager' THEN 50
    WHEN name = 'user' THEN 10
    ELSE 10
END
WHERE is_system_role = TRUE;
```

**Schema After Migration:**

```sql
-- roles table
CREATE TABLE auth_db.roles (
    id VARCHAR(36) PRIMARY KEY,
    slug VARCHAR(100) UNIQUE NOT NULL,
    name VARCHAR(50) UNIQUE NOT NULL,
    display_name VARCHAR(100) NOT NULL,
    description TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    is_system_role BOOLEAN DEFAULT FALSE,
    hierarchy_level INTEGER DEFAULT 10 NOT NULL,  -- NEW
    version INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- permissions table
CREATE TABLE auth_db.permissions (
    id VARCHAR(36) PRIMARY KEY,
    slug VARCHAR(100) UNIQUE NOT NULL,
    name VARCHAR(100) UNIQUE NOT NULL,
    resource VARCHAR(50) NOT NULL,
    action VARCHAR(50) NOT NULL,
    description TEXT,
    service VARCHAR(50),  -- NEW
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
```

---

## 5. API Changes

### Role Response Schema (Updated)

```json
{
  "id": "uuid-string",
  "name": "admin",
  "display_name": "Administrator",
  "description": "System administrator with full access",
  "hierarchy_level": 90,
  "is_active": true,
  "is_system_role": true,
  "permissions": [...],
  "created_at": "2025-11-18T00:00:00Z",
  "updated_at": "2025-11-18T00:00:00Z"
}
```

### Permission Response Schema (Updated)

```json
{
  "id": "uuid-string",
  "name": "Create Assets",
  "resource": "asset",
  "action": "create",
  "description": "Create new assets",
  "service": "asset-api",
  "created_at": "2025-11-18T00:00:00Z",
  "updated_at": "2025-11-18T00:00:00Z"
}
```

### New Error Responses

**403 Forbidden - Insufficient Hierarchy:**

```json
{
  "detail": "Insufficient privileges to update user with role 'Admin'. Your role hierarchy level (50) must be higher than theirs (90)."
}
```

**403 Forbidden - Cannot Assign Role:**

```json
{
  "detail": "Insufficient privileges to assign role 'Admin'. Your role hierarchy level (50) must be higher than the role you're assigning (90)."
}
```

---

## 6. Implementation Status

### ✅ Completed

**Role Hierarchy Protection:**
- [x] Add `hierarchy_level` field to Role model
- [x] Add `service` field to Permission model
- [x] Create database migration
- [x] Apply migration to database
- [x] Create authorization helper functions
- [x] Add hierarchy checks to update endpoint
- [x] Add hierarchy checks to delete endpoint
- [x] Add hierarchy checks to activate endpoint
- [x] Add hierarchy checks to deactivate endpoint
- [x] Add role assignment hierarchy check
- [x] Test with auth-api restart

### 🚧 Pending

**Permission Discovery:**
- [ ] Create `/permissions` endpoint template
- [ ] Implement in asset-api
- [ ] Implement in procurement-api
- [ ] Implement in admin-api
- [ ] Implement in dashboard-api
- [ ] Create PermissionSyncService in auth-api
- [ ] Add APScheduler background task
- [ ] Integrate with service-registry
- [ ] Add permission comparison logic
- [ ] Add sync logging
- [ ] Update frontend to show permission service ownership

---

## 7. Testing Guide

### Manual Testing - Role Hierarchy

**Prerequisites:**
1. Create test users with different roles:
   - `admin@test.com` - Admin role (hierarchy: 90)
   - `manager@test.com` - Manager role (hierarchy: 50)
   - `user@test.com` - User role (hierarchy: 10)

**Test Case 1: Manager Cannot Edit Admin**

```bash
# Login as manager
MANAGER_TOKEN=$(curl -s -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"manager@test.com","password":"password"}' \
  | jq -r '.temp_token')

# Verify OTP
MANAGER_TOKEN=$(curl -s -X POST "http://localhost:8000/api/v1/auth/verify-otp" \
  -H "Content-Type: application/json" \
  -d '{"temp_token":"'$MANAGER_TOKEN'","otp_code":"000000"}' \
  | jq -r '.access_token')

# Try to edit admin user (should fail)
curl -X PUT "http://localhost:8000/api/v1/users/{admin_user_id}" \
  -H "Authorization: Bearer $MANAGER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"full_name":"Hacked Admin"}'

# Expected: 403 Forbidden
# Message: "Insufficient privileges to update user..."
```

**Test Case 2: Admin Can Edit Manager**

```bash
# Login as admin
ADMIN_TOKEN=$(curl -s -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@test.com","password":"password"}' \
  | jq -r '.temp_token')

# Verify OTP
ADMIN_TOKEN=$(curl -s -X POST "http://localhost:8000/api/v1/auth/verify-otp" \
  -H "Content-Type: application/json" \
  -d '{"temp_token":"'$ADMIN_TOKEN'","otp_code":"000000"}' \
  | jq -r '.access_token')

# Edit manager user (should succeed)
curl -X PUT "http://localhost:8000/api/v1/users/{manager_user_id}" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"full_name":"Updated Manager"}'

# Expected: 200 OK with updated user data
```

**Test Case 3: Manager Cannot Assign Admin Role**

```bash
# Manager tries to assign Admin role to a user
curl -X PUT "http://localhost:8000/api/v1/users/{user_id}" \
  -H "Authorization: Bearer $MANAGER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"role_id":"{admin_role_id}"}'

# Expected: 403 Forbidden
# Message: "Insufficient privileges to assign role 'Admin'..."
```

**Test Case 4: Superuser Bypasses All Checks**

```bash
# Login as superuser
SUPER_TOKEN=$(curl -s -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@example.com","password":"admin123"}' \
  | jq -r '.temp_token')

# Verify OTP
SUPER_TOKEN=$(curl -s -X POST "http://localhost:8000/api/v1/auth/verify-otp" \
  -H "Content-Type: application/json" \
  -d '{"temp_token":"'$SUPER_TOKEN'","otp_code":"000000"}' \
  | jq -r '.access_token')

# Superuser can edit anyone (should succeed)
curl -X PUT "http://localhost:8000/api/v1/users/{any_user_id}" \
  -H "Authorization: Bearer $SUPER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"full_name":"Updated by Superuser"}'

# Expected: 200 OK
```

### Automated Testing

**Unit Tests** (To be implemented):

```python
# tests/test_authorization.py

def test_check_role_hierarchy_allows_higher_to_lower():
    """Admin (90) can modify Manager (50)"""
    pass

def test_check_role_hierarchy_blocks_lower_to_higher():
    """Manager (50) cannot modify Admin (90)"""
    pass

def test_check_role_hierarchy_blocks_equal():
    """Manager cannot modify another Manager"""
    pass

def test_superuser_bypasses_hierarchy():
    """Superuser can modify anyone"""
    pass

def test_check_role_assignment_hierarchy():
    """Users can only assign roles with lower hierarchy"""
    pass
```

---

## 8. Configuration

### Environment Variables

```env
# auth-api/.env

# Permission sync (future)
PERMISSION_SYNC_ENABLED=true
PERMISSION_SYNC_INTERVAL_MINUTES=5
SERVICE_REGISTRY_URL=http://service-registry:3000
```

### Role Hierarchy Levels

To customize hierarchy levels for custom roles:

```sql
-- Update custom role hierarchy
UPDATE auth_db.roles
SET hierarchy_level = 70
WHERE name = 'department_head';
```

**Recommended Levels:**
- `100-90`: System administrators
- `89-60`: Senior management
- `59-30`: Middle management
- `29-10`: Regular users
- `1-9`: Restricted/guest users

---

## 9. Security Considerations

### Best Practices

1. **Never Allow Equal Hierarchy Operations**: Users at the same level cannot modify each other
2. **Superuser Protection**: Only grant `is_superuser=True` to trusted accounts
3. **Audit Hierarchy Changes**: Log all role hierarchy modifications
4. **Regular Reviews**: Periodically review role assignments and hierarchy levels
5. **Principle of Least Privilege**: Assign the lowest hierarchy level that fulfills job requirements

### Attack Scenarios Prevented

| Attack | Prevention |
|--------|-----------|
| Privilege Escalation | Manager cannot assign Admin role to themselves or others |
| Lateral Movement | Users at same level cannot modify each other |
| Account Takeover | Lower-privilege attacker cannot modify admin accounts |
| Role Manipulation | Users cannot assign roles higher than their own |

---

## 10. Future Enhancements

### Phase 1 (Completed)
- ✅ Role hierarchy protection
- ✅ Database schema updates
- ✅ Authorization helper functions

### Phase 2 (Next Sprint)
- [ ] Permission discovery implementation
- [ ] Service permission endpoints
- [ ] Permission sync service
- [ ] Frontend UI for hierarchy levels

### Phase 3 (Future)
- [ ] Dynamic hierarchy adjustments via API
- [ ] Role delegation (temporary hierarchy elevation)
- [ ] Hierarchy-based dashboard filtering
- [ ] Permission dependency management

---

## 11. Documentation References

- [CLAUDE.md](../../CLAUDE.md) - Project overview
- [System Architecture](../03.%20System_Architecture.md) - Overall system design
- [API Specification](../05.%20API_Specification.md) - API documentation
- [Database Design](../04.%20Database_Design.md) - Database schema

---

**Generated**: 2025-11-18
**Author**: Claude AI + Hung Dinh
**Version**: 1.0
