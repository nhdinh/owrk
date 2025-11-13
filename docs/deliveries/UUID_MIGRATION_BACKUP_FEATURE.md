# UUID Migration - Automatic Backup Feature ✨

**Date Added**: 2025-11-13
**Status**: ✅ Implemented in Bash script

---

## 🎯 Overview

The UUID migration script now includes **automatic database backup** before dropping any databases. This provides a safety net and allows you to restore your data if needed.

---

## 📦 What's New

### Added to Migration Script

The `scripts/uuid_migration.sh` (Bash) script now includes:

**Phase 2: Backup Current Databases** (New step inserted after dependency installation)

- Creates timestamped backup directory: `backups/YYYYMMDD_HHMMSS_pre_uuid_migration/`
- Backs up all four databases:
  - `auth_db.sql`
  - `asset_db.sql`
  - `admin_db.sql`
  - `procurement_db.sql`
- Uses `mysqldump` with safe flags:
  - `--single-transaction`: Consistent backup without locking tables
  - `--routines`: Includes stored procedures
  - `--triggers`: Includes database triggers
- Displays backup file sizes and location
- Gracefully handles empty/non-existent databases

### Updated `.gitignore`

Added `backups/` directory to `.gitignore` to prevent committing large SQL dumps to version control.

---

## 🔧 Technical Details

### Backup Directory Structure

```
backups/
├── 20251113_143025_pre_uuid_migration/
│   ├── auth_db.sql
│   ├── asset_db.sql
│   ├── admin_db.sql
│   └── procurement_db.sql
├── 20251113_150432_pre_uuid_migration/
│   ├── auth_db.sql
│   ├── asset_db.sql
│   ├── admin_db.sql
│   └── procurement_db.sql
...
```

### Backup File Format

- **Format**: Plain SQL dump
- **Encoding**: UTF-8
- **Includes**: Schema + Data + Routines + Triggers
- **Size**: Varies depending on database content (typically 1-50 MB per database)

### Timestamp Format

- **Pattern**: `YYYYMMDD_HHMMSS`
- **Example**: `20251113_143025` = November 13, 2025 at 14:30:25
- **Timezone**: Local system time

---

## 🔄 How to Restore from Backup

If you need to rollback the UUID migration and restore your old data:

### Step 1: Find Your Backup

```bash
ls -lt backups/ | head -n 6
```

### Step 2: Drop Current Databases

```bash
docker exec -i mysql mysql -uroot -p$(cat .secrets/mysql_root_passwd.txt) <<EOF
DROP DATABASE IF EXISTS auth_db;
DROP DATABASE IF EXISTS asset_db;
DROP DATABASE IF EXISTS admin_db;
DROP DATABASE IF EXISTS procurement_db;
EOF
```

### Step 3: Recreate Databases

```bash
docker exec -i mysql mysql -uroot -p$(cat .secrets/mysql_root_passwd.txt) <<EOF
CREATE DATABASE auth_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE DATABASE asset_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE DATABASE admin_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE DATABASE procurement_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

GRANT ALL PRIVILEGES ON auth_db.* TO 'officework'@'%';
GRANT ALL PRIVILEGES ON asset_db.* TO 'officework'@'%';
GRANT ALL PRIVILEGES ON admin_db.* TO 'officework'@'%';
GRANT ALL PRIVILEGES ON procurement_db.* TO 'officework'@'%';
FLUSH PRIVILEGES;
EOF
```

### Step 4: Restore from Backup

```bash
# Replace BACKUP_DIR with actual timestamp
BACKUP_DIR="backups/YYYYMMDD_HHMMSS_pre_uuid_migration"

docker exec -i mysql mysql -uofficework -p$(cat .secrets/mysql_user_passwd.txt) auth_db < "$BACKUP_DIR/auth_db.sql"
docker exec -i mysql mysql -uofficework -p$(cat .secrets/mysql_user_passwd.txt) asset_db < "$BACKUP_DIR/asset_db.sql"
docker exec -i mysql mysql -uofficework -p$(cat .secrets/mysql_user_passwd.txt) admin_db < "$BACKUP_DIR/admin_db.sql"
docker exec -i mysql mysql -uofficework -p$(cat .secrets/mysql_user_passwd.txt) procurement_db < "$BACKUP_DIR/procurement_db.sql"
```

### Step 5: Revert Code Changes

After restoring databases, you must revert the code changes:

```bash
# Checkout the commit before UUID migration
git log --oneline --all --graph

# Find the commit hash before UUID changes
git checkout <commit-hash-before-uuid>

# Or create a new branch from that commit
git checkout -b rollback-uuid <commit-hash-before-uuid>
```

Then restart services:

```bash
docker compose restart auth-api asset-api admin-api procurement-api
```

---

## 📊 Updated Migration Flow

### Before (Old Flow)

1. Install Dependencies
2. **Drop Databases** ⚠️ **NO BACKUP**
3. Create New Databases
4. Clean Migrations
5. Generate Migrations
6. Run Migrations
7. Seed Data
8. Verify

### After (New Flow with Backup)

1. Install Dependencies
2. **✨ Backup Current Databases** ← **NEW STEP**
3. Drop Databases
4. Create New Databases
5. Clean Migrations
6. Generate Migrations
7. Run Migrations
8. Seed Data
9. Verify

---

