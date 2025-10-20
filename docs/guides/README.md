# 📖 GUIDES - HƯỚNG DẪN SỬ DỤNG

## Giới thiệu

Thư mục này chứa tất cả tài liệu **hướng dẫn sử dụng** cho người dùng cuối, quản trị viên và nhà phát triển bên ngoài.

---

## 📚 Danh sách Tài liệu

### 1. [User_Manual.md](User_Manual.md) 📝 TODO
**Mô tả**: Hướng dẫn sử dụng cho người dùng cuối

**Nội dung dự kiến**:

#### Chương 1: Bắt đầu sử dụng
- Đăng nhập lần đầu
- Thiết lập MFA (Google Authenticator)
- Thay đổi mật khẩu
- Cá nhân hóa tài khoản

#### Chương 2: Quản lý Tài sản
- Xem danh sách tài sản
- Tìm kiếm và lọc tài sản
- Xem chi tiết tài sản
- In QR code tài sản
- Xem lịch sử cấp phát

#### Chương 3: Đề xuất Mua sắm
- Tạo đề xuất mua sắm mới
- Thêm sản phẩm vào đề xuất
- Theo dõi trạng thái phê duyệt
- Hủy đề xuất

#### Chương 4: Phê duyệt (dành cho Manager)
- Xem danh sách đề xuất chờ phê duyệt
- Phê duyệt hoặc từ chối đề xuất
- Thêm ghi chú phê duyệt

#### Chương 5: Báo trì
- Tạo yêu cầu bảo trì
- Theo dõi tiến độ bảo trì
- Xem lịch sử bảo trì tài sản

#### Chương 6: Báo cáo
- Xem dashboard
- Tạo báo cáo tài sản
- Xuất báo cáo PDF/Excel
- Lên lịch báo cáo định kỳ

#### Chương 7: Thông báo
- Xem thông báo mới
- Quản lý thông báo
- Cài đặt email notifications

**Screenshots**: Có ảnh minh họa cho mỗi chức năng

**Đối tượng đọc**: End Users (Nhân viên, Manager, Director)

---

### 2. [Admin_Guide.md](Admin_Guide.md) 📝 TODO
**Mô tả**: Hướng dẫn quản trị hệ thống

**Nội dung dự kiến**:

#### Chương 1: Quản lý Người dùng
- Thêm người dùng mới
- Chỉnh sửa thông tin người dùng
- Khóa/Mở khóa tài khoản
- Reset mật khẩu
- Đồng bộ từ Active Directory
  ```bash
  # Sync all users from AD
  POST /api/v1/auth/sync-ad
  {
    "sync_type": "full",
    "ou": "OU=Users,DC=company,DC=com"
  }
  ```

#### Chương 2: Quản lý Vai trò & Quyền
- Tạo vai trò mới
- Phân quyền cho vai trò
- Gán vai trò cho người dùng
- Permission Matrix

**Permission Matrix Example**:
| Role | Asset View | Asset Create | Request Create | Approve L1 | Approve L2 | Approve L3 |
|------|-----------|--------------|----------------|-----------|-----------|-----------|
| Staff | ✅ | ❌ | ✅ | ❌ | ❌ | ❌ |
| Dept Manager | ✅ | ❌ | ✅ | ✅ | ❌ | ❌ |
| HR Manager | ✅ | ❌ | ✅ | ✅ | ✅ | ❌ |
| Director | ✅ | ❌ | ✅ | ✅ | ✅ | ✅ |
| Asset Manager | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ |
| Admin | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |

#### Chương 3: Quản lý Phòng ban
- Tạo phòng ban mới
- Cấu trúc phòng ban dạng cây
- Gán Trưởng phòng

#### Chương 4: Quản lý Danh mục Tài sản
- Tạo danh mục tài sản
- Phân loại: Tài sản cố định / Công cụ dụng cụ
- Cấu hình khấu hao mặc định

#### Chương 5: Quản lý Nhà cung cấp
- Thêm nhà cung cấp
- Đánh giá nhà cung cấp
- Quản lý hợp đồng khung

#### Chương 6: Cấu hình Hệ thống
- Cài đặt email server
- Cấu hình Active Directory
  ```yaml
  AD_SERVER: ldap://dc.company.com
  AD_BASE_DN: DC=company,DC=com
  AD_USER_DN: CN=admin,CN=Users,DC=company,DC=com
  AD_PASSWORD: *****
  ```
- Cấu hình backup tự động
- Cài đặt notification

#### Chương 7: Audit Logs
- Xem nhật ký hệ thống
- Lọc theo người dùng, hành động, thời gian
- Xuất audit logs

