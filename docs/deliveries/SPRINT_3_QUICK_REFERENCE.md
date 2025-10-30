# SPRINT 3 - QUICK REFERENCE

## 🚀 Services

| Service        | URL                        | Port | Status       |
| -------------- | -------------------------- | ---- | ------------ |
| Asset API      | http://localhost:8089      | 8089 | ✅ Healthy   |
| Asset Frontend | http://localhost:3001      | 3001 | ✅ Healthy   |
| Asset API Docs | http://localhost:8089/docs | -    | ✅ Available |

## 📌 Key Endpoints

### Asset Management

```bash
# List assets
GET http://localhost:8089/api/v1/assets/
  ?page=1&page_size=20&search=laptop&status=AVAILABLE

# Create asset
POST http://localhost:8089/api/v1/assets/
{
  "asset_code": "LAPTOP-001",
  "name": "Dell XPS 15",
  "category_id": 1,
  "asset_type": "FIXED_ASSET",
  "purchase_price": 35000000,
  "purchase_date": "2024-01-15",
  "depreciation_method": "STRAIGHT_LINE",
  "useful_life_months": 60,
  "residual_value": 5000000
}

# Get asset details
GET http://localhost:8089/api/v1/assets/1

# Update asset
PUT http://localhost:8089/api/v1/assets/1
{
  "description": "Updated description"
}

# Delete asset (soft delete)
DELETE http://localhost:8089/api/v1/assets/1
```

### Assignment Workflow

```bash
# Assign asset
POST http://localhost:8089/api/v1/assets/1/assign
{
  "user_id": 2,
  "department_id": 1,
  "location": "Office 3rd Floor",
  "notes": "Assigned for development work"
}

# Return asset
POST http://localhost:8089/api/v1/assets/1/return
{
  "return_condition": "GOOD",
  "return_notes": "Asset returned in good condition"
}

# Assignment history
GET http://localhost:8089/api/v1/assets/1/history
```

### QR Code & Depreciation

```bash
# Get QR code
GET http://localhost:8089/api/v1/assets/1/qrcode

# Depreciation history
GET http://localhost:8089/api/v1/assets/1/depreciation

# Statistics
GET http://localhost:8089/api/v1/assets/statistics/summary
```

### File Upload

```bash
# Upload attachment
POST http://localhost:8089/api/v1/assets/1/attachments
Content-Type: multipart/form-data
  file: [binary]
  file_type: INVOICE

# List attachments
GET http://localhost:8089/api/v1/assets/1/attachments

# Delete attachment
DELETE http://localhost:8089/api/v1/assets/attachments/1
```

### Categories

```bash
# Create category
POST http://localhost:8089/api/v1/categories/
{
  "code": "IT",
  "name": "IT Equipment",
  "description": "Information Technology Equipment"
}

# List categories
GET http://localhost:8089/api/v1/categories/
```

## 🔐 Authentication

All endpoints require Bearer token:

```bash
Authorization: Bearer <access_token>
```

Get token from auth service:

```bash
# Login
POST http://localhost:8088/api/v1/auth/login
{
  "email": "admin@example.com",
  "password": "admin123"
}

# Verify OTP (if MFA enabled)
POST http://localhost:8088/api/v1/auth/verify-otp
{
  "temp_token": "<temp_token>",
  "otp_code": "000000"
}
```

## 🧪 Testing

### Run Unit Tests

```bash
cd services/asset-api
pytest tests/test_asset_service.py -v
pytest tests/test_depreciation_service.py -v
```

### Run Integration Tests

```bash
chmod +x tests/test_asset_api_integration.sh
bash tests/test_asset_api_integration.sh
```

## 📁 Important Files

### Backend

- `services/asset-api/app/main.py` - Main app + scheduler
- `services/asset-api/app/api/v1/endpoints/assets.py` - Asset endpoints
- `services/asset-api/app/services/asset_service.py` - Business logic
- `services/asset-api/app/services/depreciation_service.py` - Depreciation
- `services/asset-api/app/services/file_service.py` - File uploads
- `services/asset-api/app/models/asset.py` - Asset model

