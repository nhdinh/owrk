# UUID Migration Implementation Guide

**Date**: 2025-11-13
**Status**: In Progress
**Method**: Fresh Start (Drop and Recreate)

---

## ✅ Completed Steps

### 1. Utilities Created
- ✅ Created `app/core/utils.py` in all services (auth-api, asset-api, admin-api)
- ✅ Functions: `generate_uuid()`, `generate_slug()`, `ensure_unique_slug()`, `is_valid_uuid()`, `format_uuid()`

### 2. Dependencies Installed
- ✅ Added `unidecode==1.3.8` to requirements.txt for all API services

### 3. Base Models Updated
- ✅ `services/auth-api/app/models/base.py` - UUID + slug
- ✅ `services/asset-api/app/models/base.py` - UUID + slug
- ✅ `services/admin-api/app/models/base.py` - UUID + slug

### 4. User Model Updated (Partial)
- ✅ Updated foreign keys to use UUID
- ✅ Added slug auto-generation event listener

---

## 🚧 Remaining Tasks

### Phase 1: Complete Model Updates

#### Auth Service Models
- [x] `user.py` - Partial (needs foreign key updates for all relationships)
- [ ] `role.py` - Update all FKs, add slug generation
- [ ] `refresh_token.py` - Update user_id FK
- [ ] `password_reset_token.py` - Update user_id FK
- [ ] `user_history.py` - Update user_id FK

#### Asset Service Models
- [ ] `asset.py` - Update all FKs, add slug generation from asset_code
- [ ] `asset_category.py` - Add slug generation from name
- [ ] `asset_assignment.py` - Update asset_id, user_id FKs
- [ ] `asset_attachment.py` - Update asset_id FK
- [ ] `asset_depreciation_record.py` - Update asset_id FK

#### Admin Service Models
- [ ] `module_settings.py` - Update module_id FK
- [ ] `system_modules.py` - Add slug generation
- [ ] `trash_items.py` - Update referenced_id (now UUID)
- [ ] `audit_logs.py` - Update user_id, entity_id FKs

### Phase 2: Drop and Recreate Databases

```bash
# Backup current data (optional)
docker exec mysql mysqldump -u root -p officework > backup_$(date +%Y%m%d).sql

# Drop databases
docker exec -it mysql mysql -u root -p
```

