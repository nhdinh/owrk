# Authentication Service

Microservice for authentication, authorization, and user management in the Asset Management System.

## Features

✅ **JWT Authentication** - Stateless token-based authentication with access and refresh tokens
✅ **Multi-Factor Authentication (MFA)** - TOTP-based 2FA with QR codes and backup codes
✅ **Active Directory Integration** - LDAP authentication for enterprise users
✅ **Role-Based Access Control (RBAC)** - Fine-grained permissions system
✅ **Account Security** - Failed login tracking, automatic lockout, password reset
✅ **User Management** - Complete CRUD operations with soft delete
✅ **Database Migrations** - Alembic for schema versioning

## Architecture

### Tech Stack
- **Framework**: FastAPI 0.104.1
- **Database**: PostgreSQL 14 (Write), MongoDB 7 (Read - CQRS)
- **ORM**: SQLAlchemy 2.0.23
- **Migrations**: Alembic 1.12.1
- **Authentication**: python-jose (JWT), passlib (bcrypt)
- **MFA**: pyotp (TOTP), qrcode (QR generation)
- **AD Integration**: ldap3
- **Message Queue**: RabbitMQ (aio-pika)
- **Cache**: Redis 7

### Design Patterns
- **Repository Pattern** - Data access abstraction
- **Unit of Work Pattern** - Transaction management
- **Service Layer Pattern** - Business logic separation
- **Dependency Injection** - FastAPI dependencies
- **CQRS** - Command Query Responsibility Segregation

## Project Structure

```
services/auth-api/
├── app/
│   ├── api/
│   │   └── v1/
│   │       ├── endpoints/
│   │       │   ├── auth.py          # Authentication endpoints
│   │       │   └── users.py         # User management endpoints
│   │       └── router.py            # Main API router
│   ├── core/
│   │   ├── config.py                # Settings and configuration
│   │   ├── database.py              # PostgreSQL connection
│   │   ├── mongo_db.py              # MongoDB connection (CQRS)
│   │   ├── rabbitmq.py              # RabbitMQ connection
│   │   ├── security.py              # JWT, password, MFA utilities
│   │   ├── active_directory.py      # LDAP integration
│   │   ├── dependencies.py          # FastAPI dependencies
│   │   └── unit_of_work.py          # UnitOfWork implementation
│   ├── models/
│   │   ├── base.py                  # SQLAlchemy base
│   │   ├── user.py                  # User model
│   │   ├── role.py                  # Role & Permission models
│   │   └── refresh_token.py         # Token models
│   ├── repositories/
│   │   ├── base_repository.py       # Generic CRUD repository
│   │   ├── user_repository.py       # User-specific operations
│   │   ├── role_repository.py       # Role & Permission operations
│   │   └── refresh_token_repository.py  # Token operations
│   ├── schemas/
│   │   ├── user_schema.py           # User Pydantic schemas
│   │   └── auth_schema.py           # Auth Pydantic schemas
│   ├── services/
│   │   └── auth_service.py          # Authentication business logic
│   └── main.py                      # FastAPI application
├── alembic/
│   ├── versions/
│   │   └── 001_initial_schema.py    # Initial migration
│   ├── env.py                       # Alembic environment
│   └── script.py.mako               # Migration template
├── alembic.ini                      # Alembic configuration
├── requirements.txt                 # Python dependencies
├── Dockerfile                       # Docker image definition
├── .env.example                     # Environment variables template
├── README.md                        # This file
└── TESTING_GUIDE.md                 # API testing guide
```

## Quick Start

### Prerequisites
- Python 3.11+
- PostgreSQL 14+
- MongoDB 7+ (for CQRS)
- Redis 7+ (for caching)
- RabbitMQ 3+ (for messaging)

### 1. Environment Setup

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your configuration
# Important: Set JWT_SECRET, DATABASE_URL, etc.
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Database Setup

```bash
# Run migrations
alembic upgrade head
```

This creates:
- `auth_db` schema in PostgreSQL
- All tables (users, roles, permissions, tokens, etc.)
- Default roles (admin, manager, staff, viewer)
- Default permissions (23 permissions)
- Default admin user (admin@example.com / admin123)

### 4. Start Service

```bash
# Development mode with auto-reload
uvicorn app.main:app --reload --host 0.0.0.0 --port 8001

# Production mode
uvicorn app.main:app --host 0.0.0.0 --port 8001 --workers 4
```

### 5. Access API Documentation

- Swagger UI: http://localhost:8001/docs
- ReDoc: http://localhost:8001/redoc

## API Endpoints

### Authentication
```
POST   /api/v1/auth/login              - Login (Step 1)
POST   /api/v1/auth/verify-otp         - Verify MFA (Step 2)
POST   /api/v1/auth/refresh            - Refresh access token
POST   /api/v1/auth/logout             - Logout
GET    /api/v1/auth/me                 - Get current user
```

### MFA Management
```
GET    /api/v1/auth/mfa/setup          - Get QR code & backup codes
POST   /api/v1/auth/mfa/enable         - Enable MFA
POST   /api/v1/auth/mfa/disable        - Disable MFA
```

### Password Management
```
POST   /api/v1/auth/forgot-password    - Request password reset
POST   /api/v1/auth/reset-password     - Confirm password reset
POST   /api/v1/users/change-password   - Change password
```

### User Management
```
GET    /api/v1/users                   - List users
GET    /api/v1/users/{id}              - Get user
POST   /api/v1/users                   - Create user
PUT    /api/v1/users/{id}              - Update user
DELETE /api/v1/users/{id}              - Deactivate user
POST   /api/v1/users/{id}/unlock       - Unlock account
```

