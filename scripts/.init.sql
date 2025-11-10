-- Create databases for each microservice
CREATE USER 'officework'@'%' IDENTIFIED BY '9JgA/WrYJOUemfNq49aGNIYHZwnJfuW8Yu/3w0BP14g=';

CREATE DATABASE IF NOT EXISTS auth_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE DATABASE IF NOT EXISTS asset_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE DATABASE IF NOT EXISTS procurement_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE DATABASE IF NOT EXISTS maintenance_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE DATABASE IF NOT EXISTS notification_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE DATABASE IF NOT EXISTS admin_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Grant privileges to the application user
GRANT ALL PRIVILEGES ON auth_db.* TO 'officework'@'%';
GRANT ALL PRIVILEGES ON asset_db.* TO 'officework'@'%';
GRANT ALL PRIVILEGES ON procurement_db.* TO 'officework'@'%';
GRANT ALL PRIVILEGES ON maintenance_db.* TO 'officework'@'%';
GRANT ALL PRIVILEGES ON notification_db.* TO 'officework'@'%';
GRANT ALL PRIVILEGES ON admin_db.* TO 'officework'@'%';

-- Flush privileges to apply changes
FLUSH PRIVILEGES;

SELECT 'Databases initialized successfully!' AS status;
