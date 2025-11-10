# Trash/Recycle Bin Feature Guide

## Overview

The Admin API provides a comprehensive trash/recycle bin feature that allows:
- Soft-deleting items across all modules
- Reviewing deleted items
- Restoring deleted items
- Permanently deleting items
- Automatic cleanup of old trash items

## Architecture

### Components

1. **TrashItem Model** - Stores soft-deleted items with full snapshots
2. **TrashConfig Model** - Configuration for trash behavior per module/resource
3. **Trash Repository** - Data access layer for trash operations
4. **Trash API Endpoints** - RESTful API for trash management
5. **Trash Cleanup Scheduler** - Automatic cleanup of old items
6. **SoftDeleteMixin** - Reusable mixin for models

### Database Tables

#### `trash_items`
Stores all soft-deleted items with:
- Resource identification (module, type, ID, name)
- Full JSON snapshot of deleted data
- Deletion metadata (who, when, why)
- Restoration tracking
- Dependencies and metadata

#### `trash_config`
Configuration per module/resource:
- `auto_delete_days` - Days before automatic permanent deletion (0 = never)
- `enable_soft_delete` - Enable/disable soft delete for this resource
- `enable_restore` - Enable/disable restoration
- `require_approval` - Require approval for restoration
- `cascade_delete` - Delete related items

## API Endpoints

### Trash Items

#### List Trash Items
```bash
GET /api/v1/admin/trash/
Query Parameters:
  - module_name (optional)
  - resource_type (optional)
  - deleted_by (optional)
  - start_date (optional)
  - end_date (optional)
  - is_restorable (optional)
  - skip (default: 0)
  - limit (default: 100)

Response: TrashItemsListResponse with aggregated counts
```

#### Get Trash Statistics
```bash
GET /api/v1/admin/trash/stats

Response:
{
  "total_items": 150,
  "total_size_kb": null,
  "by_module": {
    "auth": 50,
    "asset": 100
  },
  "by_type": {
    "user": 30,
    "asset": 100,
    "role": 20
  },
  "restorable_count": 145,
  "scheduled_for_deletion": 5,
  "oldest_item": "2024-01-01T00:00:00",
  "newest_item": "2025-11-08T10:00:00"
}
```

#### Get Trash Item
```bash
GET /api/v1/admin/trash/{trash_id}

Response: Full trash item with resource snapshot
```

#### Soft Delete Item
```bash
POST /api/v1/admin/trash/

Body:
{
  "module_name": "asset",
  "resource_type": "asset",
  "resource_id": "123",
  "resource_name": "Laptop Dell XPS 15",
  "resource_data": {
    "id": 123,
    "name": "Laptop Dell XPS 15",
    "serial_number": "ABC123",
    ...
  },
  "deleted_by": 1,
  "deleted_by_email": "admin@example.com",
  "deleted_reason": "Equipment retired",
  "is_restorable": true,
  "permanent_delete_at": null
}

Response: Created trash item
```

#### Restore Item
```bash
POST /api/v1/admin/trash/{trash_id}/restore

Body:
{
  "restore_reason": "Restored by mistake",
  "restore_dependencies": false
}

Response: Updated trash item with restoration metadata
```

#### Permanent Delete
```bash
DELETE /api/v1/admin/trash/{trash_id}

Body:
{
  "confirmation": "PERMANENTLY_DELETE",
  "reason": "Equipment destroyed"
}

Response: 204 No Content
```

### Trash Configuration

#### List Configs
```bash
GET /api/v1/admin/trash/config/
Query: module_name (optional)
```

#### Get Config
```bash
GET /api/v1/admin/trash/config/{module_name}/{resource_type}
```

#### Create Config
```bash
POST /api/v1/admin/trash/config/

Body:
{
  "module_name": "asset",
  "resource_type": "asset",
  "auto_delete_days": 365,
  "enable_soft_delete": true,
  "enable_restore": true,
  "require_approval": false,
  "cascade_delete": true
}
```

#### Update Config
```bash
PUT /api/v1/admin/trash/config/{config_id}

Body:
{
  "auto_delete_days": 180,
  "enable_restore": false
}
```

### Cleanup Operations

#### Run Scheduled Cleanup
```bash
POST /api/v1/admin/trash/cleanup/scheduled

Response:
{
  "success": true,
  "deleted_count": 25,
  "message": "Cleaned up 25 scheduled items"
}
```