```sql
DROP DATABASE IF EXISTS auth_db;
DROP DATABASE IF EXISTS asset_db;
DROP DATABASE IF EXISTS admin_db;

CREATE DATABASE auth_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE DATABASE asset_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE DATABASE admin_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### Phase 3: Create New Alembic Migrations

```bash
# Auth API
cd services/auth-api
rm -rf alembic/versions/*  # Clear old migrations
alembic revision --autogenerate -m "Initial schema with UUID and slug"
alembic upgrade head

# Asset API
cd services/asset-api
rm -rf alembic/versions/*
alembic revision --autogenerate -m "Initial schema with UUID and slug"
alembic upgrade head

# Admin API
cd services/admin-api
rm -rf alembic/versions/*
alembic revision --autogenerate -m "Initial schema with UUID and slug"
alembic upgrade head
```

### Phase 4: Update Pydantic Schemas

All response models need to update `id` fields from `int` to `str`:

```python
# Before:
class UserResponse(BaseModel):
    id: int
    role_id: Optional[int]

# After:
class UserResponse(BaseModel):
    id: str  # UUID
    slug: str
    role_id: Optional[str]  # UUID reference
```

### Phase 5: Update API Endpoints

Support both UUID and slug in path parameters:

```python
# Example endpoint update
@router.get("/users/{user_identifier}")
async def get_user(
    user_identifier: str,  # Can be UUID or slug
    db: Session = Depends(get_db)
):
    # Try slug first
    user = db.query(User).filter(User.slug == user_identifier).first()

    # Fallback to UUID
    if not user and is_valid_uuid(user_identifier):
        user = db.query(User).filter(User.id == user_identifier).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user
```

### Phase 6: Create Seed Data Script

```python
# scripts/seed_data.py
from app.core.utils import generate_uuid
from app.models.user import User
from app.models.role import Role

# Create admin role
admin_role = Role(
    id=generate_uuid(),
    slug="admin",
    name="admin",
    display_name="Administrator",
    description="Full system access"
)

# Create admin user
admin_user = User(
    id=generate_uuid(),
    slug="admin",
    email="admin@example.com",
    username="admin",
    full_name="Admin User",
    hashed_password="...",
    role_id=admin_role.id,
    is_active=True,
    is_superuser=True
)
```

### Phase 7: Frontend Updates

Update TypeScript interfaces:

```typescript
// types/auth.ts
export interface User {
  id: string;      // Was: number
  slug: string;    // NEW
  email: string;
  full_name: string;
  role_id: string; // Was: number
  role?: Role;
}

export interface Role {
  id: string;      // Was: number
  slug: string;    // NEW
  name: string;
  display_name: string;
}
```

Update API calls:

```typescript
// Before:
const user = await api.get(`/users/${userId}`);

// After (prefer slug):
const user = await api.get(`/users/${userSlug}`); // or UUID still works
```

---

## 📝 Model-Specific Slug Generation

### User Model
```python
# Slug from: username > email prefix
slug = username or email.split('@')[0]
# Example: "admin" or "john-doe"
```

### Role Model
```python
# Slug from: name
slug = name
# Example: "admin", "user", "manager"
```

### Asset Model
```python
# Slug from: asset_code
slug = asset_code
# Example: "laptop-001", "iphone-15-pro"
```

### Asset Category Model
```python
# Slug from: name
slug = name
# Example: "laptops", "phones", "furniture"
```

---

## 🧪 Testing Checklist

### Unit Tests
- [ ] Test UUID generation uniqueness
- [ ] Test slug generation from Vietnamese text
- [ ] Test slug generation from special characters
- [ ] Test slug collision handling
- [ ] Test UUID validation

### Integration Tests
- [ ] Create user with auto UUID/slug
- [ ] Fetch user by UUID
- [ ] Fetch user by slug
- [ ] Create asset with relationships
- [ ] Foreign key constraints work
- [ ] Cascade deletes work

### API Tests
- [ ] POST /users - returns UUID
- [ ] GET /users/{uuid} - works
- [ ] GET /users/{slug} - works
- [ ] PUT /users/{uuid} - works
- [ ] DELETE /users/{uuid} - works
- [ ] Relationships load correctly

---

## 🔄 Migration Script (Quick Reference)

```bash
#!/bin/bash
# Quick migration script

echo "=== UUID Migration Script ==="

# 1. Install dependencies
echo "Installing dependencies..."
docker compose exec auth-api pip install unidecode
docker compose exec asset-api pip install unidecode
docker compose exec admin-api pip install unidecode

# 2. Drop databases
echo "Dropping databases..."
docker exec -it mysql mysql -u root -p -e "
DROP DATABASE IF EXISTS auth_db;
DROP DATABASE IF EXISTS asset_db;
DROP DATABASE IF EXISTS admin_db;
CREATE DATABASE auth_db;
CREATE DATABASE asset_db;
CREATE DATABASE admin_db;
"

# 3. Run migrations
echo "Running migrations..."
docker compose exec auth-api alembic upgrade head
docker compose exec asset-api alembic upgrade head
docker compose exec admin-api alembic upgrade head

# 4. Seed data
echo "Seeding data..."
docker compose exec auth-api python scripts/seed_data.py

echo "=== Migration Complete ==="
```

---

## ⚠️ Important Notes

1. **This is a breaking change** - All existing data will be lost
2. **Backup first** if you have important data
3. **Update all foreign keys** to use CHAR(32) instead of INTEGER
4. **Update all schemas** - id fields must be strings
5. **Update frontends** - TypeScript interfaces must use string for IDs
6. **Slug must be unique** per table - add unique constraint
7. **Test thoroughly** before deploying to production

---

## 📋 Files Modified

### Core Files
- `services/auth-api/app/core/utils.py` ✅
- `services/asset-api/app/core/utils.py` ✅
- `services/admin-api/app/core/utils.py` ✅

### Base Models
- `services/auth-api/app/models/base.py` ✅
- `services/asset-api/app/models/base.py` ✅
- `services/admin-api/app/models/base.py` ✅

### Entity Models (Partial)
- `services/auth-api/app/models/user.py` ⏳ (in progress)
- All other models - ⏸️ pending

### Requirements
- `services/auth-api/requirements.txt` ✅
- `services/asset-api/requirements.txt` ✅
- `services/admin-api/requirements.txt` ✅

---

## 🎯 Next Steps

1. **Complete all model updates** (User, Role, Asset, etc.)
2. **Drop and recreate databases**
3. **Generate new Alembic migrations**
4. **Update Pydantic schemas**
5. **Update API endpoints**
6. **Create seed data script**
7. **Update frontend TypeScript types**
8. **Test all CRUD operations**
9. **Update documentation**

---

**Estimated Time Remaining**: 4-6 hours
**Current Progress**: ~30% complete
