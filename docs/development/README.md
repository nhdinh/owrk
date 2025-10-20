# 💻 DEVELOPMENT - PHÁT TRIỂN

## Giới thiệu

Thư mục này chứa tất cả tài liệu liên quan đến **phát triển phần mềm, coding standards, testing và implementation**.

---

## 📚 Danh sách Tài liệu

### 1. [DEV_README.md](DEV_README.md) ✅
**Mô tả**: Hướng dẫn setup môi trường development và bắt đầu development

**Nội dung chính**:
- **Prerequisites**: Python 3.11+, Docker, Node.js
- **Setup Instructions**:
  - Clone repository
  - Setup virtual environment
  - Install dependencies
  - Database setup
  - Run development server
- **Development Workflow**:
  - Branch strategy
  - Commit conventions
  - Pull request process
- **Debugging**: Tips & tricks
- **Common Issues**: Troubleshooting

**Đối tượng đọc**: All Developers

---

### 2. [Implementation_Plan.md](Implementation_Plan.md) ✅
**Mô tả**: Kế hoạch triển khai chi tiết 16 tuần (12 sprints)

**Nội dung chính**:

#### Roadmap 5 Phases:
- **Phase 1**: Infrastructure & Auth (Tuần 1-3)
  - Sprint 1-2: Docker, Database, Base projects
  - Sprint 3: Auth Service (MFA, AD)

- **Phase 2**: Core Modules (Tuần 4-8)
  - Sprint 4-5: Asset Management
  - Sprint 6: Procurement - Part 1 (Requests & Approval)
  - Sprint 7: Procurement - Part 2 (Quotation & PO)

- **Phase 3**: Supporting Modules (Tuần 9-11)
  - Sprint 8-9: Maintenance Service
  - Sprint 10: Notification & Report Services

- **Phase 4**: Admin & Optimization (Tuần 12-14)
  - Sprint 11: Admin Panel
  - Sprint 12: Performance Optimization
  - Sprint 13: Security Hardening

- **Phase 5**: Testing & Deployment (Tuần 15-16)
  - Sprint 14: Integration Testing & UAT
  - Sprint 15: Production Deployment

**Deliverables mỗi Sprint**:
- Working software
- Documentation
- Test results
- Sprint retrospective

**Đối tượng đọc**: Scrum Master, Tech Lead, Development Team

---

### 3. [Coding_Standards.md](Coding_Standards.md) 📝 TODO
**Mô tả**: Chuẩn code và best practices

**Nội dung dự kiến**:

#### Python (Backend)
```python
# Code style
- PEP 8 compliance
- Black formatting (line length: 100)
- Type hints required
- Docstrings for all functions

# Example
def get_user_by_id(user_id: int) -> Optional[User]:
    """
    Retrieve user by ID.

    Args:
        user_id: The user's ID

    Returns:
        User object if found, None otherwise
    """
    pass
```

#### TypeScript (Frontend)
```typescript
// Code style
- ESLint + Prettier
- Functional components with hooks
- Props interface required

// Example
interface ButtonProps {
  label: string;
  onClick: () => void;
  disabled?: boolean;
}

export const Button: React.FC<ButtonProps> = ({ label, onClick, disabled = false }) => {
  return <button onClick={onClick} disabled={disabled}>{label}</button>;
};
```

#### Naming Conventions
- Files: `snake_case.py`, `PascalCase.tsx`
- Classes: `PascalCase`
- Functions: `snake_case` (Python), `camelCase` (JS/TS)
- Constants: `UPPER_SNAKE_CASE`
- Database: `snake_case` tables and columns

**Đối tượng đọc**: All Developers

---

### 4. [Testing_Guide.md](Testing_Guide.md) 📝 TODO
**Mô tả**: Hướng dẫn viết và chạy tests

**Nội dung dự kiến**:

#### Unit Testing
```python
# pytest example
def test_create_user():
    user = UserService.create_user(
        email="test@example.com",
        password="Test@123",
        full_name="Test User"
    )
    assert user.email == "test@example.com"
    assert user.is_active is True
```

#### Integration Testing
```python
# Test API endpoints
def test_login_success(client):
    response = client.post("/api/v1/auth/login", json={
        "email": "test@example.com",
        "password": "Test@123"
    })
    assert response.status_code == 200
    assert "mfa_token" in response.json()["data"]
```

#### E2E Testing
```typescript
// Playwright example
test('complete purchase request flow', async ({ page }) => {
  await page.goto('/purchase-requests/new');
  await page.fill('[name="title"]', 'New Laptop');
  await page.click('button[type="submit"]');
  await expect(page.locator('.success-message')).toBeVisible();
});
```

#### Test Coverage
- **Target**: > 80% code coverage
- **Critical Paths**: 100% coverage
- **Commands**:
  ```bash
  pytest --cov=app --cov-report=html
  npm run test:coverage
  ```

