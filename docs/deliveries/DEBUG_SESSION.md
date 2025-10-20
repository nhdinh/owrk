# Debug Session - Auth Service Connection Issues

**Date**: 2025-10-17
**Status**: 🔧 IN PROGRESS

---

## 🐛 Issues Found and Fixed

### 1. ✅ Config File - Secret Reading Logic (FIXED)
**Problem**:
- Line 11: `with open(os.getenv("POSTGRES_PASSWD_FILE", "r"))` - Using `"r"` as fallback instead of file path
- This caused secrets to not be read correctly

**Fix**:
```python
# Before
with open(os.getenv("POSTGRES_PASSWD_FILE", "r")) as f:

# After
postgres_passwd_file = os.getenv("POSTGRES_PASSWD_FILE")
if postgres_passwd_file and os.path.exists(postgres_passwd_file):
    with open(postgres_passwd_file, "r") as f:
        DATABASE_PASSWORD = f.read().strip()
```

### 2. ✅ Connection URLs - Localhost vs Container Hostnames (FIXED)
**Problem**:
- All connection URLs used `localhost` instead of Docker container hostnames
- PostgreSQL: `localhost:5432` → should be `postgres:5432`
- MongoDB: `localhost:27017` → should be `mongodb:27017`
- RabbitMQ: `localhost:5672` → should be `rabbitmq:5672`
- Redis: `localhost:6379` → should be `redis:6379`

**Fix**:
```python
# Before
DATABASE_URL: str = f"postgresql://{DATABASE_USER}:{DATABASE_PASSWORD}@localhost:5432/{DATABASE_NAME}"

# After
DATABASE_HOST: str = os.getenv("DATABASE_HOST", "postgres")
DATABASE_URL: str = f"postgresql://{DATABASE_USER}:{quote_plus(DATABASE_PASSWORD)}@{DATABASE_HOST}:{DATABASE_PORT}/{DATABASE_NAME}"
```

### 3. ✅ MongoDB URL - Password Not URL Encoded (FIXED)
**Problem**:
- MongoDB passwords with special characters need to be URL encoded
- Error: "Username and password must be escaped according to RFC 3986"

**Fix**:
```python
from urllib.parse import quote_plus

MONGODB_URL: str = f"mongodb://admin:{quote_plus(MONGO_PASSWD)}@{MONGODB_HOST}:{MONGODB_PORT}/"
```

### 4. ✅ JWT Secret File Empty (FIXED)
**Problem**:
- `.secrets/jwt_secret_key.txt` was empty

**Fix**:
```bash
echo "your-super-secret-jwt-key-change-in-production-1760698449" > .secrets/jwt_secret_key.txt
```

### 5. ✅ PostgreSQL init.sql Syntax Error (FIXED)
**Problem**:
- Used PL/pgSQL block syntax (`BEGIN ... IF ... END`) in plain SQL
- PostgreSQL doesn't support this outside of functions

**Fix**:
```sql
# Before
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = '${DB_USER}') THEN
        CREATE ROLE ${DB_USER} WITH LOGIN PASSWORD '${DB_PASSWD}';
    END IF;
END

# After
-- User is automatically created by POSTGRES_USER
ALTER USER ${DB_USER} WITH PASSWORD '${DB_PASSWD}';
```

### 6. ✅ PostgreSQL Password Complexity (FIXED)
**Problem**:
- Password `D@VlEN!MFg4U$Xzdj!5A` with special characters caused issues

**Fix**:
```bash
echo -n "secret123" > .secrets/postgres_passwd.txt
```

### 7. ✅ Database Tables Not Created (FIXED)
**Problem**:
- Database tables didn't exist after container startup

**Fix**:
```bash
docker exec auth-service alembic upgrade head
```

**Result**:
- ✅ 7 tables created in `auth_db` schema
- ✅ Admin user seeded with correct password hash
- ✅ Roles and permissions created

---

## ✅ Current Container Status

```bash
NAME             STATUS                    PORTS
asset_mongodb    Up - healthy             0.0.0.0:27017->27017/tcp
asset_postgres   Up - healthy             0.0.0.0:5432->5432/tcp
asset_rabbitmq   Up - healthy             0.0.0.0:5672->5672/tcp, 0.0.0.0:15672->15672/tcp
asset_redis      Up - healthy             0.0.0.0:6379->6379/tcp
auth-service     Up - healthy             0.0.0.0:8088->8000/tcp
asset_nginx      Restarting (missing config)
```

### Connection Status:
- ✅ PostgreSQL: Connected successfully
- ✅ MongoDB: Connected successfully
- ✅ RabbitMQ: Connected successfully
- ✅ Redis: (Not tested yet)

### Database Status:
```sql
auth_db.users                    ✅ Created (1 user)
auth_db.roles                    ✅ Created (1 role)
auth_db.permissions              ✅ Created
auth_db.role_permissions         ✅ Created
auth_db.refresh_tokens           ✅ Created
auth_db.password_reset_tokens    ✅ Created
auth_db.mfa_backup_codes         ✅ Created
```