#### Chương 8: Bảo trì Hệ thống
- Backup database
  ```bash
  pg_dump -h localhost -U postgres asset_management > backup.sql
  ```
- Restore database
- Clear cache
- Reindex database

**Đối tượng đọc**: System Administrators, IT Support

---

### 3. [API_Documentation.md](API_Documentation.md) 📝 TODO
**Mô tả**: Tài liệu API cho developers bên ngoài hoặc integrations

**Nội dung dự kiến**:

#### Getting Started
```bash
# 1. Get API Key
# Login to admin panel → API Keys → Generate New Key

# 2. Test API
curl -H "Authorization: Bearer YOUR_API_KEY" \
     https://api.assetmanagement.com/api/v1/assets
```

#### Authentication
```bash
# OAuth 2.0 Flow (for 3rd party integrations)
POST /oauth/token
Content-Type: application/json

{
  "grant_type": "client_credentials",
  "client_id": "your_client_id",
  "client_secret": "your_client_secret"
}

# Response
{
  "access_token": "eyJhbGciOiJIUzI1...",
  "token_type": "Bearer",
  "expires_in": 3600
}
```

#### Common Endpoints
```bash
# Get Assets
GET /api/v1/assets?page=1&limit=20

# Get Asset by ID
GET /api/v1/assets/{id}

# Create Asset
POST /api/v1/assets
{
  "asset_code": "LAP-2025-001",
  "name": "Dell Latitude 5520",
  "category_id": 1,
  "purchase_price": 25000000
}

# Webhook Registration
POST /api/v1/webhooks
{
  "url": "https://your-app.com/webhook",
  "events": ["asset.created", "request.approved"]
}
```

#### Rate Limiting
- **Free Tier**: 100 requests/hour
- **Pro Tier**: 1000 requests/hour
- **Enterprise**: Unlimited

#### SDKs
```python
# Python SDK
from asset_management import AssetClient

client = AssetClient(api_key="YOUR_API_KEY")
assets = client.assets.list(limit=10)
```

```javascript
// JavaScript SDK
const AssetManagement = require('asset-management-sdk');

const client = new AssetManagement({ apiKey: 'YOUR_API_KEY' });
const assets = await client.assets.list({ limit: 10 });
```

**Đối tượng đọc**: External Developers, Integration Partners

---

### 4. [Troubleshooting.md](Troubleshooting.md) 📝 TODO
**Mô tả**: Xử lý các sự cố thường gặp

**Nội dung dự kiến**:

#### Vấn đề Đăng nhập

**Issue**: Không thể đăng nhập
```
Symptoms:
- Error: "Invalid credentials"
- Email/password correct but can't login

Solutions:
1. Check if account is locked (5 failed attempts)
   → Wait 15 minutes or contact admin to unlock

2. Check if MFA is enabled
   → Use correct OTP from Authenticator app

3. Check if account is deactivated
   → Contact admin to reactivate

4. Clear browser cache and cookies
   → Try incognito mode
```

**Issue**: Lost MFA device
```
Solutions:
1. Use backup codes
   → Enter one of the 5 backup codes

2. Contact IT Support to disable MFA temporarily
   → Admin can disable MFA in user settings
```

#### Vấn đề Performance

**Issue**: Slow loading
```
Symptoms:
- Pages load slowly (> 5 seconds)
- API responses slow

Solutions:
1. Check internet connection
2. Clear browser cache
3. Contact IT if issue persists (may be server issue)
```

#### Vấn đề API

**Issue**: 401 Unauthorized
```
Cause: Invalid or expired token

Solution:
1. Check token expiration (tokens expire after 8 hours)
2. Refresh token using /auth/refresh endpoint
3. Re-authenticate if refresh token expired
```

**Issue**: 429 Too Many Requests
```
Cause: Rate limit exceeded

Solution:
1. Wait for rate limit window to reset (1 hour)
2. Optimize API calls (batch requests)
3. Upgrade to higher tier plan
```

#### Vấn đề Database

**Issue**: Connection timeout
```
# Check database status
docker-compose ps postgres

# Restart database
docker-compose restart postgres

# Check logs
docker-compose logs postgres
```

**Đối tượng đọc**: End Users, IT Support, Developers

---

### 5. [FAQ.md](FAQ.md) 📝 TODO
**Mô tả**: Câu hỏi thường gặp

**Nội dung dự kiến**:

#### General

**Q: Tôi có thể truy cập hệ thống từ điện thoại không?**
A: Có, hệ thống responsive và hoạt động tốt trên mobile browsers. App mobile native đang trong kế hoạch phát triển.

