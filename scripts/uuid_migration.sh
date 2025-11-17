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

echo "🌱 Creating default roles..."

# Create roles first
docker compose exec -T mysql mysql -uofficework -p$(cat .secrets/mysql_user_passwd.txt) auth_db <<'EOF'
-- Insert default roles
INSERT INTO roles (id, slug, name, display_name, description, is_active, is_system_role, version, created_at, updated_at)
VALUES
  (UUID(), 'admin', 'admin', 'Administrator', 'Full system access with all permissions', TRUE, TRUE, 1, NOW(), NOW()),
  (UUID(), 'manager', 'manager', 'Manager', 'Department manager with approval rights', TRUE, TRUE, 1, NOW(), NOW()),
  (UUID(), 'user', 'user', 'Standard User', 'Regular user with basic permissions', TRUE, TRUE, 1, NOW(), NOW()),
  (UUID(), 'viewer', 'viewer', 'Viewer', 'Read-only access to system', TRUE, TRUE, 1, NOW(), NOW());
EOF

echo "✅ Default roles created (admin, manager, user, viewer)"

echo "🌱 Creating permissions..."

# Create permissions
docker compose exec -T mysql mysql -uofficework -p$(cat .secrets/mysql_user_passwd.txt) auth_db <<'EOF'
-- Insert permissions
INSERT INTO permissions (id, slug, name, resource, action, description, created_at, updated_at)
VALUES
  -- User permissions
  (UUID(), 'user-read', 'user:read', 'user', 'read', 'View users', NOW(), NOW()),
  (UUID(), 'user-create', 'user:create', 'user', 'create', 'Create users', NOW(), NOW()),
  (UUID(), 'user-update', 'user:update', 'user', 'update', 'Update users', NOW(), NOW()),
  (UUID(), 'user-delete', 'user:delete', 'user', 'delete', 'Delete users', NOW(), NOW()),

  -- Role permissions
  (UUID(), 'role-read', 'role:read', 'role', 'read', 'View roles', NOW(), NOW()),
  (UUID(), 'role-create', 'role:create', 'role', 'create', 'Create roles', NOW(), NOW()),
  (UUID(), 'role-update', 'role:update', 'role', 'update', 'Update roles', NOW(), NOW()),
  (UUID(), 'role-delete', 'role:delete', 'role', 'delete', 'Delete roles', NOW(), NOW()),

  -- Asset permissions
  (UUID(), 'asset-read', 'asset:read', 'asset', 'read', 'View assets', NOW(), NOW()),
  (UUID(), 'asset-create', 'asset:create', 'asset', 'create', 'Create assets', NOW(), NOW()),
  (UUID(), 'asset-update', 'asset:update', 'asset', 'update', 'Update assets', NOW(), NOW()),
  (UUID(), 'asset-delete', 'asset:delete', 'asset', 'delete', 'Delete assets', NOW(), NOW()),

  -- Assignment permissions
  (UUID(), 'assignment-read', 'assignment:read', 'assignment', 'read', 'View assignments', NOW(), NOW()),
  (UUID(), 'assignment-create', 'assignment:create', 'assignment', 'create', 'Create assignments', NOW(), NOW()),
  (UUID(), 'assignment-update', 'assignment:update', 'assignment', 'update', 'Update assignments', NOW(), NOW()),
  (UUID(), 'assignment-delete', 'assignment:delete', 'assignment', 'delete', 'Delete assignments', NOW(), NOW()),

  -- Category permissions
  (UUID(), 'category-read', 'category:read', 'category', 'read', 'View categories', NOW(), NOW()),
  (UUID(), 'category-create', 'category:create', 'category', 'create', 'Create categories', NOW(), NOW()),
  (UUID(), 'category-update', 'category:update', 'category', 'update', 'Update categories', NOW(), NOW()),
  (UUID(), 'category-delete', 'category:delete', 'category', 'delete', 'Delete categories', NOW(), NOW()),

  -- Department permissions
  (UUID(), 'department-read', 'department:read', 'department', 'read', 'View departments', NOW(), NOW()),
  (UUID(), 'department-create', 'department:create', 'department', 'create', 'Create departments', NOW(), NOW()),
  (UUID(), 'department-update', 'department:update', 'department', 'update', 'Update departments', NOW(), NOW()),
  (UUID(), 'department-delete', 'department:delete', 'department', 'delete', 'Delete departments', NOW(), NOW()),

  -- Procurement permissions
  (UUID(), 'vendor-read', 'vendor:read', 'vendor', 'read', 'View vendors', NOW(), NOW()),
  (UUID(), 'vendor-create', 'vendor:create', 'vendor', 'create', 'Create vendors', NOW(), NOW()),
  (UUID(), 'vendor-update', 'vendor:update', 'vendor', 'update', 'Update vendors', NOW(), NOW()),
  (UUID(), 'vendor-delete', 'vendor:delete', 'vendor', 'delete', 'Delete vendors', NOW(), NOW()),
  (UUID(), 'purchase-request-read', 'purchase_request:read', 'purchase_request', 'read', 'View purchase requests', NOW(), NOW()),
  (UUID(), 'purchase-request-create', 'purchase_request:create', 'purchase_request', 'create', 'Create purchase requests', NOW(), NOW()),
  (UUID(), 'purchase-request-update', 'purchase_request:update', 'purchase_request', 'update', 'Update purchase requests', NOW(), NOW()),
  (UUID(), 'purchase-request-delete', 'purchase_request:delete', 'purchase_request', 'delete', 'Delete purchase requests', NOW(), NOW()),
  (UUID(), 'purchase-request-approve', 'purchase_request:approve', 'purchase_request', 'approve', 'Approve purchase requests', NOW(), NOW()),
  (UUID(), 'purchase-order-read', 'purchase_order:read', 'purchase_order', 'read', 'View purchase orders', NOW(), NOW()),
  (UUID(), 'purchase-order-create', 'purchase_order:create', 'purchase_order', 'create', 'Create purchase orders', NOW(), NOW()),
  (UUID(), 'purchase-order-update', 'purchase_order:update', 'purchase_order', 'update', 'Update purchase orders', NOW(), NOW()),
  (UUID(), 'purchase-order-delete', 'purchase_order:delete', 'purchase_order', 'delete', 'Delete purchase orders', NOW(), NOW());