#### Run Config-Based Cleanup
```bash
POST /api/v1/admin/trash/cleanup/{module_name}/{resource_type}

Response:
{
  "success": true,
  "deleted_count": 10,
  "message": "Cleaned up 10 old items for asset/asset"
}
```

## Using SoftDeleteMixin

### Step 1: Add Mixin to Your Model

```python
from app.mixins.soft_delete import SoftDeleteMixin
from app.models.base import Base

class Asset(Base, SoftDeleteMixin):
    __tablename__ = "assets"
    __table_args__ = {"schema": "asset_db"}

    id = Column(Integer, primary_key=True)
    name = Column(String(200))
    serial_number = Column(String(100))
    # ... other fields

    # The mixin adds:
    # - is_deleted: Boolean
    # - deleted_at: TIMESTAMP
    # - deleted_by: Integer
```

### Step 2: Soft Delete an Item

```python
from app.repositories.asset_repository import AssetRepository

# In your endpoint or service
@router.delete("/{asset_id}")
async def delete_asset(
    asset_id: int,
    request: Request,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    repo = AssetRepository(db)
    asset = repo.get_by_id(asset_id)

    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")

    # Soft delete with trash entry
    trash_item = asset.soft_delete(
        db=db,
        user_id=current_user["id"],
        user_email=current_user["email"],
        reason="User requested deletion",
        module_name="asset",
        resource_type="asset",
        create_trash_entry=True,
    )

    return {"message": "Asset soft-deleted", "trash_id": trash_item.id}
```

### Step 3: Filter Out Deleted Items

```python
# In your repository
def get_active_assets(self, skip: int = 0, limit: int = 100):
    """Get only non-deleted assets"""
    return (
        self.db.query(Asset)
        .filter(Asset.is_deleted == False)  # Filter out soft-deleted
        .offset(skip)
        .limit(limit)
        .all()
    )

# Or use the query mixin
def get_all_assets(self):
    """Get all assets including deleted"""
    return Asset.get_all_query(self.db).all()

def get_deleted_assets(self):
    """Get only deleted assets"""
    return Asset.get_deleted_query(self.db).all()
```

### Step 4: Restore an Item

```python
@router.post("/{asset_id}/restore")
async def restore_asset(
    asset_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    repo = AssetRepository(db)
    asset = repo.get_by_id(asset_id)

    if not asset or not asset.is_soft_deleted():
        raise HTTPException(status_code=404, detail="Deleted asset not found")

    # Restore the asset
    asset.restore(
        db=db,
        user_id=current_user["id"],
        user_email=current_user["email"],
    )

    return {"message": "Asset restored successfully"}
```

## Automatic Cleanup

The trash cleanup scheduler runs automatically:
- **Daily at 2:00 AM** - Full cleanup (scheduled + config-based)
- **Every 6 hours** - Additional config-based cleanup

### Cleanup Logic

1. **Scheduled Cleanup**: Deletes items with `permanent_delete_at <= now`
2. **Config-Based Cleanup**: Deletes items older than `auto_delete_days` for each module/resource

### Manual Cleanup

You can trigger manual cleanup via API:

```bash
# Cleanup all scheduled items
curl -X POST http://localhost:8005/api/v1/admin/trash/cleanup/scheduled \
  -H "Authorization: Bearer $TOKEN"

# Cleanup specific module/resource
curl -X POST http://localhost:8005/api/v1/admin/trash/cleanup/asset/asset \
  -H "Authorization: Bearer $TOKEN"
```

Or run the task script directly:

```bash
docker compose exec admin-api python -m app.tasks.trash_cleanup
```

## Default Trash Configurations

The following configurations are created by default:

| Module | Resource Type | Auto Delete Days | Restore Enabled | Cascade Delete |
|--------|--------------|------------------|-----------------|----------------|
| auth | user | 90 | Yes | No |
| auth | role | 90 | Yes (approval required) | No |
| asset | asset | 365 | Yes | Yes |
| asset | category | 90 | Yes (approval required) | No |
| procurement | purchase_request | 180 | Yes | No |
| procurement | purchase_order | 365 | Yes | No |
| procurement | vendor | 180 | Yes | No |
| procurement | framework_contract | 730 | Yes (approval required) | No |

