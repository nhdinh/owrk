# Asset Management Service

Backend API service for managing organizational assets, including CRUD operations, assignment tracking, depreciation calculation, and file management.

## Features

✅ **Asset Management** - Complete CRUD operations for assets and categories
✅ **Asset Assignment** - Track asset assignments to users with handover documents
✅ **Depreciation Calculation** - Automatic monthly depreciation for fixed assets
✅ **QR Code Generation** - Generate and manage QR codes for asset tracking
✅ **File Attachments** - Upload and manage invoices, warranties, photos
✅ **Advanced Search & Filtering** - Search by code, name, category, status, etc.

## Tech Stack

- **Framework**: FastAPI 0.104.1 (Python 3.11)
- **Database**: MySQL 8.0 (Write)
- **ORM**: SQLAlchemy 2.0.23
- **Migrations**: Alembic 1.12.1
- **Task Scheduler**: APScheduler (for depreciation calculation)
- **Message Queue**: RabbitMQ (aio-pika)
- **Cache**: Redis 7

## Project Structure

```
services/asset-api/
├── app/
│   ├── api/
│   │   └── v1/
│   │       ├── endpoints/
│   │       │   ├── assets.py           # Asset CRUD endpoints
│   │       │   ├── categories.py       # Category CRUD endpoints
│   │       │   ├── assignments.py      # Assignment endpoints
│   │       │   └── attachments.py      # File upload endpoints
│   │       └── router.py               # Main API router
│   ├── core/
│   │   ├── config.py                   # Settings and configuration
│   │   ├── database.py                 # MySQL connection
│   │   ├── unit_of_work.py             # UnitOfWork pattern
│   │   ├── dependencies.py             # FastAPI dependencies
│   │   └── security.py                 # JWT validation, QR code generation
│   ├── models/
│   │   ├── base.py                     # SQLAlchemy base
│   │   ├── asset.py                    # Asset model
│   │   ├── category.py                 # Category model
│   │   ├── assignment.py               # Assignment model
│   │   ├── attachment.py               # Attachment model
│   │   └── depreciation.py             # Depreciation record model
│   ├── repositories/
│   │   ├── base_repository.py          # Generic CRUD repository
│   │   ├── asset_repository.py         # Asset-specific operations
│   │   ├── category_repository.py      # Category operations
│   │   ├── assignment_repository.py    # Assignment operations
│   │   ├── attachment_repository.py    # Attachment operations
│   │   └── depreciation_repository.py  # Depreciation operations
│   ├── schemas/
│   │   └── asset_schema.py             # Pydantic schemas
│   ├── services/
│   │   ├── asset_service.py            # Asset business logic
│   │   ├── depreciation_service.py     # Depreciation calculation
│   │   └── file_service.py             # File upload/download
│   └── main.py                         # FastAPI application
├── alembic/
│   ├── versions/
│   │   └── 001_initial_schema.py       # Initial migration
│   └── env.py                          # Alembic environment
├── alembic.ini                         # Alembic configuration
├── Dockerfile                          # Docker image definition
├── requirements.txt                    # Python dependencies
└── README.md                           # This file
```

## Database Schema

### Tables (asset_db schema)

1. **asset_categories** - Asset categories with hierarchical structure
2. **assets** - Main asset table with financial and depreciation info
3. **asset_assignments** - Assignment history tracking
4. **asset_attachments** - File attachments (invoices, warranties, photos)
5. **asset_depreciation_records** - Monthly depreciation tracking

## API Endpoints

### Assets

```
GET    /api/v1/assets                  # List assets (with pagination & filters)
GET    /api/v1/assets/{id}             # Get asset detail
POST   /api/v1/assets                  # Create asset
PUT    /api/v1/assets/{id}             # Update asset
DELETE /api/v1/assets/{id}             # Delete asset (soft delete)
POST   /api/v1/assets/{id}/assign      # Assign asset to user
POST   /api/v1/assets/{id}/return      # Return asset
GET    /api/v1/assets/{id}/history     # Get assignment history
GET    /api/v1/assets/{id}/depreciation # Get depreciation records
```

### Categories

```
GET    /api/v1/categories              # List categories
GET    /api/v1/categories/{id}         # Get category
POST   /api/v1/categories              # Create category
PUT    /api/v1/categories/{id}         # Update category
DELETE /api/v1/categories/{id}         # Delete category
```

