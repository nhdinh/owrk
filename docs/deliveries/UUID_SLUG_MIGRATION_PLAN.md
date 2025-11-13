# UUID và Slug Migration Plan

## Tổng Quan

Tài liệu này mô tả kế hoạch migration từ Integer ID sang UUID + Slug cho toàn bộ hệ thống.

**Ngày tạo**: 2025-11-13
**Trạng thái**: Draft
**Tác động**: Breaking change - Yêu cầu rebuild database

---

## 1. Lý Do Migration

### Vấn Đề Hiện Tại
- **Integer ID**: Dễ đoán, không an toàn cho public URLs
- **Không có slug**: URLs không SEO-friendly (ví dụ: `/users/123` thay vì `/users/admin-user`)
- **Security**: ID tuần tự tiết lộ thông tin về số lượng records

### Lợi Ích UUID + Slug
- **UUID**:
  - Globally unique, không thể đoán
  - An toàn hơn cho public APIs
  - Dễ dàng merge data từ nhiều nguồn
- **Slug**:
  - URL thân thiện: `/users/admin-user` thay vì `/users/abc123...`
  - SEO-friendly
  - Human-readable

---

## 2. Thiết Kế Technical

### 2.1. UUID Format

```python
# Lưu trữ: CHAR(32) - không có dashes
id = "a1b2c3d4e5f6789012345678901234567890"

# Display: với dashes (UUID standard format)
id = "a1b2c3d4-e5f6-7890-1234-567890123456"
```

**Lý do CHAR(32) thay vì CHAR(36)**:
- Tiết kiệm 4 bytes per row
- Dashes không cần thiết cho storage
- Có thể format lại khi cần display

### 2.2. Slug Format

```python
# Rules:
- Lowercase only
- ASCII characters (a-z, 0-9, hyphen)
- Max 100 characters
- Unique per table
- Auto-generate from name/title fields

# Examples:
"Nguyễn Văn A" → "nguyen-van-a"
"Admin User" → "admin-user"
"iPhone 15 Pro Max" → "iphone-15-pro-max"
```

### 2.3. Base Model Schema

```python
class Base(SQLAlchemyBase):
    __abstract__ = True

    # Primary Key: UUID (CHAR(32))
    id = Column(String(32), primary_key=True, default=generate_uuid)

    # Slug: URL-friendly identifier
    slug = Column(String(100), unique=True, index=True, nullable=False)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
```

---

## 3. Migration Strategy

### 3.1. Phương Án 1: Fresh Start (Recommended for Development)

**Ưu điểm**:
- Đơn giản, nhanh chóng
- Không có data migration complexity
- Schema sạch, không có legacy fields

**Nhược điểm**:
- Mất toàn bộ dữ liệu hiện tại
- Phải setup lại seed data

**Quy trình**:
```bash
# 1. Backup current data (nếu cần)
docker exec mysql mysqldump -u root -p officework > backup_$(date +%Y%m%d).sql

# 2. Drop all databases
docker exec -it mysql mysql -u root -p
DROP DATABASE auth_db;
DROP DATABASE asset_db;
DROP DATABASE admin_db;
CREATE DATABASE auth_db;
CREATE DATABASE asset_db;
CREATE DATABASE admin_db;

# 3. Update models to use UUID + Slug

# 4. Create new migrations
cd services/auth-api
alembic revision --autogenerate -m "Initial schema with UUID and slug"
alembic upgrade head

# 5. Seed data with new UUIDs
python scripts/seed_data.py
```

### 3.2. Phương Án 2: Data Preservation Migration (For Production)

**Ưu điểm**:
- Giữ lại dữ liệu hiện tại
- Có thể rollback

**Nhược điểm**:
- Phức tạp hơn nhiều
- Tốn thời gian
- Cần downtime

**Quy trình**:
```sql
-- Step 1: Add new UUID columns (không phải PK yet)
ALTER TABLE users
ADD COLUMN uuid CHAR(32) NOT NULL,
ADD COLUMN slug VARCHAR(100) NOT NULL;

-- Step 2: Populate UUID và slug cho existing data
UPDATE users SET
    uuid = UUID_TO_BIN(UUID(), 1),
    slug = LOWER(CONCAT('user-', id, '-', REPLACE(REPLACE(email, '@', '-'), '.', '-')));

-- Step 3: Create new table with UUID as PK
CREATE TABLE users_new (
    id CHAR(32) PRIMARY KEY,
    slug VARCHAR(100) UNIQUE NOT NULL,
    email VARCHAR(255),
    -- ... other columns
    INDEX(slug)
);

-- Step 4: Copy data với UUID mapping
INSERT INTO users_new SELECT uuid as id, slug, email, ... FROM users;

-- Step 5: Update foreign keys (phức tạp - cần script)

-- Step 6: Rename tables
RENAME TABLE users TO users_old, users_new TO users;

-- Step 7: Verify và drop old table
DROP TABLE users_old;
```

