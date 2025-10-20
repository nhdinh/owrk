# 📚 DOCUMENTATION - HỆ THỐNG QUẢN LÝ TRANG THIẾT BỊ VĂN PHÒNG

Chào mừng đến với tài liệu dự án! Đây là điểm khởi đầu để tìm hiểu về hệ thống.

## 🚀 Quick Links

- **📋 [INDEX](INDEX.md)** - Mục lục tổng hợp tất cả tài liệu
- **📖 [Main README](../README.md)** - Project README chính
- **🏠 [Project Home](https://github.com/your-org/asset-management)** - GitHub Repository

---

## 📁 Cấu trúc Thư mục

```
docs/
├── INDEX.md                    # Mục lục tổng hợp
├── README.md                   # File này
│
├── requirements/               # 📋 Yêu cầu
│   ├── README.md
│   ├── 01_Project_Overview.md
│   ├── 02_Business_Requirements.md
│   └── 03_User_Stories.md
│
├── design/                     # 🏗️ Thiết kế
│   ├── README.md
│   ├── 01_System_Architecture.md
│   ├── 02_Database_Design.md
│   └── 03_API_Specification.md
│
├── development/                # 💻 Phát triển
│   ├── README.md
│   ├── DEV_README.md
│   └── Implementation_Plan.md
│
├── deployment/                 # 🚀 Triển khai
│   ├── README.md
│   └── Docker_Setup.md
│
├── guides/                     # 📖 Hướng dẫn
│   └── README.md
│
├── deliveries/                 # 📦 Báo cáo Sprint
│   ├── SPRINT2_SUMMARY.md
│   ├── AUTH_SERVICE_FIXED.md
│   └── DEBUG_SESSION.md
│
└── memory_files/               # 🧠 Ghi chú nội bộ
    ├── codebase_structure.md
    ├── tech_stack.md
    └── ...
```

---

## 🎯 Tôi là ai? Tôi nên đọc gì?

### 👔 Business Analyst / Product Owner
1. Start: [INDEX.md](INDEX.md)
2. Read: [Requirements](requirements/)
3. Focus: Business Requirements, User Stories

### 👨‍💻 Backend Developer
1. Start: [DEV_README](development/DEV_README.md)
2. Read: [Design](design/) + [Development](development/)
3. Focus: System Architecture, Database Design, API Spec

### 🎨 Frontend Developer
1. Start: [DEV_README](development/DEV_README.md)
2. Read: [API Specification](design/03_API_Specification.md)
3. Focus: User Stories, API endpoints

### 🔧 DevOps Engineer
1. Start: [Docker Setup](deployment/Docker_Setup.md)
2. Read: [Deployment](deployment/)
3. Focus: CI/CD, Monitoring

### 🧪 QA / Tester
1. Start: [User Stories](requirements/03_User_Stories.md)
2. Read: [API Specification](design/03_API_Specification.md)
3. Focus: Acceptance Criteria, Test Scenarios

### 👥 End User
1. Start: [User Manual](guides/User_Manual.md) (TODO)
2. Read: [FAQ](guides/FAQ.md) (TODO)

### 🔐 System Admin
1. Start: [Admin Guide](guides/Admin_Guide.md) (TODO)
2. Read: [Deployment](deployment/)

---

## 📊 Trạng thái Tài liệu

### ✅ Hoàn thành (13 documents)
- Requirements: 100% (3/3)
- Design: 100% (3/3)
- Development: 50% (2/4)
- Deployment: 25% (1/4)
- Deliveries: 100% (4/4)

### 📝 Đang làm (0 documents)

### ⏳ Chưa làm (13 documents)
- Development: Coding Standards, Testing Guide
- Deployment: CI/CD, Production Deployment, Monitoring
- Guides: User Manual, Admin Guide, API Docs, Troubleshooting, FAQ

**Overall Progress**: 50% (13/26 documents)

---

## 🔍 Tìm kiếm Tài liệu

### Theo Chủ đề

**Authentication & Security**
- [Business Requirements](requirements/02_Business_Requirements.md) - FR-AUTH section
- [System Architecture](design/01_System_Architecture.md) - Auth Service section
- [API Specification](design/03_API_Specification.md) - Auth endpoints

**Asset Management**
- [User Stories](requirements/03_User_Stories.md) - Asset module
- [Database Design](design/02_Database_Design.md) - asset_db schema
- [API Specification](design/03_API_Specification.md) - Asset endpoints

**Procurement**
- [Business Requirements](requirements/02_Business_Requirements.md) - FR-PROC section
- [Database Design](design/02_Database_Design.md) - procurement_db schema
- [User Stories](requirements/03_User_Stories.md) - Procurement workflows

**Deployment & Operations**
- [Docker Setup](deployment/Docker_Setup.md)
- [Implementation Plan](development/Implementation_Plan.md) - CI/CD section

---

## 📝 Quy tắc Đóng góp Tài liệu

### Khi tạo tài liệu mới
1. Đặt tên theo format: `[Số]_[Tên].md`
2. Thêm header (version, author, date)
3. Cập nhật INDEX.md
4. Cập nhật README.md trong thư mục tương ứng

### Khi cập nhật tài liệu
1. Tăng version number
2. Update "Last Updated" date
3. Ghi changelog (nếu major update)
4. Commit với message rõ ràng

### Review Process
- Technical Writer review
- SME (Subject Matter Expert) review
- Final approval by Tech Lead/Product Owner

---

## 🔗 External Resources

### Documentation Tools
- [Markdown Guide](https://www.markdownguide.org/)
- [Mermaid Diagrams](https://mermaid.js.org/)
- [PlantUML](https://plantuml.com/)

### Best Practices
- [Write the Docs](https://www.writethedocs.org/)
- [Google Developer Documentation Style Guide](https://developers.google.com/style)
- [Microsoft Writing Style Guide](https://docs.microsoft.com/en-us/style-guide/)

---

## 📧 Liên hệ

### Về Tài liệu
- **Technical Writer**: docs@assetmanagement.com
- **Documentation Issues**: [GitHub Issues](https://github.com/your-org/asset-management/issues) (label: `documentation`)

### Về Dự án
- **Project Manager**: pm@assetmanagement.com
- **Tech Lead**: tech.lead@assetmanagement.com

---

## 📜 License

Documentation licensed under [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/)

---

<div align="center">

**📚 Happy Reading! 📚**

Cập nhật lần cuối: 2025-10-20

[🏠 Main README](../README.md) | [📋 INDEX](INDEX.md) | [🐛 Report Issue](https://github.com/your-org/asset-management/issues)

</div>