### Admin User:
- Email: `admin@example.com`
- Password: `admin123`
- Hash: `$2b$12$yk12wFneOEVCas/sZcLqXeXY8/uInVMwnHtjWW2QoL0CLlFdJl0ri`
- Password Verification: ✅ Working (tested with bcrypt)

---

## 🔴 Current Issue: Login API Returns 500 Error

### Problem:
```bash
curl -X POST http://localhost:8088/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@example.com","password":"admin123"}'

Response: {"detail":"Login failed"}
Status: 500 Internal Server Error
```

### Investigation:
1. ✅ Database query succeeds (user found)
2. ✅ Password hash is correct format
3. ✅ Password verification works (tested with bcrypt directly)
4. ✅ Role relationship exists (role_id=1, role found)
5. ❓ Exception occurs somewhere in `AuthService.login_step1()`
6. ❓ Exception is caught and only returns generic "Login failed"

### Logs:
```
2025-10-17 10:58:39 - sqlalchemy.engine.Engine - INFO - SELECT auth_db.users...FROM auth_db.users WHERE auth_db.users.id = %(id_1)s
2025-10-17 10:58:39 - sqlalchemy.engine.Engine - INFO - ROLLBACK
INFO: 172.18.0.1:43752 - "POST /api/v1/auth/login HTTP/1.1" 500 Internal Server Error
```

**Observation**: Query succeeds but transaction is ROLLBACK, indicating an exception occurred.

### Possible Causes:
1. Exception in password verification logic
2. Exception when creating JWT token
3. Exception in Role serialization
4. Missing field in User model vs database
5. Exception in session/transaction management

---

## 🔍 Next Steps

### Immediate Actions:
1. [ ] Add detailed exception logging to `AuthService.login_step1()`
2. [ ] Check if JWT_SECRET is being read correctly
3. [ ] Verify all User model fields match database columns
4. [ ] Test JWT token generation independently
5. [ ] Enable DEBUG logging level

### Code Changes Needed:
```python
# In auth.py, line 43-44, replace:
except Exception as e:
    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Login failed")

# With:
except Exception as e:
    import traceback
    logger.error(f"Login error: {str(e)}")
    logger.error(traceback.format_exc())
    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Login failed: {str(e)}")
```

### Testing Commands:
```bash
# Test database connection
docker exec asset_postgres psql -U admin -d asset_management -c "SELECT 1"

# Test user query
docker exec asset_postgres psql -U admin -d asset_management -c "SELECT * FROM auth_db.users WHERE username='admin'"

# Test password hash
docker exec auth-service python -c "import bcrypt; print(bcrypt.checkpw(b'admin123', b'\$2b\$12\$yk12wFneOEVCas/sZcLqXeXY8/uInVMwnHtjWW2QoL0CLlFdJl0ri'))"

# Check auth-service logs
docker logs auth-service --tail 50

# Restart auth-service
docker-compose restart auth-service
```

---

## 📝 Files Modified

1. `services/auth-api/app/core/config.py`
   - Fixed secret reading logic
   - Changed all URLs from localhost to container hostnames
   - Added URL encoding for passwords
   - Added environment variable support for hosts/ports

2. `postgres/init.sql`
   - Removed invalid PL/pgSQL block syntax
   - Simplified to just ALTER USER

3. `.secrets/postgres_passwd.txt`
   - Changed from complex password to `secret123`

4. `.secrets/jwt_secret_key.txt`
   - Added JWT secret content

5. `postgres/entry.sh`
   - Already correct, no changes needed

---

## ✅ What's Working

- ✅ All containers running and healthy (except nginx - needs config)
- ✅ PostgreSQL connection from auth-service
- ✅ MongoDB connection from auth-service
- ✅ RabbitMQ connection from auth-service
- ✅ Database migrations applied successfully
- ✅ Seed data created (admin user, roles, permissions)
- ✅ Password hash format correct
- ✅ Bcrypt password verification working
- ✅ Database schema properly configured

## 🔴 What's Not Working

- ❌ Login API endpoint returns 500 error
- ❌ Exception details not logged properly
- ⚠️ Nginx container missing configuration (separate issue)

---

## 💡 Recommendations

1. **Enable Debug Logging**: Add `--log-level debug` to uvicorn command
2. **Improve Error Handling**: Log full exception details in endpoints
3. **Add Health Check**: Verify JWT secret is loaded correctly
4. **Test Components**: Add unit tests for AuthService.login_step1()
5. **Environment Variables**: Consider using .env file for local development

---

## 📊 Timeline

- 10:49 - Started debugging
- 10:51 - Fixed config.py secret reading
- 10:54 - Fixed connection URLs
- 10:55 - Fixed PostgreSQL init.sql
- 10:57 - Ran migrations successfully
- 10:58 - Confirmed data in database
- 11:00 - Still investigating login 500 error

**Status**: Making progress, close to resolution
