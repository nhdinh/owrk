# Authentication Service - Testing Guide

Quick reference for testing the Auth Service endpoints.

## 🚀 Quick Start

### 1. Start Infrastructure

```bash
# From project root
cd c:\Users\nhdinh\dev\officework
docker-compose up -d postgres mongodb redis rabbitmq
```

### 2. Run Migrations

```bash
cd services\auth
alembic upgrade head
```

### 3. Start Auth Service

```bash
# Development mode
uvicorn app.main:app --reload --host 0.0.0.0 --port 8001

# Or via Docker
docker-compose up -d auth-service
```

### 4. Access API Documentation

- Swagger UI: http://localhost/api/v1/auth/docs
- ReDoc: http://localhost/api/v1/auth/redoc

---

## 🔐 Default Credentials

**Admin User:**
- Email: `admin@example.com`
- Password: `admin123`
- Role: `admin` (all permissions)

---

## 📝 API Testing Examples

### 1. Login (Without MFA)

```bash
# Step 1: Login with email/password
curl -X POST http://localhost/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@example.com",
    "password": "admin123"
  }'
```

**Response:**
```json
{
  "temp_token": "eyJhbGc...",
  "requires_mfa": false,
  "message": "Login successful"
}
```

If MFA is not enabled, you can use the `temp_token` is not needed. For users without MFA, proceed directly with the access token.

### 2. Login (With MFA) - Two Steps

#### Step 1: Email/Password
```bash
curl -X POST http://localhost/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "password123"
  }'
```

**Response:**
```json
{
  "temp_token": "eyJhbGc...",
  "requires_mfa": true,
  "message": "OTP required"
}
```

#### Step 2: Verify OTP
```bash
curl -X POST http://localhost/api/v1/auth/verify-otp \
  -H "Content-Type: application/json" \
  -d '{
    "temp_token": "eyJhbGc...",
    "otp_code": "123456"
  }'
```

**Response:**
```json
{
  "access_token": "eyJhbGc...",
  "refresh_token": "eyJhbGc...",
  "token_type": "bearer",
  "expires_in": 28800,
  "user": {
    "id": 1,
    "email": "user@example.com",
    "full_name": "John Doe",
    "user_type": "local",
    "mfa_enabled": true
  }
}
```

### 3. Get Current User Info

```bash
curl -X GET http://localhost/api/v1/auth/me \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### 4. Refresh Access Token

```bash
curl -X POST http://localhost/api/v1/auth/refresh \
  -H "Content-Type: application/json" \
  -d '{
    "refresh_token": "YOUR_REFRESH_TOKEN"
  }'
```

### 5. Setup MFA

```bash
# Get QR code and backup codes
curl -X GET http://localhost/api/v1/auth/mfa/setup \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**Response:**
```json
{
  "secret": "JBSWY3DPEHPK3PXP",
  "qr_code_url": "data:image/png;base64,iVBORw0KG...",
  "backup_codes": [
    "ABCD-1234",
    "EFGH-5678",
    ...
  ]
}
```

### 6. Enable MFA

```bash
# Scan QR code with authenticator app, then verify OTP
curl -X POST http://localhost/api/v1/auth/mfa/enable \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "otp_code": "123456"
  }'
```

### 7. Disable MFA

```bash
curl -X POST http://localhost/api/v1/auth/mfa/disable \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "password": "password123",
    "otp_code": "123456"
  }'
```

### 8. Password Reset

#### Step 1: Request Reset
```bash
curl -X POST http://localhost/api/v1/auth/forgot-password \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com"
  }'
```

**Response:**
```json
{
  "message": "If email exists, reset instructions have been sent",
  "token": "abc123xyz..." // TODO: Remove in production, send via email
}
```

#### Step 2: Confirm Reset
```bash
curl -X POST http://localhost/api/v1/auth/reset-password \
  -H "Content-Type: application/json" \
  -d '{
    "token": "abc123xyz...",
    "new_password": "newpassword123"
  }'
```

### 9. Logout

```bash
curl -X POST http://localhost/api/v1/auth/logout \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "refresh_token": "YOUR_REFRESH_TOKEN"
  }'
```

---

## 👥 User Management (Requires Permissions)

### 1. List All Users

```bash
curl -X GET "http://localhost/api/v1/users?skip=0&limit=10" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### 2. Create User

```bash
curl -X POST http://localhost/api/v1/users \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "newuser@example.com",
    "username": "newuser",
    "full_name": "New User",
    "password": "password123",
    "user_type": "local",
    "role_id": 3,
    "department": "IT",
    "position": "Developer"
  }'
