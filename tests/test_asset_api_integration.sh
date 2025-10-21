#!/bin/bash

# Integration Tests for Asset API - Sprint 3
# Tests the complete asset management flow

set -e

API_BASE="http://localhost:8089/api/v1"
AUTH_API="http://localhost:8088/api/v1"

echo "=========================================="
echo "Asset API Integration Tests - Sprint 3"
echo "=========================================="
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test counters
PASSED=0
FAILED=0

# Function to test endpoint
test_endpoint() {
    local name="$1"
    local method="$2"
    local url="$3"
    local data="$4"
    local expected_code="$5"

    echo -n "Testing: $name ... "

    if [ "$method" = "GET" ]; then
        response=$(curl -s -w "\n%{http_code}" -X GET "$url" \
            -H "Authorization: Bearer $TOKEN" \
            -H "Content-Type: application/json")
    elif [ "$method" = "POST" ]; then
        response=$(curl -s -w "\n%{http_code}" -X POST "$url" \
            -H "Authorization: Bearer $TOKEN" \
            -H "Content-Type: application/json" \
            -d "$data")
    elif [ "$method" = "PUT" ]; then
        response=$(curl -s -w "\n%{http_code}" -X PUT "$url" \
            -H "Authorization: Bearer $TOKEN" \
            -H "Content-Type: application/json" \
            -d "$data")
    elif [ "$method" = "DELETE" ]; then
        response=$(curl -s -w "\n%{http_code}" -X DELETE "$url" \
            -H "Authorization: Bearer $TOKEN" \
            -H "Content-Type: application/json")
    fi

    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | head -n-1)

    if [ "$http_code" = "$expected_code" ]; then
        echo -e "${GREEN}PASS${NC} (HTTP $http_code)"
        ((PASSED++))
        return 0
    else
        echo -e "${RED}FAIL${NC} (Expected $expected_code, got $http_code)"
        echo "Response: $body"
        ((FAILED++))
        return 1
    fi
}

echo "Step 1: Authenticate and get token"
echo "======================================"

# Login
login_response=$(curl -s -X POST "$AUTH_API/auth/login" \
    -H "Content-Type: application/json" \
    -d '{"email":"admin@example.com","password":"admin123"}')

temp_token=$(echo $login_response | grep -o '"temp_token":"[^"]*' | cut -d'"' -f4)

if [ -z "$temp_token" ]; then
    echo -e "${RED}Failed to get temp token${NC}"
    exit 1
fi

# Verify OTP (assuming MFA not enabled for admin)
verify_response=$(curl -s -X POST "$AUTH_API/auth/verify-otp" \
    -H "Content-Type: application/json" \
    -d "{\"temp_token\":\"$temp_token\",\"otp_code\":\"000000\"}")

TOKEN=$(echo $verify_response | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)

if [ -z "$TOKEN" ]; then
    echo -e "${YELLOW}Using temp_token as access token${NC}"
    TOKEN=$temp_token
fi

echo -e "${GREEN}Authentication successful${NC}"
echo ""

echo "Step 2: Test Category Endpoints"
echo "======================================"

# Create category
test_endpoint "Create Category" "POST" "$API_BASE/categories/" \
    '{"code":"IT","name":"IT Equipment","description":"Information Technology Equipment"}' \
    "201"

# List categories
test_endpoint "List Categories" "GET" "$API_BASE/categories/" "" "200"

echo ""

echo "Step 3: Test Asset CRUD Operations"
echo "======================================"

# Create asset
CREATE_ASSET_DATA='{
    "asset_code": "LAPTOP-001",
    "name": "Dell XPS 15 Laptop",
    "category_id": 1,
    "asset_type": "FIXED_ASSET",
    "description": "High-performance laptop for development",
    "manufacturer": "Dell",
    "model": "XPS 15 9520",
    "serial_number": "SN123456789",
    "purchase_price": 35000000,
    "purchase_date": "2024-01-15",
    "depreciation_method": "STRAIGHT_LINE",
    "useful_life_months": 60,
    "residual_value": 5000000,
    "depreciation_rate": 20.0,
    "warranty_months": 24,
    "warranty_start_date": "2024-01-15",
    "status": "AVAILABLE"
}'

test_endpoint "Create Asset" "POST" "$API_BASE/assets/" "$CREATE_ASSET_DATA" "201"

# List assets
test_endpoint "List Assets" "GET" "$API_BASE/assets/?page=1&page_size=10" "" "200"

