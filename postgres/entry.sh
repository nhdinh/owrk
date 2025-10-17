#!/bin/bash

# This script will run on entrypoint and modify the init.sql script
# Then put the script into docker-init for creating databases for the first time

# Read password from secrets file if exists, otherwise use default
if [ -f /run/secrets/postgres_passwd ]; then
    export POSTGRES_PASSWORD=$(cat /run/secrets/postgres_passwd)
else
    export POSTGRES_PASSWORD="secret123"
fi

# Set default user if not provided
export POSTGRES_USER="${POSTGRES_USR:-admin}"
export POSTGRES_DB="${POSTGRES_DB:-asset_management}"

# Prepare init.sql script
sed -i -e 's/${DB_USER}/'"$POSTGRES_USER"'/g' ./init.sql
sed -i -e 's/${DB_PASSWD}/'"$POSTGRES_PASSWORD"'/g' ./init.sql

cp ./init.sql /docker-entrypoint-initdb.d/

exec /usr/local/bin/docker-entrypoint.sh "$@"