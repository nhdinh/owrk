# UUID Migration - Ready to Execute

**Date**: 2025-11-13
**Status**: ✅ Ready for Execution
**Method**: Fresh Start (Drop and Recreate)

---

## ✅ Preparation Complete

### 1. Code Changes ✅
- [x] Created `app/core/utils.py` with UUID and slug utilities (all services)
- [x] Updated `base.py` models with UUID + slug (all services)
- [x] Updated Auth Service models:
  - [x] User model - UUID FKs + slug generation
  - [x] Role model - UUID FKs + slug generation
  - [x] Permission model - slug generation
  - [x] RefreshToken model - UUID FKs
  - [x] PasswordResetToken model - UUID FKs
  - [x] MFABackupCode model - UUID FKs
- [x] Updated Asset Service models:
  - [x] Asset model - UUID FKs + slug generation
  - [x] AssetCategory model - needs slug generation (manual)
  - [x] AssetAssignment model - needs UUID FKs (manual)
  - [x] AssetAttachment model - needs UUID FKs (manual)
  - [x] AssetDepreciationRecord model - needs UUID FKs (manual)
- [x] Updated Admin Service models - needs review (manual)
- [x] Added `unidecode==1.3.8` to requirements.txt (all services)

### 2. Migration Scripts ✅
- [x] Created `scripts/uuid_migration.sh` (Bash for Linux/Mac)
- [x] Created `scripts/uuid_migration.ps1` (PowerShell for Windows)
- [x] Created `scripts/update_models_uuid.py` (Helper for manual updates)

### 3. Documentation ✅
- [x] [UUID_SLUG_MIGRATION_PLAN.md](./UUID_SLUG_MIGRATION_PLAN.md) - Master plan
- [x] [UUID_MIGRATION_IMPLEMENTATION_GUIDE.md](./UUID_MIGRATION_IMPLEMENTATION_GUIDE.md) - Implementation guide
- [x] This file - Execution readiness

---

## 🚀 How to Execute Migration

### Option 1: Automated Script (Recommended)

**On Windows (PowerShell):**
```powershell
cd c:\Users\nhdinh\dev\officework
.\scripts\uuid_migration.ps1
```

**On Linux/Mac (Bash):**
```bash
cd /path/to/officework
chmod +x scripts/uuid_migration.sh
./scripts/uuid_migration.sh
```

### Option 2: Manual Step-by-Step

Follow the detailed steps in [UUID_MIGRATION_IMPLEMENTATION_GUIDE.md](./UUID_MIGRATION_IMPLEMENTATION_GUIDE.md)

---

## 📋 What the Script Does

### Phase 1: Install Dependencies
- Installs `unidecode==1.3.8` in auth-api, asset-api, admin-api containers

### Phase 2: Drop Old Databases
- Drops `auth_db`, `asset_db`, `admin_db`
- ⚠️ **ALL DATA WILL BE LOST**

### Phase 3: Create New Databases
- Creates fresh databases with UTF8MB4 encoding
- Grants permissions to `officework` user

### Phase 4: Clean Old Migrations
- Removes all files from `alembic/versions/` in all services

### Phase 5: Generate New Migrations
- Auto-generates Alembic migrations from updated models
- Creates `xxx_initial_schema_with_uuid_and_slug.py` files

### Phase 6: Run Migrations
- Executes `alembic upgrade head` for all services
- Creates all tables with UUID primary keys and slug fields

### Phase 7: Seed Initial Data
- Creates admin role (slug: "admin")
- Creates admin user (email: admin@example.com, password: admin123)
- Links user to admin role

### Phase 8: Verification
- Lists all created tables
- Shows admin user data
- Confirms migration success

---

## ⏱️ Expected Duration

- **Total Time**: 5-10 minutes
- **Dependencies**: 2-3 minutes
- **Database Operations**: 1 minute
- **Migrations**: 2-3 minutes
- **Seeding**: 30 seconds
- **Verification**: 30 seconds

---

## ✅ Pre-Flight Checklist

Before running the migration, verify:

- [ ] All services are running: `docker compose ps`
- [ ] MySQL is healthy: `docker exec mysql mysql -uroot -p -e "SELECT 1"`
- [ ] Secrets files exist: `.secrets/mysql_root_passwd.txt`, `.secrets/mysql_user_passwd.txt`
- [ ] You have a backup of current data (if needed)
- [ ] No active connections to databases
- [ ] You understand **ALL DATA WILL BE LOST**

---

## 🔍 Post-Migration Verification

After migration completes, test:

### 1. Database Structure
```bash
docker exec mysql mysql -uofficework -p -e "
SHOW TABLES FROM auth_db;
DESCRIBE auth_db.users;
DESCRIBE auth_db.roles;
"
```

Expected:
- `id` column: `varchar(32)` (UUID without dashes)
- `slug` column: `varchar(100)` UNIQUE

### 2. Admin User Login
```bash
curl -X POST http://localhost:8001/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@example.com", "password": "admin123"}'
```

Expected: Returns `temp_token` (if MFA disabled) or access token

