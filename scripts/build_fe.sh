#!/bin/bash

export GENERATE_SOURCEMAP=true

# Full build script with npm install
# Use this for first-time setup or after dependency changes
# For faster builds when dependencies haven't changed, use build_fe_fast.sh

echo "=== Full Frontend Build (with npm install) ==="
echo ""

# Build and deploy shared-components (Module Federation host)
echo "Building shared-components..."
cd ./services/shared-components
echo "Installing dependencies..."
rm -rf ./dist
npm install 
npm run build

echo "Deploying shared-components..."
docker cp ./dist/assets shared-components:/usr/share/nginx/html/
docker cp ./dist/index.html shared-components:/usr/share/nginx/html/
echo "✓ shared-components deployed"
echo ""

# Build and deploy auth-frontend
echo "Building auth-frontend..."
cd ../auth-frontend
echo "Installing dependencies..."
rm -rf ./dist
npm install
npm run build

echo "Deploying auth-frontend..."
docker cp ./dist/assets auth-fe:/usr/share/nginx/html/
docker cp ./dist/index.html auth-fe:/usr/share/nginx/html/
echo "✓ auth-frontend deployed"
echo ""

# Build and deploy asset-frontend
echo "Building asset-frontend..."
cd ../asset-frontend
rm -rf ./dist
npm run build

echo "Deploying asset-frontend..."
docker cp ./dist/assets asset-fe:/usr/share/nginx/html/
docker cp ./dist/index.html asset-fe:/usr/share/nginx/html/
echo "✓ asset-frontend deployed"
echo ""

# Build and deploy dashboard-frontend
echo "Building dashboard-frontend..."
cd ../dashboard-frontend
rm -rf ./dist
npm run build 

echo "Deploying dashboard-frontend..."
docker cp ./dist/assets dashboard-fe:/usr/share/nginx/html/
docker cp ./dist/index.html dashboard-fe:/usr/share/nginx/html/
echo "✓ dashboard-frontend deployed"
echo ""

echo "=== All frontends built and deployed successfully! ==="
echo ""
echo "Note: To apply changes, hard refresh your browser (Ctrl+Shift+R or Cmd+Shift+R)"
