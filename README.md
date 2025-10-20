# HỆ THỐNG QUẢN LÝ TRANG THIẾT BỊ VĂN PHÒNG

## 📋 Mục lục
- [Giới thiệu](#giới-thiệu)
- [Tính năng chính](#tính-năng-chính)
- [Kiến trúc hệ thống](#kiến-trúc-hệ-thống)
- [Công nghệ sử dụng](#công-nghệ-sử-dụng)
- [Tài liệu dự án](#tài-liệu-dự-án)
- [Cài đặt và triển khai](#cài-đặt-và-triển-khai)
- [API Documentation](#api-documentation)
- [Quy trình làm việc](#quy-trình-làm-việc)
- [Roadmap](#roadmap)
- [Team](#team)
- [License](#license)

---

## 🎯 Giới thiệu

Hệ thống Quản lý Trang thiết bị Văn phòng là giải pháp số hóa toàn diện giúp doanh nghiệp quản lý hiệu quả tài sản, thiết bị văn phòng từ khâu đề xuất mua sắm, phê duyệt, mua hàng, cấp phát đến bảo trì và thanh lý.

### 🎯 Mục tiêu
- **Số hóa quy trình**: Tự động hóa quy trình quản lý trang thiết bị từ A-Z
- **Tăng hiệu quả**: Giảm 50% thời gian phê duyệt và xử lý yêu cầu
- **Minh bạch**: Theo dõi trạng thái tài sản real-time, lịch sử đầy đủ
- **Tiết kiệm**: Tối ưu chi phí mua sắm và bảo trì thiết bị
- **Bảo mật**: Xác thực 2 bước (MFA/OTP), tích hợp Active Directory

---

## ✨ Tính năng chính

### 🔐 1. Xác thực & Phân quyền
- **Đăng nhập 2 bước (MFA/OTP)** với Google Authenticator
- **Tích hợp Active Directory** - Đồng bộ người dùng tự động
- **Quản lý vai trò & quyền hạn** - Role-based access control
- Backup codes cho recovery
- Audit logging đầy đủ

### 📦 2. Quản lý Tài sản
- **Quản lý tài sản toàn diện**: Thông tin chi tiết, QR code, file đính kèm
- **Phân loại theo kế toán**: Tài sản cố định vs Công cụ dụng cụ
- **Tính khấu hao tự động**: Theo phương pháp đường thẳng hoặc số dư giảm dần
- **Cấp phát & thu hồi**: Theo dõi người sử dụng, biên bản bàn giao
- **Lịch sử đầy đủ**: Assignment history, maintenance history

### 🛒 3. Quản lý Mua sắm (Procurement)
- **Đề xuất mua sắm**: Tạo yêu cầu với danh sách sản phẩm chi tiết
- **Phê duyệt 3 cấp**:
  - Cấp 1: Trưởng phòng (Department Manager)
  - Cấp 2: Trưởng phòng HCNS (HR Manager)
  - Cấp 3: Ban Giám đốc (Director)
- **Hai loại mua sắm**:
  - **Hợp đồng khung**: Mua từ nhà cung cấp đã có hợp đồng
  - **Mua lẻ**: Thu thập báo giá → So sánh → Chọn nhà cung cấp
- **Quản lý đơn hàng**: Purchase Order, thanh toán, giao hàng
- **Tự động tạo tài sản**: Sau khi nhận hàng

### 🔧 4. Quản lý Bảo trì
- **Yêu cầu bảo trì**: Preventive, Corrective, Emergency
- **Phân công kỹ thuật viên**: Tự động hoặc thủ công
- **Lịch bảo trì định kỳ**: Theo ngày/tuần/tháng/quý/năm
- **Theo dõi chi phí**: Ước tính vs thực tế, linh kiện thay thế
- **Lịch sử bảo trì**: Đầy đủ theo từng tài sản

### 📊 5. Báo cáo & Thống kê
- **Báo cáo tài sản**: Inventory, giá trị, khấu hao
- **Báo cáo mua sắm**: Theo thời gian, phòng ban, nhà cung cấp
- **Báo cáo bảo trì**: Chi phí, tần suất, hiệu quả
- **Xuất báo cáo**: PDF, Excel, CSV
- **Dashboard trực quan**: Biểu đồ, thống kê real-time

### 🔔 6. Thông báo
- **In-app notifications**: Real-time với WebSocket
- **Email notifications**: Phê duyệt, cấp phát, bảo trì
- **Notification center**: Quản lý tất cả thông báo
- **Email queue**: Đảm bảo gửi thành công

---

## 🏗️ Kiến trúc hệ thống

### Kiến trúc Microservices

```
┌─────────────────────────────────────────────────────┐
│                  API Gateway (Nginx)                │
│                    Port: 80/443                     │
└─────────────────────────────────────────────────────┘
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
   ┌────▼────┐      ┌─────▼─────┐      ┌────▼────┐
   │  Auth   │      │   Asset   │      │Procure- │
   │ Service │      │  Service  │      │  ment   │
   │ :8001   │      │   :8002   │      │ :8003   │
   └─────────┘      └───────────┘      └─────────┘
        │                  │                  │
   ┌────▼────┐      ┌─────▼─────┐      ┌────▼────┐
   │Mainten- │      │  Report   │      │ Notif.  │
   │  ance   │      │  Service  │      │ Service │
   │ :8004   │      │   :8005   │      │ :8006   │
   └─────────┘      └───────────┘      └─────────┘
        │                  │                  │
        └──────────────────┼──────────────────┘
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
   ┌────▼────┐      ┌─────▼─────┐      ┌────▼────┐
   │PostgreSQL│      │   Redis   │      │RabbitMQ │
   │  :5432  │      │   :6379   │      │ :5672   │
   └─────────┘      └───────────┘      └─────────┘
```

### 6 Microservices

| Service | Port | Trách nhiệm |
|---------|------|-------------|
| **Auth Service** | 8001 | Đăng nhập, MFA/OTP, Active Directory, User/Role management |
| **Asset Service** | 8002 | Quản lý tài sản, cấp phát, khấu hao, QR code |
| **Procurement Service** | 8003 | Đề xuất mua sắm, phê duyệt 3 cấp, báo giá, đơn hàng |
| **Maintenance Service** | 8004 | Yêu cầu bảo trì, lịch định kỳ, work orders |
| **Report Service** | 8005 | Tạo báo cáo, xuất PDF/Excel, dashboard |
| **Notification Service** | 8006 | Thông báo in-app, email queue |

### Database Schema

**Single PostgreSQL Database với 6 Schemas:**
- `auth_db`: Users, Roles, Permissions, MFA, Audit logs
- `asset_db`: Assets, Categories, Assignments, Depreciation
- `procurement_db`: Requests, Quotations, Purchase Orders, Vendors
- `maintenance_db`: Maintenance Requests, Schedules, History
- `notification_db`: Notifications, Email Queue
- `report_db`: Report Templates, History

**Tổng cộng**: 28+ tables với full indexing và relationships

---

## 🛠️ Công nghệ sử dụng

### Backend
- **Framework**: FastAPI (Python 3.11+)
- **ORM**: SQLAlchemy
- **Database**: PostgreSQL 14+
- **Caching**: Redis 7
- **Message Queue**: RabbitMQ 3.12
- **Authentication**:
  - JWT (python-jose)
  - MFA/OTP (pyotp)
  - Active Directory (ldap3)
  - Password hashing (passlib + bcrypt)

### Frontend
- **Framework**: FastAPI (Python 3.11+)
- **Template Engine**: Jinja2
- **Styling**: CSS/Bootstrap (served via static files)
- **Authentication**: Session-based with JWT tokens

### DevOps
- **Containerization**: Docker + Docker Compose
- **Reverse Proxy**: Nginx
- **CI/CD**: GitHub Actions
- **Monitoring**: Prometheus + Grafana
- **Logging**: ELK Stack (Elasticsearch, Logstash, Kibana)
- **Cloud**: AWS / Azure / GCP (hoặc on-premise)

### Development Tools
- **Version Control**: Git + GitHub
- **API Documentation**: Swagger/OpenAPI
- **Testing**: pytest, pytest-cov, Locust (load testing)
- **Code Quality**: Black, Flake8, mypy
- **Project Management**: Jira / Trello

---

## 📚 Tài liệu dự án

Toàn bộ tài liệu dự án được lưu trong thư mục [`docs/v1/`](docs/v1/):

| Tài liệu | Mô tả | File |
|----------|-------|------|
| **Project Overview** | Tổng quan dự án, mục tiêu, phạm vi | [20251017_Project_Overview.md](docs/v1/20251017_Project_Overview.md) |
| **Business Requirements** | Yêu cầu nghiệp vụ chi tiết (Functional & Non-functional) | [20251017_Business_Requirements.md](docs/v1/20251017_Business_Requirements.md) |
| **System Architecture** | Kiến trúc microservices, tech stack, Docker setup | [20251017_System_Architecture.md](docs/v1/20251017_System_Architecture.md) |
| **API Specification** | Đặc tả API đầy đủ cho 6 services | [20251017_API_Specification.md](docs/v1/20251017_API_Specification.md) |
| **User Stories** | 69 user stories với acceptance criteria | [20251017_User_Stories.md](docs/v1/20251017_User_Stories.md) |
| **Database Design** | Schema design, 28+ tables, indexes, security | [20251017_Database_Design.md](docs/v1/20251017_Database_Design.md) |
| **Implementation Plan** | Roadmap 16 tuần, 12 sprints, budget | [20251017_Implementation_Plan.md](docs/v1/20251017_Implementation_Plan.md) |

---

## 🚀 Cài đặt và triển khai

### Prerequisites
- Docker 20.10+
- Docker Compose 2.0+
- Python 3.11+ (for local development)
- Git

### Quick Start

#### 1. Clone repository
```bash
git clone https://github.com/your-org/asset-management.git
cd asset-management
```

#### 2. Setup environment variables
```bash
cp .env.example .env
# Edit .env với các thông tin cần thiết
```

#### 3. Start với Docker Compose
```bash
# Start all services
docker-compose up -d

# Check logs
docker-compose logs -f

# Stop all services
docker-compose down
```

#### 4. Database migration
```bash
# Run migrations
docker-compose exec auth-service alembic upgrade head
docker-compose exec asset-service alembic upgrade head
# ... repeat for other services
```

#### 5. Create admin user
```bash
docker-compose exec auth-service python scripts/create_admin.py
```

#### 6. Access the application
- **Frontend**: http://localhost:3000
- **API Gateway**: http://localhost:80
- **API Docs**: http://localhost/docs (Swagger UI)

### Development Setup

#### Backend (FastAPI)
```bash
cd services/auth-api
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8001
```

#### Frontend (FastAPI)
```bash
cd services/auth-frontend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 3000
```

---

## 📖 API Documentation

### Base URL
```
https://api.assetmanagement.com/api/v1
```

### Authentication
Tất cả API (trừ login) yêu cầu JWT Bearer token:
```
Authorization: Bearer {access_token}
```

### Key Endpoints

#### Auth Service
- `POST /auth/login` - Login (step 1: email/password)
- `POST /auth/verify-otp` - Verify OTP (step 2)
- `GET /auth/mfa/setup` - Setup MFA
- `POST /auth/mfa/enable` - Enable MFA
- `POST /auth/sync-ad` - Sync Active Directory users

#### Asset Service
- `GET /assets` - List assets
- `POST /assets` - Create asset
- `GET /assets/{id}` - Get asset detail
- `POST /assets/{id}/assign` - Assign to user
- `POST /assets/{id}/return` - Return asset

#### Procurement Service
- `POST /purchase-requests` - Create purchase request
- `POST /purchase-requests/{id}/approve` - Approve (level 1/2/3)
- `POST /quotations` - Submit quotation
- `POST /purchase-orders` - Create purchase order

#### Maintenance Service
- `POST /maintenance-requests` - Create maintenance request
- `POST /maintenance-requests/{id}/assign` - Assign to technician
- `GET /maintenance-schedules` - List schedules

### Swagger Documentation
Chi tiết đầy đủ tại: [API Specification](docs/v1/20251017_API_Specification.md)

---

## 🔄 Quy trình làm việc

### 1. Quy trình Mua sắm (Procurement Flow)

```
┌─────────────────┐
│ Nhân viên tạo   │
│  đề xuất mua    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Trưởng phòng   │◄─── Approved/Rejected
│  phê duyệt L1   │
└────────┬────────┘
         │ Approved
         ▼
┌─────────────────┐
│ Trưởng P.HCNS   │◄─── Approved/Rejected
│  phê duyệt L2   │
└────────┬────────┘
         │ Approved
         ▼
┌─────────────────┐
│  Ban Giám đốc   │◄─── Approved/Rejected
│  phê duyệt L3   │
└────────┬────────┘
         │ Approved
         ▼
    ┌────┴────┐
    │         │
    ▼         ▼
┌─────────┐ ┌──────────────┐
│Hợp đồng │ │  Thu thập    │
│  khung  │ │   báo giá    │
└────┬────┘ └──────┬───────┘
     │             │
     │             ▼
     │      ┌─────────────┐
     │      │  So sánh &  │
     │      │ chọn vendor │
     │      └──────┬──────┘
     │             │
     └──────┬──────┘
            ▼
    ┌──────────────┐
    │Tạo đơn hàng  │
    │(Purchase Order)│
    └──────┬───────┘
           │
           ▼
    ┌──────────────┐
    │ Nhận hàng &  │
    │thanh toán    │
    └──────┬───────┘
           │
           ▼
    ┌──────────────┐
    │Tự động tạo   │
    │  tài sản     │
    └──────────────┘
```

### 2. Quy trình Cấp phát Tài sản

```
Tài sản mới nhập → Quản lý thiết bị cấp phát
                         ↓
                  Chọn người nhận
                         ↓
                  Tạo biên bản bàn giao
                         ↓
                  Người dùng ký nhận
                         ↓
                  Cập nhật trạng thái: IN_USE
```

### 3. Quy trình Bảo trì

```
Phát hiện sự cố → Tạo yêu cầu bảo trì
                        ↓
              Quản lý thiết bị phân công
                        ↓
              Kỹ thuật viên tiếp nhận
                        ↓
                  Thực hiện sửa chữa
                        ↓
              Cập nhật kết quả & chi phí
                        ↓
              Đóng yêu cầu (COMPLETED)
```

---

## 🗓️ Roadmap

### Phase 1: Infrastructure & Auth ✅ (Tuần 1-3)
- [x] Docker setup, Database schemas
- [x] Auth Service với MFA/OTP
- [x] Active Directory integration
- [x] Frontend login flow

### Phase 2: Core Modules 🚧 (Tuần 4-8)
- [ ] Asset Management Service
- [ ] Procurement Service (Requests & Approval)
- [ ] Procurement Service (Quotation & PO)

### Phase 3: Supporting Modules (Tuần 9-11)
- [ ] Maintenance Service
- [ ] Notification & Report Services

### Phase 4: Admin & Optimization (Tuần 12-14)
- [ ] Admin Panel
- [ ] Performance Optimization
- [ ] Security Hardening

### Phase 5: Testing & Deployment (Tuần 15-16)
- [ ] Integration Testing & UAT
- [ ] Production Deployment
- [ ] Go Live 🚀

**Chi tiết**: [Implementation Plan](docs/v1/20251017_Implementation_Plan.md)

---

## 👥 Team

### Core Team
- **Tech Lead**: [Tên] - System Architecture, Code Review
- **Backend Developers**: [Tên 1], [Tên 2], [Tên 3] - Microservices Development
- **Frontend Developers**: [Tên 1], [Tên 2] - FastAPI Frontend Development
- **DevOps Engineer**: [Tên] - Infrastructure, CI/CD
- **QA Engineer**: [Tên] - Testing, Quality Assurance
- **Business Analyst**: [Tên] - Requirements, Documentation

### Contact
- **Project Manager**: [Email]
- **Tech Lead**: [Email]
- **Support**: support@assetmanagement.com

---

## 📊 Project Status

### Current Progress
- **Overall**: 15% Complete
- **Backend**: 20% (Auth Service completed)
- **Frontend**: 10% (Basic setup)
- **Database**: 100% (Schema design completed)
- **Documentation**: 100%

### Metrics
- **Total User Stories**: 69
- **Completed**: 12
- **In Progress**: 8
- **Pending**: 49

### Next Milestone
**Sprint 3 (Week 4-5)**: Asset Management Service
- Target: Asset CRUD, Assignment, Depreciation
- ETA: 2025-11-14

---

## 🔒 Security

### Authentication & Authorization
- Multi-Factor Authentication (MFA) với TOTP
- JWT với RS256 algorithm
- Active Directory integration
- Role-Based Access Control (RBAC)

### Data Protection
- Passwords: Bcrypt (cost factor 12)
- MFA Secrets: AES-256 encryption
- HTTPS/TLS in production
- SQL Injection prevention
- XSS & CSRF protection

### Compliance
- OWASP Top 10 compliance
- Regular security audits
- Penetration testing
- Audit logging for all actions

---

## 🧪 Testing

### Test Coverage
- **Unit Tests**: Target > 80%
- **Integration Tests**: Key workflows
- **E2E Tests**: Critical user journeys
- **Load Tests**: 1000+ concurrent users

### Running Tests
```bash
# Unit tests
pytest tests/unit -v --cov

# Integration tests
pytest tests/integration -v

# E2E tests
pytest tests/e2e -v

# Load tests
locust -f tests/load/locustfile.py
```

---

## 📈 Performance Targets

| Metric | Target | Current |
|--------|--------|---------|
| API Response Time (p95) | < 200ms | TBD |
| System Uptime | > 99.5% | TBD |
| Error Rate | < 0.1% | TBD |
| Concurrent Users | 1000+ | TBD |
| Database Query Time | < 50ms | TBD |

---

## 🤝 Contributing

### Workflow
1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

### Code Style
- Python: Black + Flake8 + mypy
- HTML/CSS: Consistent formatting
- Commit messages: Conventional Commits

### Pull Request Guidelines
- Update documentation
- Add/update tests
- Ensure CI passes
- Get approval from Tech Lead

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- FastAPI team for the amazing framework
- PostgreSQL community
- Jinja2 template engine
- All contributors

---

## 📞 Support

### Documentation
- [User Manual](docs/user-manual.md)
- [Admin Guide](docs/admin-guide.md)
- [API Reference](docs/v1/20251017_API_Specification.md)
- [FAQ](docs/faq.md)

### Get Help
- **Issues**: [GitHub Issues](https://github.com/your-org/asset-management/issues)
- **Email**: support@assetmanagement.com
- **Slack**: [Join our Slack](https://slack.assetmanagement.com)

---

<div align="center">

**Hệ thống Quản lý Trang thiết bị Văn phòng**

Made with ❤️ by [Your Organization]

[Website](https://assetmanagement.com) • [Documentation](docs/v1) • [Report Bug](https://github.com/your-org/asset-management/issues) • [Request Feature](https://github.com/your-org/asset-management/issues)

</div>
