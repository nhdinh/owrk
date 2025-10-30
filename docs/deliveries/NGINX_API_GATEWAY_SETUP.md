# NGINX API GATEWAY - SETUP GUIDE

**Date**: 2025-10-21
**Status**: ✅ **CONFIGURED AND ACTIVE**

---

## 📋 OVERVIEW

Nginx đã được cấu hình làm API Gateway cho hệ thống Asset Management, hoạt động như reverse proxy cho tất cả các microservices.

### Key Features

- ✅ **Reverse Proxy** cho Auth API và Asset API
- ✅ **Rate Limiting** bảo vệ khỏi DDoS
- ✅ **CORS Headers** cho cross-origin requests
- ✅ **Security Headers** (X-Frame-Options, CSP, etc.)
- ✅ **Health Check** endpoint
- ✅ **Compression** với Gzip
- ✅ **Load Balancing** ready (upstream configuration)

---

## 🏗️ ARCHITECTURE

```
┌─────────────┐
│   Client    │
└──────┬──────┘
       │
       ▼
┌─────────────────────────────┐
│    Nginx API Gateway        │
│    (Port 80/443)            │
│                             │
│  ┌─────────────────────┐   │
│  │  Rate Limiting      │   │
│  │  CORS               │   │
│  │  Security Headers   │   │
│  │  Gzip Compression   │   │
│  └─────────────────────┘   │
└───────┬──────────┬──────────┘
        │          │
        ▼          ▼
  ┌──────────┐  ┌──────────┐
  │ auth-api │  │asset-api │
  │ :8000    │  │ :8000    │
  └──────────┘  └──────────┘
```

---

## 🔌 ENDPOINTS

### API Gateway Routes

| Route | Backend | Description |
|-------|---------|-------------|
| `/health` | Nginx | Health check |
| `/` | Nginx HTML | Landing page |
| `/api/v1/auth` | auth-api:8000 | Authentication |
| `/api/v1/users` | auth-api:8000 | User management |
| `/api/v1/roles` | auth-api:8000 | Role management |
| `/api/v1/assets` | asset-api:8000 | Asset management |
| `/api/v1/categories` | asset-api:8000 | Categories |
| `/docs/auth` | auth-api:8000 | Auth API docs |
| `/docs/assets` | asset-api:8000 | Asset API docs |
| `/auth/` | auth-fe:3000 | Auth frontend |
| `/assets/` | asset-fe:3001 | Asset frontend |

---

## 🚀 CURRENT STATUS

### Docker Services

```bash
docker compose ps nginx
```

```
NAME          IMAGE          STATUS
api-gateway   nginx:alpine   Up (healthy)   0.0.0.0:80->80/tcp, 0.0.0.0:443->443/tcp
```

### Health Check

**From Docker Network** (working perfectly):
```bash
docker exec auth-api curl http://api-gateway/health
# Output: healthy
```

**From Host** (may conflict with existing Apache on port 80):
```bash
curl http://localhost/health
```

---

## ⚠️ PORT 80 CONFLICT

### Issue

Có Apache server đang chạy trên Windows chiếm port 80:
```
Apache/2.4.52 (Ubuntu) Server at localhost Port 80
```

### Solutions

#### Option 1: Stop Apache (Recommended)

**Windows**:
```powershell
# Find and stop Apache
net stop Apache2.4
# or
sc stop Apache2.4
```

**Linux/WSL**:
```bash
sudo systemctl stop apache2
# or
sudo service apache2 stop
```

#### Option 2: Change Nginx Port

Edit [docker-compose.yml](docker-compose.yml):
```yaml
nginx:
  ports:
    - "8080:80"  # Change 80 to 8080
    - "443:443"
```

Then access via: `http://localhost:8080/`

#### Option 3: Use Docker Network (Current)

Tất cả services trong Docker có thể giao tiếp qua nginx:
```bash
# From any container
curl http://api-gateway/api/v1/auth/login
```

---

