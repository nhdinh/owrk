# NGINX GATEWAY - LINK FIX GUIDE

## Vấn đề

Khi sử dụng Nginx làm API Gateway với các route được prefix:
- Auth Frontend: `http://localhost:8000/auth/`
- Asset Frontend: `http://localhost:8000/assets/`

Các links trong template đang sử dụng đường dẫn tương đối (ví dụ: `/dashboard`, `/assets`) sẽ không hoạt động đúng.

## Giải pháp

### Cách 1: Sử dụng URL tuyệt đối (Khuyến nghị cho cross-service links)

Khi link đến service khác, sử dụng URL đầy đủ qua nginx gateway:

```html
<!-- Link đến Asset service từ Auth frontend -->
<a href="http://localhost:8000/assets/">Tài sản</a>

<!-- Link đến Auth API từ Asset frontend -->
<a href="http://localhost:8000/api/v1/auth/login">Đăng nhập</a>
```

### Cách 2: Sử dụng prefix cho cùng service

Khi link trong cùng một frontend service, thêm prefix phù hợp:

```html
<!-- Trong Auth Frontend (prefix /auth/) -->
<a href="/auth/dashboard">Dashboard</a>
<a href="/auth/profile">Hồ sơ</a>
<a href="/auth/logout">Đăng xuất</a>

<!-- Trong Asset Frontend (prefix /assets/) -->
<a href="/assets/">Danh sách tài sản</a>
<a href="/assets/create">Tạo tài sản mới</a>
```

### Cách 3: Sử dụng Jinja2 Template Variable (Tốt nhất)

Tạo biến environment hoặc context variable cho base path:

**1. Update main.py:**
```python
import os

# Set base path from environment or default
BASE_PATH = os.getenv("BASE_PATH", "/auth")

# Add to template context
@app.get("/dashboard")
async def dashboard(request: Request):
    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
            "base_path": BASE_PATH,
            "user": current_user
        }
    )
```

**2. Update templates:**
```html
<!-- Use variable for links -->
<a href="{{ base_path }}/dashboard">Dashboard</a>
<a href="{{ base_path }}/profile">Hồ sơ</a>

<!-- Or for cross-service -->
<a href="{{ asset_base_url }}/assets/">Tài sản</a>
```

**3. Update docker-compose.yml:**
```yaml
auth-fe:
  environment:
    BASE_PATH: /auth
    ASSET_BASE_URL: http://localhost:8000
```

## Các file cần sửa trong Auth Frontend

### dashboard.html

```html
<!-- Navbar links -->
<a href="/auth/dashboard">Dashboard</a>
<a href="/auth/notifications">Thông báo</a>
<a href="/auth/profile">Hồ sơ</a>
<a href="/auth/logout">Đăng xuất</a>

<!-- Sidebar links - trong cùng service -->
<a href="/auth/dashboard">Dashboard</a>
<a href="/auth/users">Người dùng</a>
<a href="/auth/departments">Phòng ban</a>
<a href="/auth/settings">Cài đặt</a>

<!-- Sidebar links - cross service -->
<a href="http://localhost:8000/assets/">Tài sản</a>
<a href="/auth/procurement">Mua sắm</a>
<a href="/auth/maintenance">Bảo trì</a>
<a href="/auth/reports">Báo cáo</a>
```

### login.html

```html
<form action="/auth/login" method="post">
  <!-- form fields -->
</form>

<a href="/auth/forgot-password">Quên mật khẩu?</a>
```

### profile.html

```html
<form action="/auth/profile/update" method="post">
  <!-- form fields -->
</form>

<a href="/auth/dashboard">Quay lại Dashboard</a>
```

## Các file cần sửa trong Asset Frontend

### list.html

```html
<!-- Links within asset service -->
<a href="/assets/">Danh sách</a>
<a href="/assets/create">Tạo mới</a>

<!-- Link back to auth -->
<a href="http://localhost:8000/auth/dashboard">Dashboard</a>
```

### detail.html