**Q: Dữ liệu của tôi có được bảo mật không?**
A: Có, tất cả dữ liệu được mã hóa (at rest & in transit), backup hàng ngày, và tuân thủ các tiêu chuẩn bảo mật.

#### Authentication

**Q: Làm sao để thiết lập MFA?**
A: Vào Settings → Security → Enable MFA → Quét QR code bằng Google Authenticator → Nhập OTP để xác nhận.

**Q: Tôi quên mật khẩu, làm sao để reset?**
A: Click "Forgot Password" ở trang login → Nhập email → Check email để nhận link reset password.

#### Assets

**Q: Làm sao để biết ai đang giữ tài sản?**
A: Vào Asset Details → Tab "Assignment History" → Xem người đang giữ hiện tại.

**Q: QR code có tác dụng gì?**
A: QR code giúp scan nhanh để xem thông tin tài sản bằng mobile app.

#### Procurement

**Q: Mất bao lâu để đề xuất được phê duyệt?**
A: Phụ thuộc vào 3 cấp phê duyệt:
- Level 1 (Trưởng phòng): 1-2 ngày
- Level 2 (HCNS): 2-3 ngày
- Level 3 (Ban Giám đốc): 3-5 ngày
Tổng: ~7-10 ngày làm việc

**Q: Tôi có thể hủy đề xuất đã gửi không?**
A: Có thể hủy nếu chưa được phê duyệt Level 1. Sau đó phải liên hệ người phê duyệt.

#### Maintenance

**Q: Khi nào cần tạo yêu cầu bảo trì?**
A: Khi thiết bị:
- Hỏng hóc, không hoạt động
- Cần bảo trì định kỳ
- Cần thay thế linh kiện

#### Support

**Q: Tôi gặp lỗi, liên hệ ai?**
A:
- Lỗi sử dụng: IT Support (support@company.com)
- Lỗi kỹ thuật: Tech Support (tech@company.com)
- Emergency: Hotline 1900-xxxx

**Đối tượng đọc**: All Users

---

## 📊 Document Status

| Document | Status | Priority | Assignee |
|----------|--------|----------|----------|
| User_Manual.md | 📝 TODO | High | Technical Writer |
| Admin_Guide.md | 📝 TODO | High | Technical Writer |
| API_Documentation.md | 📝 TODO | Medium | API Team |
| Troubleshooting.md | 📝 TODO | Medium | Support Team |
| FAQ.md | 📝 TODO | Low | Support Team |

---

## 🎯 Documentation Best Practices

### For User Manuals
- Use simple, non-technical language
- Include screenshots for every step
- Provide examples and use cases
- Use numbering for step-by-step guides
- Include "Tips" and "Warnings" boxes

### For Admin Guides
- Technical but clear
- Include command examples
- Provide troubleshooting sections
- Document edge cases
- Security warnings for dangerous operations

### For API Docs
- Follow OpenAPI specification
- Include request/response examples
- Document all error codes
- Provide SDK code samples
- Keep up-to-date with API changes

---

## 🔄 Documentation Maintenance

### Update Schedule
- **User Manual**: Update after each feature release
- **Admin Guide**: Update monthly
- **API Docs**: Update with every API change
- **Troubleshooting**: Update when new issues discovered
- **FAQ**: Update quarterly based on support tickets

### Review Process
1. Draft by Technical Writer
2. Review by Feature Owner
3. Review by QA (test accuracy)
4. Approve by Product Owner
5. Publish

---

## 📹 Video Tutorials

### Planned Tutorials
- [ ] Getting Started (10 min)
- [ ] Asset Management Basics (15 min)
- [ ] Creating Purchase Requests (8 min)
- [ ] Approval Workflow (5 min)
- [ ] Admin Panel Overview (20 min)

**Platform**: YouTube channel (unlisted for internal use)

---

## 🌍 Localization

### Languages
- **Primary**: Vietnamese (Tiếng Việt)
- **Secondary**: English (planned)

### Translation Process
1. Write original in Vietnamese
2. Translate to English
3. Review by native speakers
4. Maintain both versions

---

## 🔗 Tài liệu Liên quan

### Internal
- [User Stories](../requirements/03_User_Stories.md) - Source for user manual
- [API Specification](../design/03_API_Specification.md) - Source for API docs

### External
- **Support Portal**: https://support.assetmanagement.com
- **Knowledge Base**: https://kb.assetmanagement.com
- **Community Forum**: https://community.assetmanagement.com

---

## 👥 Liên hệ

- **Technical Writer**: docs@assetmanagement.com
- **Support Team**: support@assetmanagement.com
- **Feedback**: feedback@assetmanagement.com

---

[⬅️ Back to Deployment](../deployment/README.md) | [⬅️ Back to Index](../INDEX.md)
