-- Create databases for each microservice
CREATE USER 'officework_dbu'@'%' IDENTIFIED BY 'zUP29fs/Kf9fap8nuKv3zloSN1Ftb/IhzCnVlUID7ic=';

CREATE DATABASE IF NOT EXISTS auth_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE DATABASE IF NOT EXISTS asset_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE DATABASE IF NOT EXISTS procurement_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE DATABASE IF NOT EXISTS maintenance_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE DATABASE IF NOT EXISTS notification_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Grant privileges to the application user
GRANT ALL PRIVILEGES ON auth_db.* TO 'officework_dbu'@'%';
GRANT ALL PRIVILEGES ON asset_db.* TO 'officework_dbu'@'%';
GRANT ALL PRIVILEGES ON procurement_db.* TO 'officework_dbu'@'%';
GRANT ALL PRIVILEGES ON maintenance_db.* TO 'officework_dbu'@'%';
GRANT ALL PRIVILEGES ON notification_db.* TO 'officework_dbu'@'%';

-- Flush privileges to apply changes
FLUSH PRIVILEGES;

SELECT 'Databases initialized successfully!' AS status;
