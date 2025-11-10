# Admin Management Service

## Overview

The Admin Management Service provides centralized administration capabilities for the entire Office Equipment Asset Management System. It handles system configuration, trash/recycle bin functionality, and audit logging across all microservices.

**Version**: 1.1.0
**Port**: 8005 (API), 3500 (Frontend)
**Database**: admin_db (MySQL)
**API Documentation**: http://localhost:8005/docs

## Features

### 1. Module Settings Management ✅
Centralized configuration management for all microservices.

**Capabilities:**
- Create, read, update, delete module settings
- Type-safe settings (STRING, INTEGER, BOOLEAN, JSON)
- Public/private settings visibility
- Category organization
- Validation rules support
- Bulk update operations

**Endpoints**: 9 total
- `GET /api/v1/admin/module-settings/` - List all settings
- `GET /api/v1/admin/module-settings/module/{module_name}` - Get module settings
- `GET /api/v1/admin/module-settings/{id}` - Get specific setting
- `POST /api/v1/admin/module-settings/` - Create setting
- `PUT /api/v1/admin/module-settings/{id}` - Update setting
- `DELETE /api/v1/admin/module-settings/{id}` - Delete setting
- `GET /api/v1/admin/module-settings/public/` - Public settings
- `GET /api/v1/admin/module-settings/public/{module}` - Module public settings
- `PUT /api/v1/admin/module-settings/bulk` - Bulk update

### 2. Trash/Recycle Bin System ✅ ✨ **NEW**
System-wide soft-delete and restoration functionality.

**Capabilities:**
- Soft-delete items across all modules
- Full JSON snapshot of deleted data
- Configurable retention policies
- Automatic cleanup scheduler
- Restoration with tracking
- Permanent deletion with confirmation

**Endpoints**: 17 total

**Trash Items** (6 endpoints):
- `GET /api/v1/admin/trash/` - List trash with filters
- `GET /api/v1/admin/trash/stats` - Dashboard statistics
- `GET /api/v1/admin/trash/{id}` - Get trash item
- `POST /api/v1/admin/trash/` - Soft delete
- `POST /api/v1/admin/trash/{id}/restore` - Restore item
- `DELETE /api/v1/admin/trash/{id}` - Permanent delete

**Trash Configuration** (5 endpoints):
- `GET /api/v1/admin/trash/config/` - List configurations
- `GET /api/v1/admin/trash/config/{module}/{resource}` - Get config
- `POST /api/v1/admin/trash/config/` - Create config
- `PUT /api/v1/admin/trash/config/{id}` - Update config
- `DELETE /api/v1/admin/trash/config/{id}` - Delete config

**Cleanup** (2 endpoints):
- `POST /api/v1/admin/trash/cleanup/scheduled` - Run scheduled cleanup
- `POST /api/v1/admin/trash/cleanup/{module}/{resource}` - Config-based cleanup

**Auto-Cleanup Schedule:**
- Daily at 2:00 AM (full cleanup)
- Every 6 hours (additional cleanup)

### 3. Audit Logging ✅
Complete audit trail for all administrative actions.

**Tracked Information:**
- User identification (ID, email)
- Action type (CREATE, UPDATE, DELETE, RESTORE, PERMANENT_DELETE)
- Module and resource details
- Before/after state snapshots
- Request metadata (IP address, user agent)
- Timestamp

### 4. System Modules Registry ✅
Registry of all system modules with status tracking.

**Module Information:**
- Display name and description
- Version tracking
- Status (ACTIVE, INACTIVE, MAINTENANCE)
- API and Frontend endpoints
- Icon and sort order
- Authentication requirements
- Role-based access

## Database Schema

### admin_db Schema (6 tables)

