# NGINX API GATEWAY - ACCESS GUIDE

**Date**: 2025-10-21
**Status**: ✅ **CONFIGURED** (Port 8000)

---

## 🌐 ACCESS URLs

### Main Gateway
- **Nginx API Gateway**: http://localhost:8000/

### Frontend Services (via Nginx)
| Service | URL | Description |
|---------|-----|-------------|
| **Landing Page** | http://localhost:8000/ | Nginx welcome page |
| **Auth Frontend** | http://localhost:8000/auth/ | Login & authentication |
| **Asset Frontend** | http://localhost:8000/assets/ | Asset management UI |

### API Endpoints (via Nginx)
| Endpoint | URL | Description |
|----------|-----|-------------|
| **Health Check** | http://localhost:8000/health | Gateway health |
| **Auth Login** | http://localhost:8000/api/v1/auth/login | POST - Login |
| **Auth Users** | http://localhost:8000/api/v1/users | User management |
| **Auth Roles** | http://localhost:8000/api/v1/roles | Role management |
| **Assets List** | http://localhost:8000/api/v1/assets | Asset CRUD |
| **Categories** | http://localhost:8000/api/v1/categories | Categories |

### API Documentation (via Nginx)
| Docs | URL | Description |
|------|-----|-------------|
| **Auth API Docs** | http://localhost:8000/docs/auth | Auth service Swagger |
| **Asset API Docs** | http://localhost:8000/docs/assets | Asset service Swagger |

### Direct Service Access (Bypass Nginx)
| Service | URL | Port |
|---------|-----|------|
| **Auth API** | http://localhost:8088/docs | 8088 |
| **Asset API** | http://localhost:8089/docs | 8089 |
| **Auth Frontend** | http://localhost:3000/ | 3000 |
| **Asset Frontend** | http://localhost:3001/ | 3001 |

---

## 🔌 PORT CONFIGURATION

| Service | Internal Port | External Port (Host) |
|---------|---------------|---------------------|
| Nginx Gateway | 8000, 8443 | **8000**, 8443 |
| Auth API | 8000 | 8088 |
| Auth Frontend | 3000 | 3000 |
| Asset API | 8000 | 8089 |
| Asset Frontend | 3001 | 3001 |
| MySQL | 3306 | 3306 |
| MongoDB | 27017 | 27017 |
| Redis | 6379 | 6379 |
| RabbitMQ | 5672, 15672 | 5672, 15672 |

**Note**: Nginx đang chạy trên port **8000** (thay vì 80) để tránh conflict với Apache server có sẵn trên Windows.

---

## 🚀 QUICK START

### 1. Start All Services

```bash
docker compose up -d
```

### 2. Check Services Status

```bash
docker compose ps
```

All services should show "healthy" status.

### 3. Access the Application

**Option A: Via Nginx Gateway (Recommended)**
```
http://localhost:8000/
```

**Option B: Direct Auth Frontend**
```
http://localhost:3000/login
```

**Option C: Direct Asset Frontend**
```
http://localhost:3001/assets/
```

---

## 📝 EXAMPLE API CALLS

### Via Nginx Gateway

#### 1. Login
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@example.com",
    "password": "admin123"
  }'
```

#### 2. Get Assets
```bash
# Get token first
TOKEN="your-token-here"

curl http://localhost:8000/api/v1/assets/ \
  -H "Authorization: Bearer $TOKEN"
```

#### 3. Create Asset
```bash
curl -X POST http://localhost:8000/api/v1/assets/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "asset_code": "LAPTOP-001",
    "name": "Dell XPS 15",
    "category_id": 1,
    "purchase_price": 35000000,
    "purchase_date": "2024-01-15"
  }'
```

---

## 🔧 NGINX ROUTING

### Request Flow

```
Client Request
    ↓
http://localhost:8000/api/v1/auth/login
    ↓
Nginx API Gateway (Port 8000)
    ├── Rate Limiting
    ├── CORS Headers
    └── Security Headers
    ↓
Proxy to: auth-api:8000/api/v1/auth/login
    ↓
Auth API Service
    ↓
Response back through Nginx
    ↓
Client
```

### Route Mapping

| Client Request | Nginx Proxies To | Service |
|---------------|------------------|---------|
| `/health` | Nginx (direct) | Nginx |
| `/` | `/usr/share/nginx/html/index.html` | Nginx |
| `/api/v1/auth` | `http://auth-api:8000/api/v1/auth` | auth-api |
| `/api/v1/users` | `http://auth-api:8000/api/v1/users` | auth-api |
| `/api/v1/roles` | `http://auth-api:8000/api/v1/roles` | auth-api |
| `/api/v1/assets` | `http://asset-api:8000/api/v1/assets` | asset-api |
| `/api/v1/categories` | `http://asset-api:8000/api/v1/categories` | asset-api |
| `/auth/` | `http://auth-fe:3000/` | auth-fe |
| `/assets/` | `http://asset-fe:3001/assets/` | asset-fe |
| `/docs/auth` | `http://auth-api:8000/docs` | auth-api |
| `/docs/assets` | `http://asset-api:8000/docs` | asset-api |