---

## 4. Implementation Plan

### Phase 1: Preparation (1-2 days)
- [ ] Create utility functions (generate_uuid, generate_slug)
- [ ] Update Base models
- [ ] Write unit tests for slug generation
- [ ] Document breaking changes

### Phase 2: Backend Migration (2-3 days)

#### Auth Service
- [ ] Update `app/models/base.py`
- [ ] Update `app/models/user.py` - add slug generation from email
- [ ] Update `app/models/role.py` - add slug generation from name
- [ ] Update repositories to use UUID
- [ ] Update endpoints to accept UUID/slug
- [ ] Update Pydantic schemas

#### Asset Service
- [ ] Update `app/models/base.py`
- [ ] Update `app/models/asset.py` - add slug generation from asset_code
- [ ] Update `app/models/asset_category.py` - add slug generation
- [ ] Update repositories
- [ ] Update endpoints
- [ ] Update schemas

#### Admin Service
- [ ] Update models
- [ ] Update endpoints
- [ ] Update schemas

### Phase 3: Database Migration (1 day)
- [ ] Create Alembic migrations for all services
- [ ] Test migrations in development
- [ ] Create rollback scripts
- [ ] Backup production data (if applicable)

### Phase 4: Frontend Updates (2-3 days)
- [ ] Update API clients to use UUID
- [ ] Update route parameters (`:id` still works with UUID)
- [ ] Update display logic
- [ ] Add slug-based URLs where appropriate
- [ ] Test all CRUD operations

### Phase 5: Testing (2 days)
- [ ] Unit tests for UUID/slug utilities
- [ ] Integration tests for all endpoints
- [ ] End-to-end tests
- [ ] Performance testing (UUID vs Integer comparison)

### Phase 6: Documentation (1 day)
- [ ] Update API documentation
- [ ] Update CLAUDE.md
- [ ] Create migration runbook
- [ ] Update README files

**Total Estimated Time**: 9-12 days

---

## 5. Code Examples

### 5.1. Utility Functions

```python
# app/core/utils.py

import uuid
import re
from unidecode import unidecode

def generate_uuid() -> str:
    """Generate UUID without dashes"""
    return uuid.uuid4().hex

def generate_slug(text: str, max_length: int = 100) -> str:
    """Generate URL-friendly slug"""
    text = unidecode(text)  # Vietnamese → ASCII
    text = text.lower()
    text = re.sub(r'[\s_]+', '-', text)
    text = re.sub(r'[^a-z0-9-]', '', text)
    text = re.sub(r'-+', '-', text)
    return text.strip('-')[:max_length]
```

### 5.2. Updated User Model

```python
class User(Base):
    __tablename__ = "users"
    __table_args__ = {'schema': 'auth_db'}

    # Inherited from Base:
    # id = Column(String(32), primary_key=True)
    # slug = Column(String(100), unique=True, index=True)

    email = Column(String(255), unique=True, index=True, nullable=False)
    full_name = Column(String(255), nullable=False)

    # Foreign keys now use UUID
    role_id = Column(String(32), ForeignKey('auth_db.roles.id'), nullable=True)

    def __init__(self, **kwargs):
        # Auto-generate slug from email if not provided
        if 'slug' not in kwargs and 'email' in kwargs:
            kwargs['slug'] = generate_slug(kwargs['email'].split('@')[0])
        super().__init__(**kwargs)
```

### 5.3. Updated API Endpoints

```python
# Before:
@router.get("/users/{user_id}", response_model=UserResponse)
async def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    # ...

# After (supports both UUID and slug):
@router.get("/users/{user_identifier}", response_model=UserResponse)
async def get_user(
    user_identifier: str,  # Can be UUID or slug
    db: Session = Depends(get_db)
):
    # Try slug first (more human-friendly)
    user = db.query(User).filter(User.slug == user_identifier).first()

    # Fallback to UUID
    if not user and is_valid_uuid(user_identifier):
        user = db.query(User).filter(User.id == user_identifier).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user
```

### 5.4. Frontend Usage