**Đối tượng đọc**: Developers, QA Engineers

---

## 🔧 Development Environment

### Local Setup
```bash
# Backend
cd services/auth-service
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8001

# Frontend
cd frontend
npm install
npm run dev

# Database
docker-compose up -d postgres redis rabbitmq
```

### Docker Setup
```bash
# All services
docker-compose up -d

# Specific service
docker-compose up -d auth-service

# Logs
docker-compose logs -f auth-service
```

---

## 🌿 Git Workflow

### Branch Strategy
```
main (production)
├── develop (integration)
│   ├── feature/user-authentication
│   ├── feature/asset-management
│   ├── bugfix/login-issue
│   └── hotfix/security-patch
```

### Branch Naming
- `feature/` - New features
- `bugfix/` - Bug fixes
- `hotfix/` - Production hotfixes
- `refactor/` - Code refactoring
- `docs/` - Documentation updates

### Commit Convention (Conventional Commits)
```
<type>(<scope>): <subject>

Types:
- feat: New feature
- fix: Bug fix
- docs: Documentation
- style: Code style (formatting)
- refactor: Code refactoring
- test: Adding tests
- chore: Maintenance tasks

Examples:
feat(auth): Add MFA setup endpoint
fix(asset): Fix depreciation calculation
docs(api): Update API specification
```

---

## 🔄 Development Workflow

### 1. Start New Task
```bash
# Update develop
git checkout develop
git pull origin develop

# Create feature branch
git checkout -b feature/asset-qrcode

# Create Jira ticket link in branch
```

### 2. Development
```bash
# Write code
# Write tests
# Run tests locally
pytest tests/

# Format code
black .
flake8 .

# Type check
mypy .
```

### 3. Commit & Push
```bash
git add .
git commit -m "feat(asset): Add QR code generation"
git push origin feature/asset-qrcode
```

### 4. Pull Request
- Create PR on GitHub
- Fill in PR template
- Request review from Tech Lead
- Address review comments
- Merge after approval

---

## 🧪 Testing Strategy

### Test Pyramid
```
       /\
      /  \  E2E Tests (10%)
     /____\
    /      \  Integration Tests (30%)
   /________\
  /          \  Unit Tests (60%)
 /__________\
```

### Test Types
1. **Unit Tests**: Test individual functions/methods
2. **Integration Tests**: Test API endpoints, database
3. **E2E Tests**: Test complete user flows
4. **Load Tests**: Performance testing with Locust

### Test Commands
```bash
# Unit tests
pytest tests/unit -v

# Integration tests
pytest tests/integration -v

# E2E tests
pytest tests/e2e -v

# All tests with coverage
pytest --cov=app --cov-report=html

# Load tests
locust -f tests/load/locustfile.py
```

---

## 📊 Code Quality

### Static Analysis
```bash
# Python
black .              # Code formatting
flake8 .             # Linting
mypy .               # Type checking
bandit -r app/       # Security checks

# TypeScript
npm run lint         # ESLint
npm run type-check   # TypeScript check
```

### Code Review Checklist
- [ ] Code follows style guide
- [ ] Tests added/updated
- [ ] Documentation updated
- [ ] No security vulnerabilities
- [ ] Performance considerations
- [ ] Error handling
- [ ] Logging added

---

## 🚀 Deployment

### Staging Deployment
```bash
# Automatic via CI/CD when merged to develop
git push origin develop
```

### Production Deployment
```bash
# Automatic via CI/CD when merged to main
git push origin main
```

---

## 📝 Sprint Process

### Sprint Planning (Day 1)
1. Review product backlog
2. Select user stories for sprint
3. Estimate story points
4. Create sprint backlog
5. Assign tasks to team members

### Daily Standup (Daily, 15 min)
- What I did yesterday
- What I'll do today
- Any blockers

### Sprint Review (Last day)
- Demo completed features
- Stakeholder feedback
- Accept/Reject user stories

### Sprint Retrospective (Last day)
- What went well
- What didn't go well
- Action items for improvement

---

## 🔗 Tài liệu Liên quan

### Upstream
- [System Architecture](../design/01_System_Architecture.md)
- [Database Design](../design/02_Database_Design.md)
- [API Specification](../design/03_API_Specification.md)

### Downstream
- [Deployment Docs](../deployment/README.md)
- [User Guides](../guides/README.md)

---

## 👥 Liên hệ

- **Tech Lead**: tech.lead@assetmanagement.com
- **Scrum Master**: scrum.master@assetmanagement.com
- **Questions**: [Create Issue](https://github.com/your-org/asset-management/issues)

---

[⬅️ Back to Design](../design/README.md) | [⬅️ Back to Index](../INDEX.md) | [➡️ Next: Deployment](../deployment/README.md)