#### 1. module_settings
Stores module-specific configuration settings.

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| module_name | VARCHAR(50) | Module identifier |
| setting_key | VARCHAR(100) | Setting key |
| setting_value | TEXT | Setting value (JSON for complex types) |
| setting_type | ENUM | STRING, INTEGER, BOOLEAN, JSON |
| display_name | VARCHAR(200) | Human-readable name |
| description | TEXT | Setting description |
| category | VARCHAR(100) | Category for grouping |
| is_public | BOOLEAN | Public visibility |
| is_editable | BOOLEAN | Can be edited by users |
| default_value | TEXT | Default value |
| validation_rules | TEXT | JSON validation rules |
| created_at | TIMESTAMP | Creation timestamp |
| updated_at | TIMESTAMP | Last update timestamp |
| updated_by | INTEGER | User who updated |

#### 2. system_modules
Registry of all system modules.

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| module_name | VARCHAR(50) | Unique module identifier |
| display_name | VARCHAR(200) | Display name |
| description | TEXT | Module description |
| version | VARCHAR(20) | Module version |
| status | ENUM | ACTIVE, INACTIVE, MAINTENANCE |
| api_endpoint | VARCHAR(500) | API base URL |
| frontend_endpoint | VARCHAR(500) | Frontend base URL |
| icon | VARCHAR(50) | Icon name (lucide-react) |
| sort_order | INTEGER | Display order |
| requires_auth | BOOLEAN | Requires authentication |
| allowed_roles | TEXT | JSON array of roles |
| is_system_module | BOOLEAN | Core system module |
| created_at | TIMESTAMP | Creation timestamp |
| updated_at | TIMESTAMP | Last update timestamp |

#### 3. audit_logs
Audit trail for all admin actions.

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| user_id | INTEGER | User who performed action |
| user_email | VARCHAR(255) | User email |
| action | VARCHAR(50) | Action type |
| module_name | VARCHAR(50) | Target module |
| resource_type | VARCHAR(100) | Resource type |
| resource_id | VARCHAR(100) | Resource ID |
| description | TEXT | Action description |
| changes | JSON | Before/after state |
| ip_address | VARCHAR(45) | Client IP |
| user_agent | VARCHAR(500) | Client user agent |
| created_at | TIMESTAMP | Action timestamp |

#### 4. system_logs
System-level event logging.

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| log_level | VARCHAR(20) | INFO, WARNING, ERROR |
| module_name | VARCHAR(50) | Source module |
| message | TEXT | Log message |
| details | JSON | Additional details |
| stack_trace | TEXT | Error stack trace |
| created_at | TIMESTAMP | Log timestamp |

#### 5. trash_items ✨ **NEW**
Soft-deleted items from all modules.

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| module_name | VARCHAR(50) | Source module |
| resource_type | VARCHAR(100) | Resource type |
| resource_id | VARCHAR(100) | Original resource ID |
| resource_name | VARCHAR(500) | Display name |
| resource_data | JSON | Full resource snapshot |
| deleted_by | INTEGER | User who deleted |
| deleted_by_email | VARCHAR(255) | Deleter email |
| deleted_at | TIMESTAMP | Deletion timestamp |
| deleted_reason | TEXT | Deletion reason |
| is_restorable | BOOLEAN | Can be restored |
| permanent_delete_at | TIMESTAMP | Scheduled deletion date |
| restore_dependencies | JSON | Dependent items list |
| extra_metadata | JSON | Additional metadata |
| restored_at | TIMESTAMP | Restoration timestamp |
| restored_by | INTEGER | User who restored |
| restored_by_email | VARCHAR(255) | Restorer email |

#### 6. trash_config ✨ **NEW**
Trash behavior configuration per module/resource.

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| module_name | VARCHAR(50) | Target module |
| resource_type | VARCHAR(100) | Target resource |
| auto_delete_days | INTEGER | Days before auto-delete (0=never) |
| enable_soft_delete | BOOLEAN | Enable soft delete |
| enable_restore | BOOLEAN | Enable restoration |
| require_approval | BOOLEAN | Require approval for restore |
| cascade_delete | BOOLEAN | Delete dependent items |
| created_at | TIMESTAMP | Creation timestamp |
| updated_at | TIMESTAMP | Last update timestamp |