## 📝 CONFIGURATION FILES

### Main Config

**File**: [nginx/nginx.conf](nginx/nginx.conf)

**Highlights**:
```nginx
# Rate limiting
limit_req_zone $binary_remote_addr zone=api_limit:10m rate=100r/s;
limit_req_zone $binary_remote_addr zone=auth_limit:10m rate=10r/s;

# Upstream backends
upstream auth-api {
    server auth-api:8000;
}

upstream asset-api {
    server asset-api:8000;
}

# Auth API proxy
location /api/v1/auth {
    limit_req zone=auth_limit burst=20 nodelay;
    proxy_pass http://auth-api/api/v1/auth;
    # Headers...
}

# Asset API proxy
location /api/v1/assets {
    limit_req zone=api_limit burst=50 nodelay;
    proxy_pass http://asset-api/api/v1/assets;
    # Headers...
}
```

### HTML Files

- **Landing Page**: [nginx/html/index.html](nginx/html/index.html)
- **Error Page**: [nginx/html/50x.html](nginx/html/50x.html)

---

## 🧪 TESTING

### Test Health Endpoint

```bash
# From Docker network
docker exec auth-api curl http://api-gateway/health

# Expected output:
healthy
```

### Test Auth API

```bash
# Login endpoint
docker exec auth-api curl -X POST http://api-gateway/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@example.com","password":"admin123"}'

# Expected output:
{"temp_token":"eyJ...","requires_mfa":false,"message":"Login successful"}
```

### Test Asset API

```bash
# Get token first
TOKEN=$(docker exec auth-api curl -s -X POST http://api-gateway/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@example.com","password":"admin123"}' | \
  grep -o '"temp_token":"[^"]*' | cut -d'"' -f4)

# List assets
docker exec auth-api curl -H "Authorization: Bearer $TOKEN" \
  http://api-gateway/api/v1/assets/
```

### Test Rate Limiting

```bash
# Spam auth endpoint (should be limited to 10 req/s)
for i in {1..50}; do
  docker exec auth-api curl -s -o /dev/null -w "%{http_code}\n" \
    http://api-gateway/api/v1/auth/login &
done

# Some requests will return 503 (rate limited)
```

---

## 🔧 MANAGEMENT COMMANDS

### Restart Nginx

```bash
docker compose restart nginx
```

### Reload Configuration

```bash
docker exec api-gateway nginx -s reload
```

### Check Configuration

```bash
docker exec api-gateway nginx -t
```

### View Logs

```bash
# Access log
docker compose logs nginx

# Error log
docker exec api-gateway cat /var/log/nginx/error.log
```

### Monitor in Real-time

```bash
docker compose logs -f nginx
```

---

## 📊 PERFORMANCE & SECURITY

### Rate Limiting Configuration

| Zone | Rate | Burst | Applies To |
|------|------|-------|------------|
| `auth_limit` | 10 req/s | 20 | `/api/v1/auth`, `/api/v1/users`, `/api/v1/roles` |
| `api_limit` | 100 req/s | 50 | `/api/v1/assets`, `/api/v1/categories` |

### Security Headers

```nginx
X-Frame-Options: SAMEORIGIN
X-Content-Type-Options: nosniff
X-XSS-Protection: 1; mode=block
Referrer-Policy: no-referrer-when-downgrade
Access-Control-Allow-Origin: *
```

### Compression

- Gzip enabled for: JSON, JavaScript, CSS, HTML, XML, Fonts
- Compression level: 6

### Timeouts

```nginx
proxy_connect_timeout: 60s
proxy_send_timeout: 60s
proxy_read_timeout: 60s
```

---

## 🔐 SSL/TLS (Future)

### Generate Self-Signed Certificate

```bash
mkdir -p nginx/ssl

openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout nginx/ssl/key.pem \
  -out nginx/ssl/cert.pem \
  -subj "/C=VN/ST=HaNoi/L=HaNoi/O=AssetManagement/CN=localhost"
```