---

## ⚠️ IMPORTANT NOTES

### Frontend Link Issues

**Problem**: Links trong templates (dashboard.html, etc.) hiện đang sử dụng relative paths như `/dashboard`, `/profile` mà không có prefix `/auth/` hoặc `/assets/`.

**Impact**:
- Khi truy cập qua nginx (`http://localhost:8000/auth/dashboard`), các link sẽ bị sai
- Click vào link `/dashboard` sẽ dẫn đến `http://localhost:8000/dashboard` thay vì `http://localhost:8000/auth/dashboard`

**Solution**:
Xem chi tiết trong [NGINX_LINK_FIX_GUIDE.md](NGINX_LINK_FIX_GUIDE.md)

Tóm tắt:
- Links trong cùng service: Thêm prefix (`/auth/dashboard`, `/assets/create`)
- Links cross-service: Dùng URL đầy đủ (`http://localhost:8000/assets/`)
- Best practice: Dùng template variables

### Temporary Workaround

Hiện tại có thể:
1. **Truy cập trực tiếp** vào services mà không qua nginx:
   - Auth: http://localhost:3000/
   - Asset: http://localhost:3001/

2. **Chỉ dùng nginx cho API calls**, frontend access trực tiếp

3. **Sửa templates** theo hướng dẫn trong [NGINX_LINK_FIX_GUIDE.md](NGINX_LINK_FIX_GUIDE.md)

---

## 🧪 TESTING

### Test Nginx Health

```bash
curl http://localhost:8000/health
# Expected: healthy
```

### Test Auth API Through Nginx

```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@example.com","password":"admin123"}'
```

### Test Asset API Through Nginx

```bash
# Login first to get token
TOKEN=$(curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@example.com","password":"admin123"}' | \
  grep -o '"temp_token":"[^"]*' | cut -d'"' -f4)

# List assets
curl http://localhost:8000/api/v1/assets/ \
  -H "Authorization: Bearer $TOKEN"
```

### Test Frontend Through Nginx

```bash
# Test auth frontend
curl -I http://localhost:8000/auth/

# Test asset frontend
curl -I http://localhost:8000/assets/
```

---

## 📊 NGINX FEATURES ACTIVE

- ✅ **Reverse Proxy** - Routing to multiple services
- ✅ **Rate Limiting** - 10 req/s for auth, 100 req/s for others
- ✅ **CORS** - Cross-origin requests enabled
- ✅ **Security Headers** - XSS, clickjacking protection
- ✅ **Gzip Compression** - Bandwidth optimization
- ✅ **Health Checks** - Service monitoring
- ✅ **Error Pages** - Custom 50x error pages
- ⏸️ **SSL/TLS** - Not configured (HTTP only)

---

## 🐛 TROUBLESHOOTING

### Nginx shows unhealthy

```bash
# Check logs
docker compose logs nginx

# Check config
docker exec api-gateway nginx -t

# Restart
docker compose restart nginx
```

### Cannot access via http://localhost:8000

**Issue**: Port may be in use by another service

**Check**:
```bash
# Windows
netstat -ano | findstr :8000

# Kill process if needed
taskkill /PID <pid> /F
```

**Or change port in docker-compose.yml**:
```yaml
nginx:
  ports:
    - "8080:8000"  # Use 8080 instead
```

### 502 Bad Gateway

**Cause**: Backend service is down

**Fix**:
```bash
# Check backend services
docker compose ps auth-api asset-api

# Restart if needed
docker compose restart auth-api asset-api nginx
```

### Links not working in frontend

**Solution**: See [NGINX_LINK_FIX_GUIDE.md](NGINX_LINK_FIX_GUIDE.md)

---

## 📚 RELATED DOCUMENTATION

- [NGINX_API_GATEWAY_SETUP.md](NGINX_API_GATEWAY_SETUP.md) - Detailed setup guide
- [NGINX_LINK_FIX_GUIDE.md](NGINX_LINK_FIX_GUIDE.md) - Fix frontend links
- [SPRINT_3_COMPLETION_REPORT.md](SPRINT_3_COMPLETION_REPORT.md) - Sprint 3 report
- [SPRINT_3_QUICK_REFERENCE.md](SPRINT_3_QUICK_REFERENCE.md) - Quick reference

---

## ✅ QUICK CHECKLIST

**For API Development:**
- [x] Nginx running on port 8000
- [x] All API endpoints accessible via nginx
- [x] Rate limiting active
- [x] CORS configured
- [x] API documentation accessible

**For Frontend Development:**
- [x] Frontend services running
- [ ] Links fixed in templates (see NGINX_LINK_FIX_GUIDE.md)
- [ ] Static files proxied correctly
- [ ] Navigation between services working

**For Production:**
- [ ] SSL/TLS configured
- [ ] Rate limits adjusted
- [ ] CORS restricted to specific origins
- [ ] Error pages customized
- [ ] Monitoring enabled
- [ ] Logs configured

---

**Last Updated**: 2025-10-21
**Nginx Status**: ✅ Running on port 8000
**Next Steps**: Fix frontend template links for seamless navigation