## Default Configurations

### Default System Modules
- auth - Authentication & Authorization
- asset - Asset Management
- procurement - Procurement Management
- dashboard - System Dashboard
- admin - Administration

### Default Trash Configurations

| Module | Resource Type | Retention Days | Approval Required | Cascade Delete |
|--------|--------------|----------------|-------------------|----------------|
| auth | user | 90 | No | No |
| auth | role | 90 | Yes | No |
| asset | asset | 365 | No | Yes |
| asset | category | 90 | Yes | No |
| procurement | purchase_request | 180 | No | No |
| procurement | purchase_order | 365 | No | No |
| procurement | vendor | 180 | No | No |
| procurement | framework_contract | 730 | Yes | No |

## Architecture

### Technology Stack
- **Framework**: FastAPI 0.104.1
- **ORM**: SQLAlchemy 2.0.23
- **Database**: MySQL 8.0 (admin_db schema)
- **Migration**: Alembic 1.12.1
- **Scheduler**: APScheduler 3.10.4
- **Cache**: Redis 5.0.1
- **Authentication**: JWT (python-jose)

### Design Patterns
- **Repository Pattern** - Data access abstraction
- **Service Layer Pattern** - Business logic encapsulation
- **Dependency Injection** - FastAPI dependencies
- **Soft Delete Mixin** - Reusable soft-delete functionality

### Components

```
admin-api/
├── app/
│   ├── api/
│   │   └── v1/
│   │       └── endpoints/
│   │           ├── module_settings.py (9 endpoints)
│   │           └── trash.py (17 endpoints)
│   ├── models/
│   │   ├── base.py
│   │   ├── module_setting.py
│   │   ├── audit_log.py
│   │   └── trash.py
│   ├── schemas/
│   │   ├── module_setting_schema.py
│   │   ├── audit_log_schema.py
│   │   └── trash_schema.py
│   ├── repositories/
│   │   ├── module_setting_repository.py
│   │   ├── audit_log_repository.py
│   │   └── trash_repository.py
│   ├── mixins/
│   │   └── soft_delete.py
│   ├── tasks/
│   │   └── trash_cleanup.py
│   └── core/
│       ├── config.py
│       ├── database.py
│       └── dependencies.py
├── alembic/
│   └── versions/
│       ├── 001_initial_admin_schema.py
│       └── 002_add_trash_tables.py
└── requirements.txt
```

## API Usage Examples

### Module Settings

```bash
# List all settings
curl http://localhost:8005/api/v1/admin/module-settings/ \
  -H "Authorization: Bearer $TOKEN"

# Create a setting
curl -X POST http://localhost:8005/api/v1/admin/module-settings/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "module_name": "asset",
    "setting_key": "max_file_size",
    "setting_value": "10485760",
    "setting_type": "INTEGER",
    "display_name": "Maximum File Size",
    "description": "Maximum upload file size in bytes",
    "category": "Upload",
    "is_public": false,
    "is_editable": true
  }'
```

### Trash Management

```bash
# List trash items
curl http://localhost:8005/api/v1/admin/trash/?module_name=asset \
  -H "Authorization: Bearer $TOKEN"

# Get trash statistics
curl http://localhost:8005/api/v1/admin/trash/stats \
  -H "Authorization: Bearer $TOKEN"

# Restore an item
curl -X POST http://localhost:8005/api/v1/admin/trash/123/restore \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "restore_reason": "Restored by request",
    "restore_dependencies": false
  }'

# Permanent delete
curl -X DELETE http://localhost:8005/api/v1/admin/trash/123 \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "confirmation": "PERMANENTLY_DELETE",
    "reason": "Equipment destroyed"
  }'
```

## Integration Guide

### Using Soft Delete in Your Service

1. **Add the SoftDeleteMixin to your model**:

```python
from app.mixins.soft_delete import SoftDeleteMixin

class Asset(Base, SoftDeleteMixin):
    __tablename__ = "assets"
    id = Column(Integer, primary_key=True)
    name = Column(String(200))
    # ... other fields
```

2. **Soft delete an item**:

```python
trash_item = asset.soft_delete(
    db=db,
    user_id=current_user["id"],
    user_email=current_user["email"],
    reason="User requested deletion",
    module_name="asset",
    resource_type="asset"
)
```

3. **Filter out deleted items**:

```python
active_assets = db.query(Asset).filter(Asset.is_deleted == False).all()
```

4. **Restore an item**:

```python
asset.restore(
    db=db,
    user_id=current_user["id"],
    user_email=current_user["email"]
)
```

## Deployment

### Using Docker

```bash
# Build
docker compose build admin-api

# Start
docker compose up -d admin-api

# Check logs
docker compose logs -f admin-api

# Verify health
curl http://localhost:8005/health
```

### Database Migrations

**IMPORTANT**: Requires MySQL recreation to create admin_db database.

See [DEPLOYMENT_INSTRUCTIONS.md](DEPLOYMENT_INSTRUCTIONS.md) for complete deployment steps.

```bash
# After MySQL recreation
docker compose exec admin-api alembic upgrade head

# Check current version
docker compose exec admin-api alembic current

# Rollback
docker compose exec admin-api alembic downgrade -1
```

## Documentation

- **[TRASH_FEATURE_GUIDE.md](TRASH_FEATURE_GUIDE.md)** - Complete trash feature usage guide
- **[DEPLOYMENT_INSTRUCTIONS.md](DEPLOYMENT_INSTRUCTIONS.md)** - Deployment procedures
- **[IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md)** - Technical implementation details
- **API Docs**: http://localhost:8005/docs (Swagger UI)
- **API Docs**: http://localhost:8005/redoc (ReDoc)

## Security

- All endpoints require admin authentication
- Complete audit trail for all operations
- Request metadata tracking (IP, user agent)
- Permanent delete requires confirmation string
- Before/after snapshots in audit logs

## Monitoring

### Health Check

```bash
curl http://localhost:8005/health
# {"status": "healthy", "service": "Admin Management Service", "version": "1.0.0"}
```

### Logs

```bash
# Real-time logs
docker compose logs -f admin-api

# Scheduler logs
docker compose logs admin-api | grep -i "trash cleanup"

# Error logs
docker compose logs admin-api | grep ERROR
```

### Metrics to Track
- Trash item count by module
- Trash size growth
- Cleanup success/failure rate
- Restoration success rate
- API response times

## Troubleshooting

### Common Issues

**1. Database Permission Error**
```
Error: (1045, "Access denied for user 'officework'@'%'")
Solution: Recreate MySQL with updated init.sql (see DEPLOYMENT_INSTRUCTIONS.md)
```

**2. Trash Cleanup Not Running**
```bash
# Check scheduler status
docker compose logs admin-api | grep scheduler

# Run manual cleanup
docker compose exec admin-api python -m app.tasks.trash_cleanup
```

**3. Admin API Unhealthy**
```bash
# Check logs
docker compose logs admin-api --tail 100

# Restart service
docker compose restart admin-api
```

## Version History

- **v1.0.0** (2025-11-08) - Initial release
  - Module settings management
  - System modules registry
  - Audit logging

- **v1.1.0** (2025-11-08) - Trash feature ✨
  - Trash/recycle bin system
  - Automatic cleanup scheduler
  - Soft delete mixin
  - Default configurations

## Support

For issues or questions:
- API Documentation: http://localhost:8005/docs
- Project Documentation: [../../CLAUDE.md](../../CLAUDE.md)
- Feature Guide: [TRASH_FEATURE_GUIDE.md](TRASH_FEATURE_GUIDE.md)

---

**Developed by**: Claude AI Assistant
**Last Updated**: 2025-11-08
**Status**: Production Ready (pending MySQL migration)
