#!/bin/sh
set -e

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

# check if APP_ENV variable is set to 'development', then set root password to never expire
if [ "$APP_ENV" = "development" ]; then
    echo "Development environment detected: setting root password to never expire."
    EXPIRE_NEVER="ALTER USER 'root'@'%' PASSWORD EXPIRE NEVER;" # "PASSWORD EXPIRE NEVER"
else
    EXPIRE_NEVER=""
fi

# Create databases for each microservice
echo "-- Create databases for each microservice
ALTER USER 'root'@'%' IDENTIFIED BY '${MYSQL_ROOT_PASSWORD}';
ALTER USER 'root'@'localhost' IDENTIFIED BY '${MYSQL_ROOT_PASSWORD}';
CREATE USER IF NOT EXISTS '${MYSQL_USER}'@'%' IDENTIFIED BY '${MYSQL_PASSWORD}';

${EXPIRE_NEVER}

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

SELECT 'Databases initialized successfully!' AS status;" >> /app/init.sql

echo "SQL initialization script created at /app/init.sql"

# Copy init.sql to the Docker entrypoint directory
mv /app/init.sql /docker-entrypoint-initdb.d/

# set MYSQL_ROOT_PASSWORD to empty to avoid issues with entrypoint script
exec /entrypoint.sh "$@"
