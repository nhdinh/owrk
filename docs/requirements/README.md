# 📋 REQUIREMENTS - YÊU CẦU HỆ THỐNG

## Giới thiệu

Thư mục này chứa tất cả tài liệu liên quan đến **yêu cầu nghiệp vụ và chức năng** của hệ thống Quản lý Trang thiết bị Văn phòng.

---

## 📚 Danh sách Tài liệu

### 1. [Project Overview](01_Project_Overview.md) ✅
**Mô tả**: Tổng quan dự án, mục tiêu, phạm vi, stakeholders

**Nội dung chính**:
- Mục tiêu dự án
- Phạm vi (In-scope & Out-scope)
- Stakeholders
- Success criteria
- Timeline & Budget estimates

**Đối tượng đọc**: Toàn bộ team, Management, Stakeholders

---

### 2. [Business Requirements](02_Business_Requirements.md) ✅
**Mô tả**: Yêu cầu nghiệp vụ chi tiết bao gồm Functional và Non-functional Requirements

**Nội dung chính**:
- **Functional Requirements (FR)**: 30+ yêu cầu chức năng
  - FR-AUTH: Authentication (MFA/OTP, Active Directory)
  - FR-ASSET: Asset Management (CRUD, Assignment, Depreciation)
  - FR-PROC: Procurement (3-level approval, Quotation, PO)
  - FR-MAINT: Maintenance Management
  - FR-REPORT: Reporting & Analytics
  - FR-NOTIF: Notifications

- **Non-functional Requirements (NFR)**:
  - Performance: Response time < 200ms
  - Security: MFA, RBAC, Encryption
  - Scalability: 1000+ concurrent users
  - Availability: 99.5% uptime

**Đối tượng đọc**: Business Analyst, Product Owner, Development Team

---

### 3. [User Stories](03_User_Stories.md) ✅
**Mô tả**: 69 User Stories với Acceptance Criteria và Test Scenarios

**Nội dung chính**:
- **Module Authentication**: 7 user stories (Login, MFA, AD sync)
- **Module Asset Management**: 15 user stories
- **Module Procurement**: 18 user stories
- **Module Maintenance**: 12 user stories
- **Module Reporting**: 8 user stories
- **Module Administration**: 9 user stories

**Format mỗi User Story**:
```
### US-XXX: [Tiêu đề]
**Là** [vai trò]
**Tôi muốn** [hành động]
**Để** [mục đích]

**Acceptance Criteria:**
- [ ] Tiêu chí 1
- [ ] Tiêu chí 2
...

**Priority**: High/Medium/Low
**Story Points**: 1-13
```

**Đối tượng đọc**: Development Team, QA, Product Owner

---

## 🔗 Tài liệu Liên quan

### Upstream (đầu vào)
- Không có (đây là điểm khởi đầu)

### Downstream (đầu ra)
- [System Architecture](../design/01_System_Architecture.md) - Thiết kế từ requirements
- [Database Design](../design/02_Database_Design.md) - Database schema từ requirements
- [API Specification](../design/03_API_Specification.md) - API endpoints từ requirements

---

## 📊 Trạng thái

| Tài liệu | Version | Last Updated | Status |
|----------|---------|--------------|--------|
| Project Overview | 1.0 | 2025-10-17 | ✅ Complete |
| Business Requirements | 1.0 | 2025-10-17 | ✅ Complete |
| User Stories | 1.0 | 2025-10-17 | ✅ Complete |

**Progress**: 3/3 documents (100%)

---

## 🔄 Quy trình Review

### 1. Requirement Gathering
- Business Analyst thu thập requirements từ stakeholders
- Workshop sessions với users
- Document trong Business Requirements

### 2. Requirements Review
- Product Owner review và approve
- Tech Lead đánh giá tính khả thi
- Stakeholders sign-off

### 3. User Stories Creation
- BA/PO tạo user stories từ requirements
- Development team estimate story points
- QA review acceptance criteria

### 4. Refinement
- Sprint Planning: Review và refine user stories
- Update requirements nếu cần
- Maintain traceability

---

## 📝 Ghi chú

### Requirements Change Management
Khi có thay đổi requirements:
1. Tạo Change Request
2. Impact Analysis (time, cost, scope)
3. Approval từ Product Owner & Stakeholders
4. Update tài liệu (version + changelog)
5. Notify toàn bộ team

### Traceability Matrix
Mỗi User Story phải trace về:
- Business Requirement ID
- Test Cases
- Implementation (code commits)

---

## 👥 Liên hệ

- **Business Analyst**: ba@assetmanagement.com
- **Product Owner**: po@assetmanagement.com
- **Questions**: [Create Issue](https://github.com/your-org/asset-management/issues)

---

[⬅️ Back to Index](../INDEX.md) | [➡️ Next: Design](../design/README.md)