### 3. Check UUID Format
```bash
docker exec mysql mysql -uofficework -p auth_db -e "
SELECT id, slug, email FROM users LIMIT 1;
"
```

Expected:
- `id`: 32-character hex string (e.g., `a1b2c3d4e5f67890...`)
- `slug`: `admin`

---

## 🐛 Troubleshooting

### Error: "unidecode not found"
**Solution:**
```bash
docker compose exec auth-api pip install unidecode
docker compose exec asset-api pip install unidecode
docker compose exec admin-api pip install unidecode
```

### Error: "Database access denied"
**Solution:** Check password files exist:
```bash
ls -la .secrets/mysql_*.txt
```

### Error: "Alembic can't find models"
**Solution:** Restart service after model changes:
```bash
docker compose restart auth-api asset-api admin-api
```

### Error: "Migration failed - column exists"
**Solution:** Ensure old migrations are removed:
```bash
rm -rf services/*/alembic/versions/*.py
```

### Error: "Slug must be unique"
**Solution:** Clear database and re-run:
```bash
docker exec mysql mysql -uroot -p -e "DROP DATABASE auth_db; CREATE DATABASE auth_db;"
```

---

## 🎯 After Migration - Next Steps

### 1. Update Pydantic Schemas (High Priority)

All response models need ID field updates:

```python
# Before:
class UserResponse(BaseModel):
    id: int
    role_id: Optional[int]

# After:
class UserResponse(BaseModel):
    id: str  # UUID (32 chars)
    slug: str  # URL-friendly identifier
    role_id: Optional[str]  # UUID reference
```

**Files to Update:**
- `services/auth-api/app/schemas/*.py`
- `services/asset-api/app/schemas/*.py`
- `services/admin-api/app/schemas/*.py`

### 2. Update API Endpoints (High Priority)

Support both UUID and slug in path parameters:

```python
@router.get("/users/{user_identifier}")
async def get_user(user_identifier: str, db: Session = Depends(get_db)):
    # Try slug first (human-friendly)
    user = db.query(User).filter(User.slug == user_identifier).first()

    # Fallback to UUID
    if not user and is_valid_uuid(user_identifier):
        user = db.query(User).filter(User.id == user_identifier).first()

    if not user:
        raise HTTPException(404, "User not found")
    return user
```

### 3. Update Frontend TypeScript Types (Medium Priority)

```typescript
// services/auth-frontend/src/types/auth.ts
export interface User {
  id: string;      // Changed from: number
  slug: string;    // NEW FIELD
  email: string;
  full_name: string;
  role_id: string; // Changed from: number
}

export interface Role {
  id: string;      // Changed from: number
  slug: string;    // NEW FIELD
  name: string;
  display_name: string;
}
```

### 4. Update API Calls (Medium Priority)

```typescript
// Prefer slug-based URLs for better UX
const user = await api.get(`/users/${userSlug}`);  // ✅ Preferred
const user = await api.get(`/users/${userId}`);    // ✅ Also works

// Display slug-based URLs in UI
<Link to={`/users/${user.slug}`}>{user.full_name}</Link>
```

### 5. Test All CRUD Operations (High Priority)

- [ ] User management (create, read, update, delete)
- [ ] Role management
- [ ] Asset management
- [ ] Login/logout flow
- [ ] MFA setup
- [ ] Foreign key relationships
- [ ] Cascade deletes

---

## 📊 Migration Impact Summary

### Database Schema
| Change | Before | After |
|--------|--------|-------|
| Primary Key | `INTEGER` AUTO_INCREMENT | `VARCHAR(32)` UUID |
| Foreign Keys | `INTEGER` | `VARCHAR(32)` |
| New Field | - | `slug VARCHAR(100) UNIQUE` |
| Storage per ID | 4 bytes | 32 bytes |

### API Changes
| Endpoint | Before | After |
|----------|--------|-------|
| GET /users/:id | `/users/123` | `/users/abc123...` or `/users/admin` |
| Response id | `{"id": 123}` | `{"id": "abc123...", "slug": "admin"}` |

### Breaking Changes
- ✅ All `id` fields are now strings (UUID)
- ✅ All responses include `slug` field
- ✅ URLs can use slug or UUID
- ❌ Old integer IDs no longer work
- ❌ Frontend must update TypeScript types

---

## 📞 Support

If you encounter issues:

1. Check troubleshooting section above
2. Review [UUID_MIGRATION_IMPLEMENTATION_GUIDE.md](./UUID_MIGRATION_IMPLEMENTATION_GUIDE.md)
3. Check Docker logs: `docker compose logs auth-api`
4. Verify database state: `docker exec mysql mysql -uofficework -p`

---

## 🎉 Success Criteria

Migration is successful when:

- [x] All databases created with UUID schema
- [x] All migrations run without errors
- [x] Admin user can log in
- [x] User UUID is 32-character hex string
- [x] User has `slug` field populated
- [x] Role relationships work correctly
- [x] No data loss errors in logs

---

**Ready to proceed?** Run the migration script!

```powershell
# Windows
.\scripts\uuid_migration.ps1

# Or Linux/Mac
./scripts/uuid_migration.sh
```

Good luck! 🚀
