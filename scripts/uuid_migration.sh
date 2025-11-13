#!/bin/bash
# UUID Migration Script - Complete Migration from Integer ID to UUID + Slug
# This script performs a fresh start migration (drops all data)

set -e  # Exit on error

echo "=========================================="
echo "UUID + Slug Migration Script"
echo "=========================================="
echo ""
echo "⚠️  WARNING: This will DROP ALL DATABASES and DATA!"
echo "⚠️  Make sure you have a backup if needed."
echo ""
read -p "Continue? (yes/no): " confirm

if [ "$confirm" != "yes" ]; then
    echo "❌ Migration cancelled."
    exit 1
fi

echo ""
echo "=========================================="
echo "Step 1: Installing Dependencies"
echo "=========================================="

echo "📦 Installing unidecode in auth-api..."
docker compose exec -T auth-api pip install unidecode==1.3.8

echo "📦 Installing unidecode in asset-api..."
docker compose exec -T asset-api pip install unidecode==1.3.8

echo "📦 Installing unidecode in admin-api..."
docker compose exec -T admin-api pip install unidecode==1.3.8

echo "📦 Installing unidecode in procurement-api..."
docker compose exec -T procurement-api pip install unidecode==1.3.8

echo "✅ Dependencies installed"

echo ""
echo "=========================================="
echo "Step 2: Backing Up Current Databases"
echo "=========================================="

# Create backup directory with timestamp
BACKUP_DIR="backups/$(date +%Y%m%d_%H%M%S)_pre_uuid_migration"
mkdir -p "$BACKUP_DIR"

echo "💾 Backing up auth_db..."
docker compose exec mysql mysqldump -uofficework -p$(cat .secrets/mysql_user_passwd.txt) \
    --single-transaction \
    --routines \
    --triggers \
    auth_db > "$BACKUP_DIR/auth_db.sql" 2>/dev/null || echo "⚠️  auth_db is empty or doesn't exist"

echo "💾 Backing up asset_db..."
docker compose exec mysql mysqldump -uofficework -p$(cat .secrets/mysql_user_passwd.txt) \
    --single-transaction \
    --routines \
    --triggers \
    asset_db > "$BACKUP_DIR/asset_db.sql" 2>/dev/null || echo "⚠️  asset_db is empty or doesn't exist"

echo "💾 Backing up admin_db..."
docker compose exec mysql mysqldump -uofficework -p$(cat .secrets/mysql_user_passwd.txt) \
    --single-transaction \
    --routines \
    --triggers \
    admin_db > "$BACKUP_DIR/admin_db.sql" 2>/dev/null || echo "⚠️  admin_db is empty or doesn't exist"

echo "💾 Backing up procurement_db..."
docker compose exec mysql mysqldump -uofficework -p$(cat .secrets/mysql_user_passwd.txt) \
    --single-transaction \
    --routines \
    --triggers \
    procurement_db > "$BACKUP_DIR/procurement_db.sql" 2>/dev/null || echo "⚠️  procurement_db is empty or doesn't exist"

echo "✅ Backups saved to: $BACKUP_DIR"
echo ""
echo "📋 Backup files:"
ls -lh "$BACKUP_DIR"

echo ""
echo "=========================================="
echo "Step 3: Dropping Old Databases"
echo "=========================================="

echo "🗑️  Dropping databases..."
docker compose exec -T mysql mysql -uroot -p$(cat .secrets/mysql_root_passwd.txt) <<EOF
DROP DATABASE IF EXISTS auth_db;
DROP DATABASE IF EXISTS asset_db;
DROP DATABASE IF EXISTS admin_db;
DROP DATABASE IF EXISTS procurement_db;
EOF

echo "✅ Databases dropped"

echo ""
echo "=========================================="
echo "Step 4: Creating New Databases"
echo "=========================================="

echo "🏗️  Creating databases with UTF8MB4..."
docker compose exec -T mysql mysql -uroot -p$(cat .secrets/mysql_root_passwd.txt) <<EOF
CREATE DATABASE auth_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE DATABASE asset_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE DATABASE admin_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE DATABASE procurement_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Grant permissions
GRANT ALL PRIVILEGES ON auth_db.* TO 'officework'@'%';
GRANT ALL PRIVILEGES ON asset_db.* TO 'officework'@'%';
GRANT ALL PRIVILEGES ON admin_db.* TO 'officework'@'%';
GRANT ALL PRIVILEGES ON procurement_db.* TO 'officework'@'%';
FLUSH PRIVILEGES;
EOF

echo "✅ Databases created"

echo ""
echo "=========================================="
echo "Step 5: Cleaning Old Migrations"
echo "=========================================="

