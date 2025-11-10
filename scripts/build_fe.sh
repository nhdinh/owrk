#!/bin/bash

services=(
    "shared-components:shared-components"
    "auth-frontend:auth-fe"
    "asset-frontend:asset-fe"
    "dashboard-frontend:dashboard-fe"
    "procurement-frontend:procurement-fe"
    "admin-frontend:admin-fe"
)

# Parse arguments
TARGET_SERVICE=""
FULL_BUILD=false

while [[ $# -gt 0 ]]; do
  case $1 in
    --full)
      FULL_BUILD=true
      shift
      ;;
    *)
      if [[ -z "$TARGET_SERVICE" ]]; then
        TARGET_SERVICE="$1"
      else
        echo "Error: Unknown argument '$1'" >&2
        echo "Usage: $0 [service_name] [--full]" >&2
        echo "       $0              - Build all services" >&2
        echo "       $0 auth-frontend - Build only auth-frontend" >&2
        echo "       $0 --full       - Full rebuild all services with npm install" >&2
        exit 1
      fi
      shift
      ;;
  esac
done

# export GENERATE_SOURCEMAP=true

# Full build script with npm install
# Use this for first-time setup or after dependency changes
# For faster builds when dependencies haven't changed, use build_fe_fast.sh

if [[ -n "$TARGET_SERVICE" ]]; then
    echo "=== Building Frontend: $TARGET_SERVICE ==="
else
    echo "=== Building All Frontends ==="
fi
echo ""

PACKAGES_HASH_FILE=$(pwd)/scripts/.packages_hashes
SERVICE_BASE_PATH=$(pwd)/services/

build_service() {
    SERVICE_NAME=$1
    CONTAINER_NAME=$2

    echo "🚀 Building ${SERVICE_NAME}..."
    cd ${SERVICE_BASE_PATH}/${SERVICE_NAME}

    # read hash of package.json to determine if dependencies have changed
    package_hash=$(md5sum package.json | awk '{ print $1 }')

    # read stored hash
    stored_hash=""
    if [ -f ${PACKAGES_HASH_FILE} ]; then
        stored_hash=$(grep "^${SERVICE_NAME}:" ${PACKAGES_HASH_FILE} | cut -d':' -f2)
    fi


    # Determine if we should do full install
    should_install=false
    if [[ "$FULL_BUILD" == "true" ]]; then
        echo "Full build requested. Proceeding with complete reinstall."
        should_install=true
    elif [ "$package_hash" != "$stored_hash" ]; then
        echo "Dependencies changed or no stored hash. Proceeding with full install."
        should_install=true
    else
        echo "Dependencies unchanged. Skipping npm install."
    fi

    # Clean dist directory
    rm -rf ./dist

    # Install if needed
    if [[ "$should_install" == "true" ]]; then
        rm -rf ./node_modules
        rm -rf ./package-lock.json
        npm install
    fi

    # Build
    npm run build

    # Deploy to container
    if [[ $? -eq 0 ]]; then
        echo "Deploying ${SERVICE_NAME}..."
        docker cp ./dist/assets ${CONTAINER_NAME}:/usr/share/nginx/html/ 2>/dev/null || echo "Note: dist/assets not found or container not running"
        docker cp ./dist/index.html ${CONTAINER_NAME}:/usr/share/nginx/html/ 2>/dev/null || echo "Note: dist/index.html not found or container not running"
        echo "✓ ${SERVICE_NAME} deployed"
    else
        echo "✗ ${SERVICE_NAME} build failed"
        return 1
    fi
    echo ""

    # update stored hash
    grep -v "^${SERVICE_NAME}:" ${PACKAGES_HASH_FILE} > ${PACKAGES_HASH_FILE}.tmp 2>/dev/null || true
    echo "${SERVICE_NAME}:${package_hash}" >> ${PACKAGES_HASH_FILE}.tmp
    mv ${PACKAGES_HASH_FILE}.tmp ${PACKAGES_HASH_FILE}
}

# Build services
if [[ -n "$TARGET_SERVICE" ]]; then
    # Build single service
    found=false
    for service in "${services[@]}"; do
        IFS=":" read -r SERVICE_NAME CONTAINER_NAME <<< "$service"
        if [[ "$SERVICE_NAME" == "$TARGET_SERVICE" ]]; then
            found=true
            build_service $SERVICE_NAME $CONTAINER_NAME
            break
        fi
    done

    if [[ "$found" == "false" ]]; then
        echo "Error: Service '$TARGET_SERVICE' not found." >&2
        echo "Available services:" >&2
        for service in "${services[@]}"; do
            IFS=":" read -r SERVICE_NAME CONTAINER_NAME <<< "$service"
            echo "  - $SERVICE_NAME" >&2
        done
        exit 1
    fi

    echo "=== Frontend '$TARGET_SERVICE' built and deployed successfully! ==="
else
    # Build all services
    for service in "${services[@]}"; do
        IFS=":" read -r SERVICE_NAME CONTAINER_NAME <<< "$service"
        build_service $SERVICE_NAME $CONTAINER_NAME
    done

    echo "=== All frontends built and deployed successfully! ==="
fi
echo ""
echo "Note: To apply changes, hard refresh your browser (Ctrl+Shift+R or Cmd+Shift+R)"