```html
<form action="/assets/{{ asset.id }}/assign" method="post">
  <!-- form fields -->
</form>

<a href="/assets/">Quay lại danh sách</a>
```

## Static Files

Static files (CSS, JS, images) cũng cần được cấu hình đúng:

### Trong template:

```html
<!-- Đúng - relative path trong cùng service -->
<link rel="stylesheet" href="/static/css/style.css">
<script src="/static/js/main.js"></script>

<!-- Hoặc dùng url_for nếu có -->
<link rel="stylesheet" href="{{ url_for('static', path='/css/style.css') }}">
```

### Nginx config cần proxy static files:

```nginx
# Auth static files
location /auth/static/ {
    proxy_pass http://auth-fe/static/;
}

# Asset static files
location /assets/static/ {
    proxy_pass http://asset-fe/static/;
}
```

## API Calls từ JavaScript

Khi gọi API từ JavaScript, sử dụng URL đầy đủ:

```javascript
// Gọi Auth API
fetch('http://localhost:8000/api/v1/auth/login', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({email, password})
})

// Gọi Asset API
fetch('http://localhost:8000/api/v1/assets/', {
  headers: {'Authorization': `Bearer ${token}`}
})
```

Hoặc dùng relative URL nếu đã config proxy đúng:

```javascript
// Nếu đang ở auth frontend
fetch('/api/v1/auth/login', {...})

// Nếu đang ở asset frontend
fetch('/api/v1/assets/', {...})
```

## Testing Links

### Test từ browser:

1. Truy cập: `http://localhost:8000/auth/`
2. Đăng nhập
3. Click Dashboard - URL should be: `http://localhost:8000/auth/dashboard`
4. Click Tài sản - URL should navigate to: `http://localhost:8000/assets/`
5. Click Profile - URL should be: `http://localhost:8000/auth/profile`

### Test với curl:

```bash
# Test auth endpoints
curl http://localhost:8000/auth/dashboard

# Test asset endpoints
curl http://localhost:8000/assets/

# Test API endpoints
curl http://localhost:8000/api/v1/auth/health
curl http://localhost:8000/api/v1/assets/
```

## Script tự động sửa links

```bash
#!/bin/bash

# Fix auth-frontend links
find services/auth-frontend/app/templates -name "*.html" -type f -exec \
  sed -i 's|href="/dashboard"|href="/auth/dashboard"|g' {} +

find services/auth-frontend/app/templates -name "*.html" -type f -exec \
  sed -i 's|href="/profile"|href="/auth/profile"|g' {} +

find services/auth-frontend/app/templates -name "*.html" -type f -exec \
  sed -i 's|href="/logout"|href="/auth/logout"|g' {} +

# Fix asset-frontend links
find services/asset-frontend/app/templates -name "*.html" -type f -exec \
  sed -i 's|href="/assets/"|href="/assets/"|g' {} +

echo "Links fixed!"
```

## Checklist

- [ ] Sửa tất cả href trong auth-frontend templates
- [ ] Sửa tất cả href trong asset-frontend templates
- [ ] Sửa form action URLs
- [ ] Sửa API calls trong JavaScript
- [ ] Test navigation giữa các services
- [ ] Test static files (CSS, JS, images)
- [ ] Test form submissions
- [ ] Update environment variables nếu dùng cách 3
- [ ] Test logout và redirect sau login

## URL Pattern Summary

| Context | Pattern | Example |
|---------|---------|---------|
| Auth frontend internal | `/auth/*` | `/auth/dashboard` |
| Asset frontend internal | `/assets/*` | `/assets/create` |
| Cross-service navigation | Full URL | `http://localhost:8000/assets/` |
| Auth API calls | `/api/v1/auth/*` | `/api/v1/auth/login` |
| Asset API calls | `/api/v1/assets/*` | `/api/v1/assets/` |
| Static files | `/static/*` or service-specific | `/auth/static/css/style.css` |

---

**Recommendation**: Sử dụng Cách 3 (Template Variables) cho maintainability tốt nhất. Điều này cho phép thay đổi base path dễ dàng mà không cần sửa tất cả templates.