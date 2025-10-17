-- User ${DB_USER} is automatically created by PostgreSQL from POSTGRES_USER
-- Just update the password
ALTER USER ${DB_USER} WITH PASSWORD '${DB_PASSWD}';

-- Create schemas for each microservice
CREATE SCHEMA IF NOT EXISTS auth_db;
CREATE SCHEMA IF NOT EXISTS asset_db;
CREATE SCHEMA IF NOT EXISTS procurement_db;
CREATE SCHEMA IF NOT EXISTS maintenance_db;
CREATE SCHEMA IF NOT EXISTS notification_db;

-- Grant privileges on schemas
GRANT ALL PRIVILEGES ON SCHEMA auth_db TO ${DB_USER};
GRANT ALL PRIVILEGES ON SCHEMA asset_db TO ${DB_USER};
GRANT ALL PRIVILEGES ON SCHEMA procurement_db TO ${DB_USER};
GRANT ALL PRIVILEGES ON SCHEMA maintenance_db TO ${DB_USER};
GRANT ALL PRIVILEGES ON SCHEMA notification_db TO ${DB_USER};

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";