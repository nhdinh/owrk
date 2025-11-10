#!/bin/bash
set -e

# Read password from secrets file if exists, otherwise use default
if [ -f /run/secrets/mysql_root_passwd ]; then
    export MYSQL_ROOT_PASSWORD=$(cat /run/secrets/mysql_root_passwd | tr -d '[:space:]')
else
    export MYSQL_ROOT_PASSWORD=$(openssl rand -base64 32)
fi

if [ -f /run/secrets/mysql_user_passwd ]; then
    export MYSQL_PASSWORD=$(cat /run/secrets/mysql_user_passwd | tr -d '[:space:]')
else
    export MYSQL_PASSWORD=$(openssl rand -base64 32)
fi

echo "Creating SQL initialization script"

# Wait for MySQL to be ready
# until mysql -u root -p"${MYSQL_ROOT_PASSWORD}" -e "SELECT 1" &>/dev/null; do
#     echo "Waiting for MySQL to be ready..."
#     sleep 2
# done

# Create databases for each microservice
echo "-- Create databases for each microservice
CREATE USER '${MYSQL_USER}'@'%' IDENTIFIED BY '${MYSQL_PASSWORD}';

CREATE DATABASE IF NOT EXISTS auth_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE DATABASE IF NOT EXISTS asset_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE DATABASE IF NOT EXISTS procurement_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE DATABASE IF NOT EXISTS maintenance_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE DATABASE IF NOT EXISTS notification_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE DATABASE IF NOT EXISTS admin_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Grant privileges to the application user
GRANT ALL PRIVILEGES ON auth_db.* TO '${MYSQL_USER}'@'%';
GRANT ALL PRIVILEGES ON asset_db.* TO '${MYSQL_USER}'@'%';
GRANT ALL PRIVILEGES ON procurement_db.* TO '${MYSQL_USER}'@'%';
GRANT ALL PRIVILEGES ON maintenance_db.* TO '${MYSQL_USER}'@'%';
GRANT ALL PRIVILEGES ON notification_db.* TO '${MYSQL_USER}'@'%';
GRANT ALL PRIVILEGES ON admin_db.* TO '${MYSQL_USER}'@'%';

-- Flush privileges to apply changes
FLUSH PRIVILEGES;

SELECT 'Databases initialized successfully!' AS status;" > /docker-entrypoint-initdb.d/init.sql

# mv /tmp/init.sql /docker-entrypoint-initdb.d/

sh /entrypoint.sh