echo "🧹 Removing old migration files..."
rm -rf services/auth-api/alembic/versions/*.py
rm -rf services/asset-api/alembic/versions/*.py
rm -rf services/admin-api/alembic/versions/*.py
rm -rf services/procurement-api/alembic/versions/*.py

echo "✅ Old migrations removed"

echo ""
echo "=========================================="
echo "Step 6: Generating New Migrations"
echo "=========================================="

echo "📝 Generating auth-api migration..."
docker compose exec -T auth-api alembic revision --autogenerate -m "Initial schema with UUID and slug"

echo "📝 Generating asset-api migration..."
docker compose exec -T asset-api alembic revision --autogenerate -m "Initial schema with UUID and slug"

echo "📝 Generating admin-api migration..."
docker compose exec -T admin-api alembic revision --autogenerate -m "Initial schema with UUID and slug"

echo "📝 Generating procurement-api migration..."
docker compose exec -T procurement-api alembic revision --autogenerate -m "Initial schema with UUID and slug"

echo "✅ Migrations generated"

echo ""
echo "=========================================="
echo "Step 7: Running Migrations"
echo "=========================================="

echo "🚀 Running auth-api migration..."
docker compose exec -T auth-api alembic upgrade head

echo "🚀 Running asset-api migration..."
docker compose exec -T asset-api alembic upgrade head

echo "🚀 Running admin-api migration..."
docker compose exec -T admin-api alembic upgrade head

echo "🚀 Running procurement-api migration..."
docker compose exec -T procurement-api alembic upgrade head

echo "✅ Migrations completed"

echo ""
echo "=========================================="
echo "Step 8: Seeding Initial Data"
echo "=========================================="

echo "🌱 Creating seed data..."

# Create seed data SQL
docker compose exec mysql mysql -uofficework -p$(cat /run/secrets/mysql_user_passwd) auth_db <<'EOF'
-- Insert admin role
INSERT INTO roles (id, slug, name, display_name, description, is_active, is_system_role, version, created_at, updated_at)
VALUES (
    UUID(),
    'admin',
    'admin',
    'Administrator',
    'Full system access',
    TRUE,
    TRUE,
    1,
    NOW(),
    NOW()
);

-- Get the admin role ID
SET @admin_role_id = (SELECT id FROM roles WHERE slug = 'admin');

-- Insert admin user
INSERT INTO users (id, slug, email, username, full_name, hashed_password, user_type, is_active, is_superuser, email_verified, mfa_enabled, failed_login_attempts, require_password_change, role_id, version, created_at, updated_at)
VALUES (
    UUID(),
    'admin',
    'admin@example.com',
    'admin',
    'System Administrator',
    '\$2b\$12\$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY0uktBLLjG0Upi',  -- password: admin123
    'local',
    TRUE,
    TRUE,
    TRUE,
    FALSE,
    0,
    FALSE,
    @admin_role_id,
    1,
    NOW(),
    NOW()
);
EOF

echo "✅ Seed data created"

echo ""
echo "=========================================="
echo "Step 9: Verifying Migration"
echo "=========================================="

echo "🔍 Checking database tables..."
docker compose exec mysql mysql -uofficework -p$(cat /run/secrets/mysql_user_passwd) -e "
SELECT
    'auth_db' as database_name,
    TABLE_NAME,
    TABLE_ROWS
FROM information_schema.TABLES
WHERE TABLE_SCHEMA = 'auth_db'
UNION ALL
SELECT
    'asset_db' as database_name,
    TABLE_NAME,
    TABLE_ROWS
FROM information_schema.TABLES
WHERE TABLE_SCHEMA = 'asset_db'
UNION ALL
SELECT
    'admin_db' as database_name,
    TABLE_NAME,
    TABLE_ROWS
FROM information_schema.TABLES
WHERE TABLE_SCHEMA = 'admin_db'
UNION ALL
SELECT
    'procurement_db' as database_name,
    TABLE_NAME,
    TABLE_ROWS
FROM information_schema.TABLES
WHERE TABLE_SCHEMA = 'procurement_db';
"

echo ""
echo "🔍 Checking admin user..."
docker compose exec mysql mysql -uofficework -p$(cat /run/secrets/mysql_user_passwd) auth_db -e "
SELECT id, slug, email, full_name, is_active FROM users;
"

echo ""
echo "=========================================="
echo "✅ Migration Complete!"
echo "=========================================="
echo ""
echo "📋 Summary:"
echo "  - Database backups saved to: $BACKUP_DIR"
echo "  - All databases recreated with UUID primary keys"
echo "  - All tables have slug fields for URL-friendly identifiers"
echo "  - Admin user created: admin@example.com / admin123"
echo "  - Admin role created with full permissions"
echo ""
echo "💾 Backup Information:"
echo "  - Location: $BACKUP_DIR"
echo "  - auth_db.sql: $(ls -lh $BACKUP_DIR/auth_db.sql 2>/dev/null | awk '{print $5}' || echo 'N/A')"
echo "  - asset_db.sql: $(ls -lh $BACKUP_DIR/asset_db.sql 2>/dev/null | awk '{print $5}' || echo 'N/A')"
echo "  - admin_db.sql: $(ls -lh $BACKUP_DIR/admin_db.sql 2>/dev/null | awk '{print $5}' || echo 'N/A')"
echo "  - procurement_db.sql: $(ls -lh $BACKUP_DIR/procurement_db.sql 2>/dev/null | awk '{print $5}' || echo 'N/A')"
echo ""
echo "🔄 To restore from backup (if needed):"
echo "  docker compose exec mysql mysql -uofficework -p\$(cat /run/secrets/mysql_user_passwd) auth_db < $BACKUP_DIR/auth_db.sql"
echo "  docker compose exec mysql mysql -uofficework -p\$(cat /run/secrets/mysql_user_passwd) asset_db < $BACKUP_DIR/asset_db.sql"
echo "  docker compose exec mysql mysql -uofficework -p\$(cat /run/secrets/mysql_user_passwd) admin_db < $BACKUP_DIR/admin_db.sql"
echo "  docker compose exec mysql mysql -uofficework -p\$(cat /run/secrets/mysql_user_passwd) procurement_db < $BACKUP_DIR/procurement_db.sql"
echo ""
echo "🚀 Next Steps:"
echo "  1. Test login: curl -X POST http://localhost:8001/api/v1/auth/login"
echo "  2. Update Pydantic schemas (id: int → id: str)"
echo "  3. Update API endpoints to support UUID/slug"
echo "  4. Update frontend TypeScript types"
echo "  5. Test all CRUD operations"
echo ""
echo "📚 Documentation:"
echo "  - See: docs/deliveries/UUID_MIGRATION_IMPLEMENTATION_GUIDE.md"
echo "  - See: docs/deliveries/UUID_SLUG_MIGRATION_PLAN.md"
echo ""
