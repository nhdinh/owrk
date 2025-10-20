# Asset Management System - Development Guide

## Sprint 1: Infrastructure Setup ✅

Hệ thống quản lý trang thiết bị văn phòng với kiến trúc Microservices, CQRS Pattern, và Event-Driven Architecture.

## 🏗️ Architecture Overview

```
┌──────────────────────────────────────────────────────────────┐
│                     CLIENT LAYER                             │
│              Browser / Mobile / Tablet                       │
└────────────────────────┬─────────────────────────────────────┘
                         │ HTTPS
                         ↓
┌──────────────────────────────────────────────────────────────┐
│                 NGINX API GATEWAY                            │
│         Load Balancing + Rate Limiting + CORS                │
└────────────────────────┬─────────────────────────────────────┘
                         │
        ┌────────────────┼────────────────┬──────────────┐
        ↓                ↓                ↓              ↓
   ┌─────────┐    ┌──────────┐    ┌───────────┐   ┌──────────┐
   │  Auth   │    │  Asset   │    │Procurement│   │Maintenance│
   │ Service │    │ Service  │    │  Service  │   │  Service │
   └────┬────┘    └────┬─────┘    └─────┬─────┘   └────┬─────┘
        │              │                 │              │
        └──────────────┴─────────────────┴──────────────┘
                         ↓
        ┌────────────────────────────────────────────────┐
        │          SHARED INFRASTRUCTURE                 │
        │  PostgreSQL | MongoDB | Redis | RabbitMQ      │
        └────────────────────────────────────────────────┘
```

## 📋 Tech Stack

### Backend

- **Framework**: FastAPI 0.104.1 (Python 3.11)
- **ORM**: SQLAlchemy 2.0.23
- **Write DB**: PostgreSQL 14
- **Read DB**: MongoDB 7 (CQRS)
- **Message Queue**: RabbitMQ 3.12
- **Cache**: Redis 7
- **Auth**: JWT + MFA (pyotp) + Active Directory (ldap3)

### Frontend

- **Framework**: FastAPI
- **Language**: Python 3.11
- **Templating**: Jinja2

### DevOps

- **Containerization**: Docker & Docker Compose
- **API Gateway**: Nginx
- **CI/CD**: GitHub Actions
- **Monitoring**: Prometheus + Grafana (coming soon)

## 🚀 Quick Start

### Prerequisites

- Docker Desktop installed
- Git
- At least 8GB RAM
- 20GB free disk space

### 1. Clone Repository

```bash
git clone <repository-url>
cd officework
```

### 2. Start Infrastructure

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Check service health
docker-compose ps
```

### 3. Access Services

| Service                   | URL                    | Credentials       |
| ------------------------- | ---------------------- | ----------------- |
| **API Gateway**           | http://localhost:80    | -                 |
| **Auth Service API Docs** | http://localhost/docs  | -                 |
| **PostgreSQL**            | localhost:5432         | admin / secret123 |
| **MongoDB**               | localhost:27017        | admin / secret123 |
| **Redis**                 | localhost:6379         | -                 |
| **RabbitMQ Management**   | http://localhost:15672 | guest / guest     |
| **Frontend**              | http://localhost:3000  | (Coming soon)     |

### 4. Verify Installation

```bash
# Check Auth Service health
curl http://localhost:80/health

# Check Auth Service API status
curl http://localhost:80/api/v1/status

# Test PostgreSQL connection
docker-compose exec postgres psql -U admin -d asset_management -c "SELECT version();"

# Test MongoDB connection
docker-compose exec mongodb mongosh -u admin -p secret123 --eval "db.version()"

# Test Redis connection
docker-compose exec redis redis-cli ping

# Test RabbitMQ
curl http://localhost:15672/api/overview -u guest:guest
```

## 📁 Project Structure

```
officework/
├── docs/                              # Project documentation
│   ├── 01. Project_Overview.md
│   ├── 02. Business_Requirements.md
│   ├── 03. System_Architecture.md
│   ├── 04. Database_Design.md
│   ├── 05. API_Specification.md
│   ├── 06. User_Stories.md
│   └── 07. Implementation_Plan.md
│
├── services/                          # Microservices
│   ├── auth-api/                      # Auth API Service
│   │   ├── app/
│   │   │   ├── api/                   # API endpoints
│   │   │   ├── core/                  # Config, DB, RabbitMQ
│   │   │   ├── models/                # SQLAlchemy models
│   │   │   ├── schemas/               # Pydantic schemas
│   │   │   │   ├── commands/          # CQRS Commands
│   │   │   │   ├── queries/           # CQRS Queries
│   │   │   │   └── events/            # Domain Events
│   │   │   ├── repositories/          # Write repositories
│   │   │   ├── read_repositories/     # Read repositories (MongoDB)
│   │   │   ├── commands/              # Command handlers
│   │   │   ├── queries/               # Query handlers
│   │   │   ├── services/              # Business logic
│   │   │   └── main.py
│   │   ├── Dockerfile
│   │   └── requirements.txt
│   │
│   ├── auth-frontend/                 # Auth Frontend Service
│   ├── asset/                         # Asset Service
│   ├── procurement/                   # Procurement Service
│   ├── maintenance/                   # Maintenance Service
│   ├── report/                        # Report Service
│   └── notification/                  # Notification Service
│
├── nginx/                             # API Gateway configuration
│   └── nginx.conf
│
├── scripts/                           # Utility scripts
│   └── init-postgres.sh
│
├── docker-compose.yml                 # Docker Compose configuration
├── .gitignore
└── README.md
```

## 🔧 Development Workflow

### Running Individual Services

```bash
# Auth API Service
cd services/auth-api
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload

# With Docker
docker-compose up auth-api-service
```

### Database Migrations (Alembic)

```bash
# Initialize Alembic (first time only)
cd services/auth-api
alembic init alembic

# Create migration
alembic revision --autogenerate -m "Create users table"

# Apply migration
alembic upgrade head

# Rollback
alembic downgrade -1
```

### Testing

```bash
# Run tests for Auth API Service
cd services/auth-api
pytest tests/ -v

# With coverage
pytest tests/ --cov=app --cov-report=html

# Run specific test
pytest tests/test_auth.py::test_login -v
```

### Code Quality

```bash
# Format code
black app/

# Lint
flake8 app/

# Type checking
mypy app/
```

## 🌐 API Documentation

### Swagger UI

- Auth Service: http://localhost/docs
- Interactive API testing available

### API Endpoints (Sprint 1)

#### Auth Service

- `GET /health` - Health check
- `GET /api/v1/status` - Service status

_(More endpoints will be added in Sprint 2)_

## 🗄️ Database Schemas

### PostgreSQL Schemas

- `auth_db` - Auth Service data
- `asset_db` - Asset Service data
- `procurement_db` - Procurement Service data
- `maintenance_db` - Maintenance Service data
- `notification_db` - Notification Service data

### MongoDB Collections (Read Models)

- `users` - User read model
- `assets` - Asset read model
- `purchase_requests` - Purchase request read model

## 🔒 Security

### Environment Variables

**⚠️ IMPORTANT**: Change these in production!

- `JWT_SECRET` - Change to a strong random string
- `POSTGRES_PASSWORD` - Change database password
- `MONGODB_PASSWORD` - Change MongoDB password
- `SMTP_PASSWORD` - Add SMTP credentials

### Best Practices

- Never commit `.env` files
- Use strong passwords
- Enable HTTPS in production
- Rotate JWT secrets regularly
- Enable MFA for all users

## 📊 Monitoring

### Health Checks

```bash
# Check all services
docker-compose ps

# Check specific service
curl http://localhost/health

# View service logs
docker-compose logs -f auth-service
```

### Resource Usage

```bash
# Monitor container stats
docker stats

# View PostgreSQL activity
docker-compose exec postgres psql -U admin -d asset_management \
  -c "SELECT * FROM pg_stat_activity;"
```

## 🐛 Troubleshooting

### Common Issues

**1. Port already in use**

```bash
# Find process using port
netstat -ano | findstr :5432  # Windows
lsof -i :5432                  # Linux/Mac

# Stop conflicting service or change port in docker-compose.yml
```

**2. Database connection failed**

```bash
# Check if PostgreSQL is running
docker-compose ps postgres

# View PostgreSQL logs
docker-compose logs postgres

# Restart PostgreSQL
docker-compose restart postgres
```

**3. RabbitMQ connection failed**

```bash
# Check RabbitMQ status
docker-compose logs rabbitmq

# Restart RabbitMQ
docker-compose restart rabbitmq
```

**4. Service won't start**

```bash
# Rebuild service
docker-compose build auth-service

# Remove and recreate
docker-compose down
docker-compose up -d
```

## 📝 Next Steps

### Sprint 1 Deliverables ✅

- [x] Docker Compose setup
- [x] PostgreSQL with multiple schemas
- [x] MongoDB connection
- [x] Redis setup
- [x] RabbitMQ setup
- [x] Nginx API Gateway
- [x] Base FastAPI project structure (Auth Service)
- [x] Development documentation

### Sprint 2 Tasks (Week 3)

- [ ] Implement User authentication endpoints
- [ ] JWT token generation & validation
- [ ] MFA/OTP implementation
- [ ] Active Directory integration
- [ ] Password reset flow
- [ ] Role & Permission system
- [ ] Frontend login page

## 📚 Documentation Links

- [Project Overview](docs/01.%20Project_Overview.md)
- [Business Requirements](docs/02.%20Business_Requirements.md)
- [System Architecture](docs/03.%20System_Architecture.md)
- [Database Design](docs/04.%20Database_Design.md)
- [API Specification](docs/05.%20API_Specification.md)
- [User Stories](docs/06.%20User_Stories.md)
- [Implementation Plan](docs/07.%20Implementation_Plan.md)

## 👥 Team & Support

- **Tech Lead**: Hung Dinh
- **Backend Developers**: Hung Dinh
- **Frontend Developers**: Hung Dinh
- **DevOps**: Hung Dinh
- **QA/Tester**: Hung Dinh

## 📄 License

Internal project for [Company Name]

---

**Last Updated**: 2025-10-17
**Sprint**: Sprint 1 - Infrastructure Setup
**Status**: ✅ Completed
