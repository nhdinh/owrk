#!/bin/bash

# Script to update all services with service discovery

SERVICES=("asset-api" "procurement-api" "admin-api")

for SERVICE in "${SERVICES[@]}"; do
    echo "Updating $SERVICE..."

    # Copy service_discovery.py if not exists
    if [ ! -f "/c/Users/nhdinh/dev/officework/services/$SERVICE/app/core/service_discovery.py" ]; then
        cp /c/Users/nhdinh/dev/officework/services/auth-api/app/core/service_discovery.py \
           /c/Users/nhdinh/dev/officework/services/$SERVICE/app/core/service_discovery.py
        echo "  ✅ Copied service_discovery.py"
    fi

    echo "  ✅ $SERVICE updated"
done

echo "All services updated!"