```

### 3. Update User

```bash
curl -X PUT http://localhost/api/v1/users/2 \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "full_name": "Updated Name",
    "department": "Engineering"
  }'
```

### 4. Deactivate User

```bash
curl -X POST http://localhost/api/v1/users/2/deactivate \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### 5. Unlock User Account

```bash
# Admin only
curl -X POST http://localhost/api/v1/users/2/unlock \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### 6. Change Own Password

```bash
curl -X POST http://localhost/api/v1/users/change-password \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "old_password": "oldpassword123",
    "new_password": "newpassword123"
  }'
```

---

## 🔧 Active Directory Sync (Admin Only)

```bash
curl -X POST http://localhost/api/v1/auth/sync-ad \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john.doe",
    "sync_all": false
  }'
```

---

## 🧪 Testing Scenarios

### Scenario 1: Account Lockout

1. Attempt login with wrong password 5 times
2. Account gets locked for 30 minutes
3. Verify error message: "Account is locked until..."
4. Admin unlocks the account
5. User can login again

### Scenario 2: MFA Flow

1. User logs in (receives temp_token)
2. User enters OTP from authenticator app
3. Receives access_token and refresh_token
4. Access protected endpoints

### Scenario 3: Backup Code Recovery

1. User loses phone with authenticator
2. User logs in (receives temp_token)
3. User enters backup code instead of OTP
4. Backup code is consumed (marked as used)
5. Receives access_token

### Scenario 4: Password Reset

1. User requests password reset
2. Receives reset token (via email in production)
3. User confirms reset with new password
4. All refresh tokens are revoked
5. User must login again with new password

### Scenario 5: Token Refresh

1. Access token expires (after 8 hours)
2. Use refresh token to get new access token
3. Continue accessing protected endpoints
4. Refresh token expires after 7 days

---

## 🛠️ Database Queries

### Check Users
```sql
SELECT id, email, username, user_type, mfa_enabled, is_active, role_id
FROM auth_db.users;
```

### Check Roles & Permissions
```sql
SELECT r.name as role, p.name as permission
FROM auth_db.roles r
JOIN auth_db.role_permissions rp ON r.id = rp.role_id
JOIN auth_db.permissions p ON p.id = rp.permission_id
ORDER BY r.name, p.name;
```

### Check Active Sessions
```sql
SELECT u.email, rt.token, rt.created_at, rt.expires_at, rt.is_revoked
FROM auth_db.refresh_tokens rt
JOIN auth_db.users u ON u.id = rt.user_id
WHERE rt.is_revoked = false
ORDER BY rt.created_at DESC;
```

### Check Failed Login Attempts
```sql
SELECT email, failed_login_attempts, locked_until, last_failed_login_at
FROM auth_db.users
WHERE failed_login_attempts > 0;
```

---

## 📱 MFA Testing Apps

Use any TOTP-compatible authenticator app:
- Google Authenticator (iOS/Android)
- Microsoft Authenticator (iOS/Android)
- Authy (iOS/Android/Desktop)
- 1Password
- Bitwarden

Scan the QR code from `/auth/mfa/setup` endpoint.

---

## ⚠️ Common Issues

### Issue: "Invalid or expired token"
- Check token expiration
- Ensure correct token type (access vs refresh vs temp)
- Verify JWT_SECRET in .env matches

### Issue: "Permission denied"
- Check user's role has required permission
- Verify role_permissions junction table
- Check permission name format (resource:action)

### Issue: "Account is locked"
- Wait 30 minutes or
- Admin unlocks via `/users/{id}/unlock`

### Issue: "Invalid OTP code"
- Verify time sync on server and mobile device
- Check TOTP window (default ±30 seconds)
- Try backup code instead

---

## 🎯 Permission Matrix

| Role | Permissions |
|------|-------------|
| **admin** | ALL permissions |
| **manager** | read, create, update, approve (all resources) |
| **staff** | read, create (excluding user management) |
| **viewer** | read only (all resources) |

---

## 📚 Additional Resources

- API Documentation: http://localhost/api/v1/auth/docs
- Database Schema: [001_initial_schema.py](alembic/versions/001_initial_schema.py)
- Sprint Summary: [SPRINT2_COMPLETE.md](../../docs/deliveries/SPRINT2_COMPLETE.md)
- System Architecture: [03. System_Architecture.md](../../docs/03.%20System_Architecture.md)
