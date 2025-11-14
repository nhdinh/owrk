-- Seed Permissions Script
-- Run this script to populate permissions and assign them to the admin role
-- Usage: mysql -u<user> -p<password> auth_db < seed_permissions.sql

-- Insert permissions if they don't exist (using IGNORE to skip duplicates)
INSERT IGNORE INTO permissions (id, slug, name, resource, action, description, created_at, updated_at)
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
  (UUID(), 'department-delete', 'department:delete', 'department', 'delete', 'Delete departments', NOW(), NOW());

-- Assign all permissions to admin role
INSERT IGNORE INTO role_permissions (role_id, permission_id)
SELECT
  (SELECT id FROM roles WHERE name = 'admin') as role_id,
  id as permission_id
FROM permissions;

-- Display results
SELECT 'Permissions seeded successfully!' as status;
SELECT COUNT(*) as total_permissions FROM permissions;
SELECT
  r.name as role_name,
  COUNT(rp.permission_id) as assigned_permissions
FROM roles r
LEFT JOIN role_permissions rp ON r.id = rp.role_id
WHERE r.name = 'admin'
GROUP BY r.id, r.name;