```typescript
// URLs can use either UUID or slug
GET /api/v1/users/admin-user          // ✅ Slug (recommended)
GET /api/v1/users/a1b2c3d4...         // ✅ UUID (works)

// Response includes both
{
  "id": "a1b2c3d4e5f67890...",        // UUID
  "slug": "admin-user",                 // Slug
  "email": "admin@example.com",
  "full_name": "Admin User"
}

// Links can use slug for better UX
<Link to={`/users/${user.slug}`}>     // Preferred
<Link to={`/users/${user.id}`}>       // Also works
```

---

## 6. Breaking Changes

### API Changes
- ❌ `/users/123` (integer) → ✅ `/users/admin-user` or `/users/abc123...`
- All `id` fields now return string (UUID) instead of integer
- Foreign key references are now UUID strings

### Database Schema
- All primary keys: `INTEGER` → `CHAR(32)`
- All foreign keys: `INTEGER` → `CHAR(32)`
- New field: `slug VARCHAR(100) UNIQUE NOT NULL`

### Client Code
```typescript
// Before:
interface User {
  id: number;
  role_id: number;
}

// After:
interface User {
  id: string;      // UUID
  slug: string;    // URL-friendly
  role_id: string; // UUID reference
}
```

---

## 7. Rollback Plan

### If Migration Fails

**Option 1: Restore from backup**
```bash
# Restore database from backup
docker exec -i mysql mysql -u root -p officework < backup_20251113.sql

# Revert code changes
git revert <commit-hash>

# Restart services
docker compose restart
```

**Option 2: Keep old tables**
```sql
-- Keep old tables as backup during migration
RENAME TABLE users TO users_old;
-- ... migration ...
-- If success: DROP TABLE users_old
-- If fail: RENAME TABLE users_old TO users
```

---

## 8. Performance Considerations

### UUID vs Integer Performance

**Storage**:
- Integer: 4 bytes
- UUID (CHAR(32)): 32 bytes
- **Impact**: ~8x storage increase for ID fields

**Index Performance**:
- UUID: Slightly slower than integer for joins (not significant for most use cases)
- Slug index: Fast lookups, similar to varchar index

**Recommendations**:
- Use appropriate indexes on UUID fields
- Use slug for user-facing URLs (better caching)
- Keep UUID for API internal operations

### Benchmarks (Expected)

```
Integer PK JOIN:    0.001ms
UUID PK JOIN:       0.002ms  (2x slower, but negligible)
Slug lookup:        0.001ms  (with index)
```

---

## 9. Testing Checklist

### Unit Tests
- [ ] UUID generation is unique
- [ ] Slug generation handles Vietnamese characters
- [ ] Slug handles special characters
- [ ] Slug collision handling
- [ ] UUID validation

### Integration Tests
- [ ] Create with auto-generated UUID
- [ ] Create with auto-generated slug
- [ ] Fetch by UUID
- [ ] Fetch by slug
- [ ] Update operations
- [ ] Delete operations
- [ ] Foreign key constraints work

### End-to-End Tests
- [ ] User registration → UUID assigned
- [ ] Login works with UUID-based users
- [ ] Asset creation with UUID references
- [ ] All frontend pages load correctly
- [ ] Navigation with slug URLs works

---

## 10. Dependencies

### Python Packages (Add to requirements.txt)
```txt
# Already installed:
# uuid (built-in)
# sqlalchemy (already installed)

# Need to add:
unidecode==1.3.8    # For Vietnamese → ASCII conversion
```

### Database
- MySQL 8.0+ (already using)
- Ensure CHAR(32) support
- Ensure VARCHAR(100) UNIQUE support

---

## 11. Next Steps

### Immediate Actions (Today)
1. Review this plan with team
2. Decide on migration approach (Fresh Start vs Data Preservation)
3. Create backup of current database
4. Install required dependencies

### Tomorrow
1. Implement utility functions
2. Update Base models
3. Create unit tests

### This Week
1. Complete backend migration
2. Run database migrations
3. Update frontend code
4. Comprehensive testing

---

## 12. Questions & Decisions Needed

- [ ] **Fresh start** or **data preservation**?
- [ ] Slug format preferences? (current: lowercase-with-dashes)
- [ ] Slug max length? (current: 100 characters)
- [ ] UUID format in URLs? (with or without dashes?)
- [ ] Performance benchmarks needed?
- [ ] Production migration downtime window?

---

**Document Owner**: Claude AI + Hung Dinh
**Last Updated**: 2025-11-13
**Status**: Awaiting approval