EOF

echo "✅ Permissions created (36 permissions across all modules)"

echo "🌱 Assigning permissions to roles..."

# Assign permissions to roles
docker compose exec -T mysql mysql -uofficework -p$(cat .secrets/mysql_user_passwd.txt) auth_db <<'EOF'
-- Assign all permissions to admin role
INSERT INTO role_permissions (role_id, permission_id)
SELECT
  (SELECT id FROM roles WHERE slug = 'admin') as role_id,
  id as permission_id
FROM permissions;

-- Assign read permissions and some write permissions to manager role
INSERT INTO role_permissions (role_id, permission_id)
SELECT
  (SELECT id FROM roles WHERE slug = 'manager') as role_id,
  id as permission_id
FROM permissions
WHERE action IN ('read', 'create', 'update', 'approve');

-- Assign read and limited write permissions to user role
INSERT INTO role_permissions (role_id, permission_id)
SELECT
  (SELECT id FROM roles WHERE slug = 'user') as role_id,
  id as permission_id
FROM permissions
WHERE action IN ('read', 'create')
  AND resource NOT IN ('user', 'role');

-- Assign only read permissions to viewer role
INSERT INTO role_permissions (role_id, permission_id)
SELECT
  (SELECT id FROM roles WHERE slug = 'viewer') as role_id,
  id as permission_id
FROM permissions
WHERE action = 'read';
EOF

echo "✅ Role permissions assigned"

echo "🌱 Creating default admin user..."

# Create admin user
docker compose exec -T mysql mysql -uofficework -p$(cat .secrets/mysql_user_passwd.txt) auth_db <<'EOF'
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
    '\$2b\$12\$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY0uktBLLjG0Upi',
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

echo "✅ Admin user created (admin@example.com / admin123)"

echo "🌱 Displaying seeded data summary..."

# Display summary
docker compose exec -T mysql mysql -uofficework -p$(cat .secrets/mysql_user_passwd.txt) auth_db <<'EOF'
-- Roles Created
SELECT slug, name, display_name, is_system_role FROM roles ORDER BY slug;

-- Total Permissions
SELECT COUNT(*) as total_permissions FROM permissions;

-- Permissions by Role
SELECT
  r.slug as role,
  r.display_name as role_name,
  COUNT(rp.permission_id) as permission_count
FROM roles r
LEFT JOIN role_permissions rp ON r.id = rp.role_id
GROUP BY r.id, r.slug, r.display_name
ORDER BY r.slug;

-- Admin User
SELECT slug, email, full_name, is_active, is_superuser FROM users WHERE slug = 'admin';
EOF

echo "✅ All seed data created successfully"

echo ""
echo "=========================================="
echo "Step 9: Verifying Migration"
echo "=========================================="

echo "🔍 Checking database tables..."
docker compose exec mysql mysql -uofficework -p$(cat .secrets/mysql_user_passwd.txt) -e "
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
docker compose exec mysql mysql -uofficework -p$(cat .secrets/mysql_user_passwd.txt) auth_db -e "
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
echo ""
echo "  🔐 Seeded Data:"
echo "  - 4 System Roles: admin, manager, user, viewer"
echo "  - 36 Permissions across all modules (user, role, asset, procurement, etc.)"
echo "  - Admin user: admin@example.com / admin123 (full permissions)"
echo "  - Role-based access control configured"
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