### Attachments

```
POST   /api/v1/assets/{id}/attachments # Upload file
GET    /api/v1/assets/{id}/attachments # List attachments
DELETE /api/v1/attachments/{id}        # Delete attachment
```

## Quick Start

### Prerequisites

- Python 3.11+
- MySQL 8.0+
- Redis 7+
- RabbitMQ 3+

### 1. Environment Setup

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your configuration
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

### 4. Start Service

```bash
# Development mode
uvicorn app.main:app --reload --host 0.0.0.0 --port 8002

# Production mode
uvicorn app.main:app --host 0.0.0.0 --port 8002 --workers 4
```

### 5. Access API Documentation

- Swagger UI: http://localhost:8002/docs
- ReDoc: http://localhost:8002/redoc

## Docker Deployment

### Build Image

```bash
docker build -t asset-api:latest .
```

### Run Container

```bash
docker run -d \
  --name asset-api \
  -p 8002:8000 \
  --env-file .env \
  asset-api:latest
```

### Docker Compose

```bash
# Start service
docker-compose up -d asset-api-service

# View logs
docker-compose logs -f asset-api-service

# Stop service
docker-compose down
```

## Features Implementation

### 1. Asset CRUD

- Create assets with all details (financial, warranty, depreciation)
- Update asset information
- Soft delete (deleted_at timestamp)
- Advanced filtering and search

### 2. Asset Assignment

- Assign asset to user with handover document
- Track assignment history
- Return asset with condition assessment
- Generate assignment reports

### 3. Depreciation Calculation

- Automatic monthly calculation (scheduled job)
- Two methods: Straight-line and Declining balance
- Track depreciation history
- Calculate current book value

### 4. QR Code Generation

- Generate unique QR code for each asset
- QR code contains asset_code for scanning
- Base64 encoded image stored in database

### 5. File Upload

- Support multiple file types (PDF, images, documents)
- File size validation (max 10MB)
- File type validation
- Secure file storage

### 6. Search & Filtering

Query parameters:
- `search`: Search by code, name, manufacturer, model
- `category_id`: Filter by category
- `status`: Filter by status
- `asset_type`: Filter by type (FIXED_ASSET, TOOL)
- `department_id`: Filter by department
- `page`: Page number (default: 1)
- `page_size`: Results per page (default: 20)

## Configuration

### Environment Variables

```bash
# Database
DATABASE_USER=admin
DATABASE_PASSWORD_FILE=/run/secrets/mysql_passwd
DATABASE_HOST=mysql
DATABASE_PORT=3306
DATABASE_NAME=asset_management

# JWT (for auth validation)
JWT_SECRET_KEY_FILE=/run/secrets/jwt_secret_key
JWT_ALGORITHM=HS256

# File Upload
UPLOAD_DIR=/app/uploads
MAX_UPLOAD_SIZE=10485760

# Depreciation
DEPRECIATION_DAY_OF_MONTH=1
```

## Testing

### Run Tests

```bash
pytest tests/ -v --cov=app
```

### Test Coverage

- Unit tests: Asset CRUD, depreciation calculation
- Integration tests: Assignment flow, file upload
- E2E tests: Create → Assign → Return workflow

## Scheduled Jobs

### Depreciation Calculation

- **Schedule**: 1st day of each month at 00:00
- **Job**: Calculate depreciation for all active fixed assets
- **Method**: APScheduler CronTrigger

## Monitoring

### Health Check

```
GET /health
```

Returns service status and database connectivity.

### Metrics

- Total assets
- Assets by status
- Assets by category
- Monthly depreciation amount

## Troubleshooting

### Common Issues

**Q: "Database connection failed"**
- Check MySQL is running
- Verify DATABASE_URL in config
- Check network connectivity

**Q: "File upload fails"**
- Check UPLOAD_DIR exists and has write permissions
- Verify file size < MAX_UPLOAD_SIZE
- Check file extension is allowed

**Q: "Depreciation not calculating"**
- Check APScheduler is running
- Verify DEPRECIATION_DAY_OF_MONTH setting
- Check asset has depreciation_method set

## License

Proprietary - Asset Management System

## Support

For issues and questions:
- API Docs: http://localhost:8002/docs
- Project Documentation: [docs/](../../docs/)
