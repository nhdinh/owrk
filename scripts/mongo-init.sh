#!/bin/bash
# MongoDB initialization script to read password from secrets file

set -e

# Read password from secrets file if it exists
if [ -f /run/secrets/mongo_passwd ]; then
    export MONGO_INITDB_ROOT_PASSWORD=$(cat /run/secrets/mongo_passwd)
    echo "✅ MongoDB password loaded from secrets file"
else
    echo "⚠️ Warning: Secret file not found, using default password"
fi

# Execute the original MongoDB entrypoint
exec docker-entrypoint.sh "$@"
