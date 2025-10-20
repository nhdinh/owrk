# Quick Reference Card - Auth Service

---

## 🚀 Start Services

```bash
docker-compose up -d
```

**Check Status**:
```bash
docker-compose ps
```

---

## 🔐 Default Login

- **Email**: `admin@example.com`
- **Password**: `admin123`

---

## 📡 Endpoints

- **API Base**: http://localhost:8088/api/v1
- **API Docs**: http://localhost:8088/docs
- **Health**: http://localhost:8088/health

---

## 🧪 Quick Tests

### Login:
```bash
curl -X POST http://localhost:8088/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@example.com","password":"admin123"}'
```

### Get Current User:
```bash
curl -X GET http://localhost:8088/api/v1/auth/me \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Setup MFA:
```bash
curl -X GET http://localhost:8088/api/v1/auth/mfa/setup \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## 🗄️ Database Access

```bash
docker exec -it asset_postgres psql -U admin -d asset_management
```

**Check Users**:
```sql
SELECT * FROM auth_db.users;
```

---

## 📋 Logs

```bash
docker logs auth-service -f
```

---

## 🔄 Restart

```bash
docker-compose restart auth-service
```

---

## 📚 Documentation

1. **[AUTH_SERVICE_FIXED.md](AUTH_SERVICE_FIXED.md)** - All fixes
2. **[COMPREHENSIVE_API_TESTING.md](COMPREHENSIVE_API_TESTING.md)** - API tests
3. **[INTEGRATION_COMPLETE.md](INTEGRATION_COMPLETE.md)** - Integration summary
4. **[services/auth-api/TESTING_GUIDE.md](services/auth-api/TESTING_GUIDE.md)** - Full testing guide

---

## ✅ Status

- **Backend**: 🟢 Operational
- **Database**: 🟢 Connected
- **API**: 🟢 Working
- **Login**: ✅ Tested
- **Docs**: ✅ Complete