## ⏱️ Updated Time Estimates

| Phase | Time | Notes |
|-------|------|-------|
| **Total** | **6-12 minutes** | +1-2 min for backup |
| Dependencies | 2-3 minutes | No change |
| **Backup** | **1-2 minutes** | **NEW** - varies by DB size |
| Database Ops | 1 minute | No change |
| Migrations | 2-3 minutes | No change |
| Seeding | 30 seconds | No change |
| Verification | 30 seconds | No change |

---

## 🛡️ Safety Features

### 1. Non-Destructive Backup

- Backups are created **before** any destructive operations
- Uses `--single-transaction` for consistency
- No table locks during backup

### 2. Error Handling

- Script continues even if backup fails (e.g., empty database)
- Displays warning if database doesn't exist
- Does not abort migration on backup errors

### 3. Multiple Backups Preserved

- Each migration run creates a new timestamped backup
- Old backups are not deleted automatically
- You can manually clean up old backups when needed

### 4. Git Ignored

- `backups/` directory is excluded from version control
- Prevents accidentally committing large SQL files
- Keeps repository size manageable

---

## 📝 Script Output Example

### Backup Phase Output (Bash)

```
==========================================
Step 2: Backing Up Current Databases
==========================================
💾 Backing up auth_db...
💾 Backing up asset_db...
💾 Backing up admin_db...
💾 Backing up procurement_db...
✅ Backups saved to: backups/20251113_143025_pre_uuid_migration

📋 Backup files:
-rw-r--r-- 1 user user 1.0M Nov 13 14:30 auth_db.sql
-rw-r--r-- 1 user user 512K Nov 13 14:30 asset_db.sql
-rw-r--r-- 1 user user 256K Nov 13 14:30 admin_db.sql
-rw-r--r-- 1 user user 128K Nov 13 14:30 procurement_db.sql
```

### Final Summary (Bash)

```
==========================================
✅ Migration Complete!
==========================================

📋 Summary:
  - Database backups saved to: backups/20251113_143025_pre_uuid_migration
  - All databases recreated with UUID primary keys
  - All tables have slug fields for URL-friendly identifiers
  - Admin user created: admin@example.com / admin123
  - Admin role created with full permissions

💾 Backup Information:
  - Location: backups/20251113_143025_pre_uuid_migration
  - auth_db.sql: 1.0M
  - asset_db.sql: 512K
  - admin_db.sql: 256K
  - procurement_db.sql: 128K

🔄 To restore from backup (if needed):
  docker exec -i mysql mysql -uofficework -p$(cat .secrets/mysql_user_passwd.txt) auth_db < backups/20251113_143025_pre_uuid_migration/auth_db.sql
  docker exec -i mysql mysql -uofficework -p$(cat .secrets/mysql_user_passwd.txt) asset_db < backups/20251113_143025_pre_uuid_migration/asset_db.sql
  docker exec -i mysql mysql -uofficework -p$(cat .secrets/mysql_user_passwd.txt) admin_db < backups/20251113_143025_pre_uuid_migration/admin_db.sql
  docker exec -i mysql mysql -uofficework -p$(cat .secrets/mysql_user_passwd.txt) procurement_db < backups/20251113_143025_pre_uuid_migration/procurement_db.sql
```

---

## 🗑️ Managing Old Backups

### View All Backups

```bash
du -sh backups/*/ | sort -h
```

### Delete Old Backups

**Keep only last 3 backups**:

```bash
ls -t backups/ | tail -n +4 | xargs -I {} rm -rf backups/{}
```

### Manual Cleanup

```bash
# Delete specific backup
rm -rf backups/20251113_143025_pre_uuid_migration

# Delete all backups older than 30 days
find backups/ -type d -mtime +30 -exec rm -rf {} +
```

---

## ✅ Benefits

1. **Safety Net**: Can rollback if migration fails
2. **Data Preservation**: No data loss during testing
3. **Debugging**: Can compare old vs new schema
4. **Confidence**: Test migration without fear
5. **Compliance**: Audit trail of data changes

---

## ⚠️ Important Notes

1. **Disk Space**: Ensure sufficient disk space for backups (typically 10-100 MB total)
2. **Backup Time**: Large databases (>1GB) may take longer to backup
3. **Not a Replacement**: This is a convenience backup, not a production backup strategy
4. **Manual Cleanup**: Old backups are not auto-deleted, clean up periodically
5. **Git Ignored**: Backups won't be committed to repository

---

## 📚 Related Documentation

- [UUID_SLUG_MIGRATION_PLAN.md](./UUID_SLUG_MIGRATION_PLAN.md) - Master plan
- [UUID_MIGRATION_IMPLEMENTATION_GUIDE.md](./UUID_MIGRATION_IMPLEMENTATION_GUIDE.md) - Implementation guide
- [UUID_MIGRATION_READY.md](./UUID_MIGRATION_READY.md) - Execution readiness
- [UUID_MIGRATION_MODELS_COMPLETE.md](./UUID_MIGRATION_MODELS_COMPLETE.md) - Model updates complete

---

**Implementation Date**: 2025-11-13
**Implemented By**: Claude AI
**Script Updated**:
- `scripts/uuid_migration.sh` (Bash for Linux/Mac/Windows Git Bash)
- `.gitignore` (Added `backups/` exclusion)