## Migration

To apply the trash tables:

```bash
# Enter admin-api container
docker compose exec admin-api bash

# Run migration
alembic upgrade head

# Verify tables
alembic current
```

## Audit Trail

All trash operations are logged in the `audit_logs` table:
- SOFT_DELETE - When item is moved to trash
- RESTORE - When item is restored
- PERMANENT_DELETE - When item is permanently deleted

## Best Practices

1. **Always Use Soft Delete** for user-facing deletions
   - Allows recovery from accidental deletions
   - Maintains data history

2. **Configure Auto-Delete** appropriately
   - Critical data: 365+ days or 0 (never)
   - Regular data: 90-180 days
   - Temporary data: 30 days

3. **Use Cascade Delete** for related items
   - Enable for parent-child relationships
   - Ensure dependencies are tracked

4. **Monitor Trash Size**
   - Use `/trash/stats` endpoint
   - Set up alerts for large trash accumulation

5. **Regular Cleanup Reviews**
   - Review scheduled deletions periodically
   - Adjust auto_delete_days based on usage patterns

## Security

- All trash endpoints require **admin privileges**
- Permanent deletion requires **confirmation string**
- All operations are **audit logged**
- IP address and user agent tracked
- Full resource snapshot preserved

## Troubleshooting

### Trash Cleanup Not Running

Check scheduler status:
```bash
docker compose logs admin-api | grep -i "trash cleanup"
```

### Items Not Auto-Deleting

1. Check trash config: `GET /api/v1/admin/trash/config/{module}/{resource}`
2. Verify `auto_delete_days > 0`
3. Check item age vs auto_delete_days
4. Run manual cleanup to test

### Restore Failing

1. Verify item is restorable: `is_restorable == true`
2. Check if already restored: `restored_at == null`
3. Ensure calling service implements restore logic
4. Check trash config: `enable_restore == true`

## Example Workflow

```python
# 1. User deletes an asset
DELETE /api/v1/assets/123
→ Asset.soft_delete() called
→ TrashItem created in admin_db
→ Asset marked is_deleted=true

# 2. Admin reviews trash
GET /api/v1/admin/trash/?module_name=asset
→ Returns list of deleted assets

# 3. Admin restores by mistake
POST /api/v1/admin/trash/456/restore
→ TrashItem marked as restored
→ Asset.restore() called
→ Asset marked is_deleted=false

# 4. Admin permanently deletes
DELETE /api/v1/admin/trash/789
→ TrashItem deleted from database
→ Audit log created
→ (Asset service should also delete)

# 5. Automatic cleanup runs
→ Scheduler triggers at 2:00 AM
→ Items older than auto_delete_days deleted
→ Scheduled items deleted
→ System log created
```

## Integration Example

### Asset Service Integration

```python
# services/asset-api/app/api/v1/endpoints/assets.py

import httpx

@router.delete("/{asset_id}")
async def delete_asset(
    asset_id: int,
    reason: Optional[str] = None,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Soft delete an asset"""
    repo = AssetRepository(db)
    asset = repo.get_by_id(asset_id)

    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")

    # Soft delete in asset database
    trash_item = asset.soft_delete(
        db=db,
        user_id=current_user["id"],
        user_email=current_user["email"],
        reason=reason,
        module_name="asset",
        resource_type="asset",
    )

    # Also send to admin trash API
    async with httpx.AsyncClient() as client:
        try:
            await client.post(
                "http://admin-api:8000/api/v1/admin/trash/",
                json={
                    "module_name": "asset",
                    "resource_type": "asset",
                    "resource_id": str(asset_id),
                    "resource_name": asset.name,
                    "resource_data": asset._to_dict(),
                    "deleted_by": current_user["id"],
                    "deleted_by_email": current_user["email"],
                    "deleted_reason": reason,
                },
                headers={"Authorization": f"Bearer {current_user['token']}"},
            )
        except Exception as e:
            logger.error(f"Failed to create trash entry: {e}")

    return {"message": "Asset deleted", "trash_id": trash_item.id}
```

## API Documentation

Full API documentation available at:
- Swagger UI: http://localhost:8005/docs
- ReDoc: http://localhost:8005/redoc

Look for the "Trash Management" tag in the API docs.