### Active Directory
```
POST   /api/v1/auth/sync-ad            - Sync AD user
```

See [TESTING_GUIDE.md](TESTING_GUIDE.md) for detailed API examples.

## Authentication Flow

### Standard Login (No MFA)
1. User sends email/password to `/auth/login`
2. Service validates credentials
3. Returns access token + refresh token immediately

### Login with MFA (Two-Step)
1. **Step 1**: User sends email/password to `/auth/login`
   - Service validates credentials
   - Returns temporary token (5min expiry) + `requires_mfa: true`
2. **Step 2**: User sends temp token + OTP to `/auth/verify-otp`
   - Service validates OTP or backup code
   - Returns access token (8h) + refresh token (7d)

### Token Refresh
1. Access token expires after 8 hours
2. Client sends refresh token to `/auth/refresh`
3. Service returns new access token
4. Refresh token valid for 7 days

## Security Features

### Password Security
- Bcrypt hashing with automatic salt
- Minimum password requirements (enforced in client)
- Password reset with secure tokens (1-hour expiry)
- Token revocation on password change

### Account Protection
- Failed login attempt tracking
- Automatic account lockout (5 attempts = 30 min)
- IP address logging
- Session management

### Multi-Factor Authentication
- TOTP-based (RFC 6238)
- 30-second time window
- QR code provisioning
- 10 backup codes per user
- Backup code consumption (one-time use)

### Token Security
- JWT with RS256/HS256 algorithm
- Short-lived access tokens (8 hours)
- Refresh token rotation
- Token revocation support
- Different token types (access, refresh, temp)

## Configuration

### Environment Variables

```bash
# Application
APP_NAME=Auth Service
DEBUG=false
API_PREFIX=/api/v1

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/asset_management

# MongoDB (CQRS)
MONGODB_URL=mongodb://localhost:27017
MONGODB_DB_NAME=auth_read_db

# Redis
REDIS_URL=redis://localhost:6379/0

# RabbitMQ
RABBITMQ_URL=amqp://guest:guest@localhost:5672/

# JWT
JWT_SECRET=your-secret-key-change-this
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=480
REFRESH_TOKEN_EXPIRE_DAYS=7

# MFA
MFA_ISSUER=Asset Management System

# Active Directory (Optional)
AD_ENABLED=false
AD_SERVER=ldap://ad.company.com
AD_BASE_DN=DC=company,DC=com
AD_BIND_USER=cn=admin,dc=company,dc=com
AD_BIND_PASSWORD=password
AD_USER_SEARCH_BASE=ou=users,dc=company,dc=com
```

## Database Schema

### Tables
- `auth_db.users` - User accounts
- `auth_db.roles` - User roles
- `auth_db.permissions` - System permissions
- `auth_db.role_permissions` - Role-permission mapping
- `auth_db.refresh_tokens` - Active refresh tokens
- `auth_db.password_reset_tokens` - Password reset tokens
- `auth_db.mfa_backup_codes` - MFA backup codes

### Default Roles
- **admin** - Full system access (all permissions)
- **manager** - Management access (read, create, update, approve)
- **staff** - Standard access (read, create)
- **viewer** - Read-only access

### Permission Format
`resource:action` (e.g., `user:read`, `asset:create`, `procurement:approve`)

## Testing

### Run Unit Tests
```bash
pytest tests/ -v --cov=app
```

### Manual Testing
See [TESTING_GUIDE.md](TESTING_GUIDE.md) for comprehensive API testing examples.

### Default Test User
- Email: `admin@example.com`
- Password: `admin123`
- Role: `admin`

## Docker Deployment

### Build Image
```bash
docker build -t auth-service:latest .
```

### Run Container
```bash
docker run -d \
  --name auth-service \
  -p 8001:8001 \
  --env-file .env \
  auth-service:latest
```

### Docker Compose
```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f auth-service

# Stop services
docker-compose down
```

## Migrations

### Create New Migration
```bash
# Auto-generate from model changes
alembic revision --autogenerate -m "description"

# Create empty migration
alembic revision -m "description"
```

### Apply Migrations
```bash
# Upgrade to latest
alembic upgrade head

# Upgrade one version
alembic upgrade +1

# Downgrade one version
alembic downgrade -1
```

### View Migration History
```bash
alembic history
alembic current
```

## Monitoring

### Health Check
```
GET /health
```

Returns service status and database connectivity.

### Metrics
- Active users
- Failed login attempts
- Token refresh rate
- MFA adoption rate

## Troubleshooting

### Common Issues

**Q: "Invalid or expired token"**
- Check JWT_SECRET matches in .env
- Verify token hasn't expired
- Ensure correct token type (access vs refresh)

**Q: "Account is locked"**
- Wait 30 minutes for auto-unlock
- Admin can unlock via `/users/{id}/unlock`

**Q: "Invalid OTP code"**
- Check time sync on server/mobile
- Try backup code
- Verify TOTP window setting

**Q: "Active Directory authentication failed"**
- Check AD_ENABLED=true in .env
- Verify AD server connectivity
- Check bind user credentials
- Confirm user exists in AD

## Contributing

### Code Style
- Follow PEP 8
- Use Black for formatting
- Type hints required
- Docstrings for all functions

### Pull Request Process
1. Create feature branch
2. Write tests
3. Update documentation
4. Submit PR with description

## License

Proprietary - Asset Management System

## Support

For issues and questions:
- Documentation: `/docs`
- API Docs: http://localhost:8001/docs
- Testing Guide: [TESTING_GUIDE.md](TESTING_GUIDE.md)
