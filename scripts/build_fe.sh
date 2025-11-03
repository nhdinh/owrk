#!/bin/bash

services=(
    "shared-components:shared-components"
    "auth-frontend:auth-fe"
    "asset-frontend:asset-fe"
    "dashboard-frontend:dashboard-fe"
)

if [[ $# -gt 2 ]]; then
  echo "Usage: $0 <service_name> [--full]: for full build with node_modules reinstallation" >&2
  echo "       $0: for build all the services" >&2
  exit 1
fi

# export GENERATE_SOURCEMAP=true

# Full build script with npm install
# Use this for first-time setup or after dependency changes
# For faster builds when dependencies haven't changed, use build_fe_fast.sh

echo "=== Full Frontend Build (with npm install) ==="
echo ""

PACKAGES_HASH_FILE=$(pwd)/scripts/.packages_hashes
SERVICE_BASE_PATH=$(pwd)/services/

build_service() {
    SERVICE_NAME=$1
    CONTAINER_NAME=$2

    
    echo "Building ${SERVICE_NAME}..."
    cd ${SERVICE_BASE_PATH}/${SERVICE_NAME}

    # read hash of package.json to determine if dependencies have changed
    package_hash=$(md5sum package.json | awk '{ print $1 }')

    # read stored hash
    stored_hash=""
    if [ -f ${PACKAGES_HASH_FILE} ]; then
        stored_hash=$(grep "^${SERVICE_NAME}:" ${PACKAGES_HASH_FILE} | cut -d':' -f2)
    fi


    # if hashes match, skip npm install
    if [ "$package_hash" == "$stored_hash" ]; then
        echo "Dependencies unchanged. Skipping npm install."
        rm -rf ./dist
    else
        echo "Dependencies changed or no stored hash. Proceeding with full install."

        rm -rf ./dist
        rm -rf ./node_modules
        rm -rf ./package-lock.json

        npm install 
    fi

    npm run build

    echo "Deploying auth-frontend..."
    docker cp ./dist/assets ${CONTAINER_NAME}:/usr/share/nginx/html/
    docker cp ./dist/index.html ${CONTAINER_NAME}:/usr/share/nginx/html/
    echo "✓ ${SERVICE_NAME} deployed"
    echo ""

    # update stored hash
    grep -v "^${SERVICE_NAME}:" ${PACKAGES_HASH_FILE} > ${PACKAGES_HASH_FILE}.tmp || true
    echo "${SERVICE_NAME}:${package_hash}" >> ${PACKAGES_HASH_FILE}.tmp
    mv ${PACKAGES_HASH_FILE}.tmp ${PACKAGES_HASH_FILE}
}

for service in "${services[@]}"; do
    IFS=":" read -r SERVICE_NAME CONTAINER_NAME <<< "$service"
    build_service $SERVICE_NAME $CONTAINER_NAME
done

echo "=== All frontends built and deployed successfully! ==="
echo ""
echo "Note: To apply changes, hard refresh your browser (Ctrl+Shift+R or Cmd+Shift+R)"