### Enable HTTPS

Uncomment HTTPS server block in [nginx.conf](nginx/nginx.conf):

```nginx
server {
    listen 443 ssl http2;
    server_name asset-management.local;

    ssl_certificate /etc/nginx/ssl/cert.pem;
    ssl_certificate_key /etc/nginx/ssl/key.pem;
    ssl_protocols TLSv1.2 TLSv1.3;

    # Same location blocks as HTTP...
}
```

---

## 📈 MONITORING

### Health Check

Nginx có health check tự động:
```yaml
healthcheck:
  test: ["CMD", "wget", "--quiet", "--tries=1", "--spider", "http://localhost/health"]
  interval: 30s
  timeout: 5s
  retries: 3
```

### Access Logs Format

```
$remote_addr - $remote_user [$time_local] "$request"
$status $body_bytes_sent "$http_referer" "$http_user_agent"
```

### Metrics to Monitor

- Request rate (req/s)
- Response time (ms)
- Error rate (4xx, 5xx)
- Active connections
- Rate limit hits

---

## 🎯 BENEFITS

### ✅ Single Entry Point

- All APIs accessible through one gateway
- Consistent URL structure
- Easy to manage and monitor

### ✅ Security

- Rate limiting prevents DDoS
- Security headers protect from XSS, clickjacking
- CORS policy control
- SSL/TLS termination (when enabled)

### ✅ Performance

- Gzip compression reduces bandwidth
- Connection pooling to backends
- Static file serving
- Caching ready (can add)

### ✅ Flexibility

- Easy to add new services
- Load balancing ready
- A/B testing capable
- Canary deployments possible

---

## 🚦 NEXT STEPS

### 1. Resolve Port 80 Conflict

Choose one of the solutions above to access nginx from host.

### 2. Add More Services

When new services are ready (Procurement, Maintenance, etc.):

```nginx
# Add upstream
upstream procurement-api {
    server procurement-api:8000;
}

# Add location
location /api/v1/procurement {
    proxy_pass http://procurement-api/api/v1/procurement;
    # ...
}
```

### 3. Enable SSL/TLS

For production deployment, enable HTTPS.

### 4. Add Monitoring

- Nginx Amplify
- Prometheus + Grafana
- ELK Stack for logs

---

## 📞 TROUBLESHOOTING

### Nginx Not Starting

```bash
# Check config
docker exec api-gateway nginx -t

# Check logs
docker compose logs nginx

# Check port binding
docker compose ps nginx
```

### 502 Bad Gateway

Backend service may be down:
```bash
# Check backend health
docker compose ps auth-api asset-api

# Restart backend
docker compose restart auth-api asset-api
```

### 504 Gateway Timeout

Increase proxy timeouts in nginx.conf:
```nginx
proxy_connect_timeout 120s;
proxy_send_timeout 120s;
proxy_read_timeout 120s;
```

---

## 📚 DOCUMENTATION

- Nginx Official: https://nginx.org/en/docs/
- Nginx Reverse Proxy: https://docs.nginx.com/nginx/admin-guide/web-server/reverse-proxy/
- Rate Limiting: https://www.nginx.com/blog/rate-limiting-nginx/

---

**Last Updated**: 2025-10-21
**Status**: ✅ **FULLY OPERATIONAL** (in Docker network)
**Next**: Resolve port 80 conflict for host access

---

## ✅ VERIFICATION CHECKLIST

- [x] Nginx container running and healthy
- [x] Configuration syntax valid
- [x] Health endpoint working
- [x] Auth API accessible through nginx
- [x] Asset API accessible through nginx
- [x] Rate limiting configured
- [x] Security headers added
- [x] CORS enabled
- [x] Gzip compression active
- [x] Error pages created
- [x] Documentation complete
- [ ] Port 80 accessible from host (blocked by Apache)
- [ ] SSL/TLS configured (future)

**Overall Status**: 95% Complete - Nginx API Gateway is fully functional within Docker network!
