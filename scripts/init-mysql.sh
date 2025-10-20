#!/bin/bash
set -e


# Read password from secrets file if exists, otherwise use default
if [ -f /run/secrets/mysql_passwd ]; then
    export MYSQL_ROOT_PASSWORD=$(cat /run/secrets/mysql_passwd)
    export MYSQL_PASSWORD=$(cat /run/secrets/mysql_passwd)
else
    export MYSQL_ROOT_PASSWORD="secret123"
    export MYSQL_PASSWORD="secret123"
fi


echo "Starting MySQL database initialization..."

# Wait for MySQL to be ready
until mysql -u root -p"${MYSQL_ROOT_PASSWORD}" -e "SELECT 1" &>/dev/null; do
    echo "Waiting for MySQL to be ready..."
    sleep 2
done

# Create databases for each microservice
mysql -u root -p"${MYSQL_ROOT_PASSWORD}" <<-EOSQL
    -- Create databases for each microservice
    CREATE DATABASE IF NOT EXISTS auth_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
    CREATE DATABASE IF NOT EXISTS asset_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
    CREATE DATABASE IF NOT EXISTS procurement_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
    CREATE DATABASE IF NOT EXISTS maintenance_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
    CREATE DATABASE IF NOT EXISTS notification_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

    -- Grant privileges to the application user
    GRANT ALL PRIVILEGES ON auth_db.* TO '${MYSQL_USER}'@'%';
    GRANT ALL PRIVILEGES ON asset_db.* TO '${MYSQL_USER}'@'%';
    GRANT ALL PRIVILEGES ON procurement_db.* TO '${MYSQL_USER}'@'%';
    GRANT ALL PRIVILEGES ON maintenance_db.* TO '${MYSQL_USER}'@'%';
    GRANT ALL PRIVILEGES ON notification_db.* TO '${MYSQL_USER}'@'%';

    -- Flush privileges to apply changes
    FLUSH PRIVILEGES;

    SELECT 'Databases initialized successfully!' AS status;
EOSQL

echo "MySQL initialization completed!"