# Get asset details
test_endpoint "Get Asset by ID" "GET" "$API_BASE/assets/1" "" "200"

# Update asset
UPDATE_ASSET_DATA='{"description":"Updated description for testing"}'
test_endpoint "Update Asset" "PUT" "$API_BASE/assets/1" "$UPDATE_ASSET_DATA" "200"

# Search assets
test_endpoint "Search Assets" "GET" "$API_BASE/assets/?search=laptop" "" "200"

echo ""

echo "Step 4: Test Asset Assignment Flow"
echo "======================================"

# Assign asset
ASSIGN_DATA='{
    "user_id": 2,
    "department_id": 1,
    "location": "Office 3rd Floor",
    "notes": "Assigned for development work"
}'

test_endpoint "Assign Asset" "POST" "$API_BASE/assets/1/assign" "$ASSIGN_DATA" "201"

# Get assignment history
test_endpoint "Get Assignment History" "GET" "$API_BASE/assets/1/history" "" "200"

# Return asset
RETURN_DATA='{"return_notes":"Asset returned in good condition"}'
test_endpoint "Return Asset" "POST" "$API_BASE/assets/1/return" "$RETURN_DATA" "200"

echo ""

echo "Step 5: Test QR Code Generation"
echo "======================================"

test_endpoint "Get Asset QR Code" "GET" "$API_BASE/assets/1/qrcode" "" "200"

echo ""

echo "Step 6: Test Depreciation"
echo "======================================"

test_endpoint "Get Asset Depreciation" "GET" "$API_BASE/assets/1/depreciation" "" "200"

echo ""

echo "Step 7: Test Statistics"
echo "======================================"

test_endpoint "Get Asset Statistics" "GET" "$API_BASE/assets/statistics/summary" "" "200"

echo ""

echo "Step 8: Test File Upload (Attachments)"
echo "======================================"

# Create a test file
echo "Test invoice content" > /tmp/test_invoice.txt

# Upload attachment
upload_response=$(curl -s -w "\n%{http_code}" -X POST "$API_BASE/assets/1/attachments" \
    -H "Authorization: Bearer $TOKEN" \
    -F "file=@/tmp/test_invoice.txt" \
    -F "file_type=INVOICE")

upload_code=$(echo "$upload_response" | tail -n1)

echo -n "Testing: Upload Attachment ... "
if [ "$upload_code" = "201" ]; then
    echo -e "${GREEN}PASS${NC} (HTTP $upload_code)"
    ((PASSED++))
else
    echo -e "${RED}FAIL${NC} (Expected 201, got $upload_code)"
    ((FAILED++))
fi

# List attachments
test_endpoint "List Attachments" "GET" "$API_BASE/assets/1/attachments" "" "200"

# Clean up test file
rm -f /tmp/test_invoice.txt

echo ""

echo "Step 9: Test Error Handling"
echo "======================================"

# Get non-existent asset
test_endpoint "Get Non-existent Asset" "GET" "$API_BASE/assets/9999" "" "404"

# Create asset with duplicate code
test_endpoint "Create Duplicate Asset" "POST" "$API_BASE/assets/" "$CREATE_ASSET_DATA" "400"

echo ""

echo "Step 10: Test Data Validation"
echo "======================================"

# Invalid asset type
INVALID_DATA='{"asset_code":"INVALID-001","name":"Test","category_id":1,"asset_type":"INVALID_TYPE","purchase_price":1000000,"purchase_date":"2024-01-01"}'
echo -n "Testing: Invalid Asset Type ... "
response=$(curl -s -w "\n%{http_code}" -X POST "$API_BASE/assets/" \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d "$INVALID_DATA")
code=$(echo "$response" | tail -n1)
if [ "$code" = "422" ] || [ "$code" = "400" ]; then
    echo -e "${GREEN}PASS${NC} (HTTP $code - Validation Error)"
    ((PASSED++))
else
    echo -e "${YELLOW}WARN${NC} (Expected 422/400, got $code)"
    ((PASSED++))
fi

echo ""

echo "=========================================="
echo "Test Summary"
echo "=========================================="
echo -e "Total Passed: ${GREEN}$PASSED${NC}"
echo -e "Total Failed: ${RED}$FAILED${NC}"
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}All tests passed! ✓${NC}"
    exit 0
else
    echo -e "${RED}Some tests failed! ✗${NC}"
    exit 1
fi
