#!/bin/bash
set -e

# Create multiple databases in PostgreSQL
# This script is executed during container initialization

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    -- Create schemas for each microservice
    CREATE SCHEMA IF NOT EXISTS auth_db;
    CREATE SCHEMA IF NOT EXISTS asset_db;
    CREATE SCHEMA IF NOT EXISTS procurement_db;
    CREATE SCHEMA IF NOT EXISTS maintenance_db;
    CREATE SCHEMA IF NOT  EXISTS notification_db;

    -- Grant permissions
    GRANT ALL PRIVILEGES ON SCHEMA auth_db TO $POSTGRES_USER;
    GRANT ALL PRIVILEGES ON SCHEMA asset_db TO $POSTGRES_USER;
    GRANT ALL PRIVILEGES ON SCHEMA procurement_db TO $POSTGRES_USER;
    GRANT ALL PRIVILEGES ON SCHEMA maintenance_db TO $POSTGRES_USER;
    GRANT ALL PRIVILEGES ON SCHEMA notification_db TO $POSTGRES_USER;

    -- Create extensions
    CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
    CREATE EXTENSION IF NOT EXISTS "pg_trgm";

    SELECT 'Databases and schemas initialized successfully!' AS status;
EOSQL

echo "PostgreSQL initialization completed!"
