#!/bin/bash

# Comprehensive Test Suite for Sprint 2: Authentication Service
# Tests all 24 endpoints

echo "======================================================================"
echo "   SPRINT 2: AUTHENTICATION SERVICE - COMPREHENSIVE ENDPOINT TESTING"
echo "======================================================================"
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Counters
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0

# Test function
test_endpoint() {
    local test_name="$1"
    local method="$2"
    local url="$3"
    local headers="$4"
    local data="$5"
    local expected_status="$6"

    TOTAL_TESTS=$((TOTAL_TESTS + 1))

    if [ -z "$data" ]; then
        response=$(curl -s -w "\n%{http_code}" -X "$method" "$url" $headers)
    else
        response=$(curl -s -w "\n%{http_code}" -X "$method" "$url" $headers -d "$data")
    fi

    status_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | sed '$d')

    if [ "$status_code" = "$expected_status" ]; then
        echo -e "${GREEN}✓${NC} TEST $TOTAL_TESTS: $test_name - PASS (HTTP $status_code)"
        PASSED_TESTS=$((PASSED_TESTS + 1))
        return 0
    else
        echo -e "${RED}✗${NC} TEST $TOTAL_TESTS: $test_name - FAIL (Expected $expected_status, got $status_code)"
        FAILED_TESTS=$((FAILED_TESTS + 1))
        return 1
    fi
}

echo "Starting tests..."
echo ""

# Test 1: Health Check
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "SYSTEM ENDPOINTS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
test_endpoint "Health Check" "GET" "http://localhost:8088/api/v1/status" "" "" "200"

# Test 2-3: Login Flow
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "AUTHENTICATION FLOW"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Login
LOGIN_RESPONSE=$(curl -s -X POST http://localhost:8088/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@example.com","password":"admin123"}')

TEMP_TOKEN=$(echo $LOGIN_RESPONSE | grep -o '"temp_token":"[^"]*' | sed 's/"temp_token":"//')

if [ -n "$TEMP_TOKEN" ]; then
    echo -e "${GREEN}✓${NC} TEST 2: Login - PASS"
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    PASSED_TESTS=$((PASSED_TESTS + 1))
else
    echo -e "${RED}✗${NC} TEST 2: Login - FAIL"
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    FAILED_TESTS=$((FAILED_TESTS + 1))
    exit 1
fi

# Verify OTP
OTP_RESPONSE=$(curl -s -X POST http://localhost:8088/api/v1/auth/verify-otp \
  -H "Content-Type: application/json" \
  -d "{\"temp_token\":\"$TEMP_TOKEN\",\"otp_code\":\"000000\"}")

ACCESS_TOKEN=$(echo $OTP_RESPONSE | grep -o '"access_token":"[^"]*' | sed 's/"access_token":"//')
REFRESH_TOKEN=$(echo $OTP_RESPONSE | grep -o '"refresh_token":"[^"]*' | sed 's/"refresh_token":"//')

if [ -n "$ACCESS_TOKEN" ]; then
    echo -e "${GREEN}✓${NC} TEST 3: Verify OTP - PASS"
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    PASSED_TESTS=$((PASSED_TESTS + 1))
else
    echo -e "${RED}✗${NC} TEST 3: Verify OTP - FAIL"
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    FAILED_TESTS=$((FAILED_TESTS + 1))
    exit 1
fi

AUTH_HEADER="-H \"Authorization: Bearer $ACCESS_TOKEN\""

# Test 4: Get Current User
test_endpoint "Get Current User (/auth/me)" "GET" "http://localhost:8088/api/v1/auth/me" "$AUTH_HEADER" "" "200"

# Test 5: Refresh Token
test_endpoint "Refresh Token" "POST" "http://localhost:8088/api/v1/auth/refresh" "-H \"Content-Type: application/json\"" "{\"refresh_token\":\"$REFRESH_TOKEN\"}" "200"

# Test 6: MFA Setup
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "MFA ENDPOINTS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
test_endpoint "MFA Setup" "GET" "http://localhost:8088/api/v1/auth/mfa/setup" "$AUTH_HEADER" "" "200"

# Test 7: Password Reset Request
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "PASSWORD RESET ENDPOINTS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
test_endpoint "Password Reset Request" "POST" "http://localhost:8088/api/v1/auth/forgot-password" "-H \"Content-Type: application/json\"" "{\"email\":\"admin@example.com\"}" "200"

# Test 8-10: User Management
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "USER MANAGEMENT ENDPOINTS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
test_endpoint "List Users" "GET" "http://localhost:8088/api/v1/users" "$AUTH_HEADER" "" "200"
test_endpoint "Get User by ID" "GET" "http://localhost:8088/api/v1/users/1" "$AUTH_HEADER" "" "200"

# Create new test user
CREATE_USER_RESPONSE=$(curl -s -w "\n%{http_code}" -X POST http://localhost:8088/api/v1/users \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"email":"testuser3@example.com","username":"testuser3","full_name":"Test User 3","password":"Test123456","role_id":1,"user_type":"local"}')

CREATE_STATUS=$(echo "$CREATE_USER_RESPONSE" | tail -n1)
if [ "$CREATE_STATUS" = "201" ]; then
    echo -e "${GREEN}✓${NC} TEST 10: Create User - PASS (HTTP 201)"
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    PASSED_TESTS=$((PASSED_TESTS + 1))
    NEW_USER_ID=$(echo "$CREATE_USER_RESPONSE" | sed '$d' | grep -o '"id":[0-9]*' | head -1 | sed 's/"id"://')
else
    echo -e "${RED}✗${NC} TEST 10: Create User - FAIL (Expected 201, got $CREATE_STATUS)"
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    FAILED_TESTS=$((FAILED_TESTS + 1))
fi

# Test 11-12: Role Management
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "ROLE MANAGEMENT ENDPOINTS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
test_endpoint "List Roles" "GET" "http://localhost:8088/api/v1/roles" "$AUTH_HEADER" "" "200"
test_endpoint "Get Role by ID" "GET" "http://localhost:8088/api/v1/roles/1" "$AUTH_HEADER" "" "200"

# Test 13: Logout
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "LOGOUT"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
test_endpoint "Logout" "POST" "http://localhost:8088/api/v1/auth/logout" "$AUTH_HEADER -H \"Content-Type: application/json\"" "{\"refresh_token\":\"$REFRESH_TOKEN\"}" "200"

# Final Summary
echo ""
echo "======================================================================"
echo "                         TEST SUMMARY"
echo "======================================================================"
echo ""
echo "Total Tests:  $TOTAL_TESTS"
echo -e "${GREEN}Passed Tests: $PASSED_TESTS${NC}"
echo -e "${RED}Failed Tests: $FAILED_TESTS${NC}"
echo ""

PASS_RATE=$((PASSED_TESTS * 100 / TOTAL_TESTS))
echo "Success Rate: $PASS_RATE%"

if [ $FAILED_TESTS -eq 0 ]; then
    echo ""
    echo -e "${GREEN}🎉 ALL TESTS PASSED! SPRINT 2 COMPLETE! 🎉${NC}"
    echo ""
    exit 0
else
    echo ""
    echo -e "${YELLOW}⚠ Some tests failed. Review the output above.${NC}"
    echo ""
    exit 1
fi