### Frontend

- `services/asset-frontend/app/templates/assets/list.html` - Asset list
- `services/asset-frontend/app/templates/assets/detail.html` - Asset detail (with modals)
- `services/asset-frontend/app/templates/assets/form.html` - Create/Edit form
- `services/asset-frontend/app/static/css/style.css` - Styles
- `services/asset-frontend/app/static/js/main.js` - JavaScript

### Tests

- `services/asset-api/tests/test_asset_service.py` - Unit tests (15 cases)
- `services/asset-api/tests/test_depreciation_service.py` - Unit tests (12 cases)
- `tests/test_asset_api_integration.sh` - Integration tests (20+ cases)

## 🔧 Docker Commands

```bash
# Check service status
docker compose ps

# View logs
docker compose logs asset-api
docker compose logs asset-fe

# Restart services
docker compose restart asset-api asset-fe

# Stop services
docker compose stop asset-api asset-fe

# Start services
docker compose start asset-api asset-fe

# Rebuild and restart
docker compose up -d --build asset-api asset-fe
```

## 📊 Database

### Schema: asset_db

**Tables**:

- `assets` - Main asset table
- `asset_categories` - Asset categories
- `asset_assignments` - Assignment history
- `asset_attachments` - File uploads
- `asset_depreciation_records` - Depreciation tracking

### Connect to MySQL

```bash
docker exec -it mysql mysql -u officework_dbu -p
# Password from .secrets/mysql_user_passwd.txt

USE asset_db;
SHOW TABLES;
SELECT * FROM assets;
```

## 📅 Depreciation Scheduler

**Schedule**: Runs on 1st of each month at 00:00
**Configuration**: `DEPRECIATION_DAY_OF_MONTH=1` in docker-compose.yml

**Manual trigger** (for testing):

```python
from app.services.depreciation_service import DepreciationService

period = DepreciationService.get_current_period()  # e.g., 202410
count = DepreciationService.calculate_all_depreciation(period)
print(f"Processed {count} assets")
```

## 🎨 Asset Statuses

- `NEW` - Newly purchased
- `AVAILABLE` - Ready for assignment
- `IN_USE` - Currently assigned
- `MAINTENANCE` - Under repair
- `BROKEN` - Not functional
- `DISPOSED` - Retired/sold

## 📋 File Types

- `INVOICE` - Purchase invoices
- `WARRANTY` - Warranty documents
- `MANUAL` - User manuals
- `PHOTO` - Asset photos
- `OTHER` - Other documents

**Allowed Extensions**: .pdf, .jpg, .jpeg, .png, .doc, .docx, .xls, .xlsx
**Max Size**: 10MB

## 🚦 Health Checks

```bash
# Asset API
curl http://localhost:8089/health

# Asset Frontend
curl http://localhost:3001/health
```

## 📖 Documentation

- **API Docs**: http://localhost:8089/docs
- **OpenAPI Spec**: http://localhost:8089/openapi.json
- **Sprint 3 Report**: [SPRINT_3_COMPLETION_REPORT.md](SPRINT_3_COMPLETION_REPORT.md)
- **Implementation Plan**: [docs/development/Implementation_Plan.md](docs/development/Implementation_Plan.md)

## ✅ Sprint 3 Checklist

- [x] Asset CRUD APIs
- [x] Category management
- [x] Assignment/Return workflow
- [x] Depreciation calculation (automated)
- [x] QR code generation
- [x] File upload system
- [x] Search & filtering
- [x] Frontend pages (list, detail, form)
- [x] Assignment modal
- [x] Return modal
- [x] Upload modal
- [x] Unit tests (27 cases)
- [x] Integration tests (20+ cases)
- [x] All services healthy
- [x] Documentation complete

**Status**: ✅ 100% COMPLETE

---

**Last Updated**: 2025-10-21
**Sprint**: Sprint 3 - Asset Management Service
**Next**: Sprint 4 - Procurement Service (Part 1)
