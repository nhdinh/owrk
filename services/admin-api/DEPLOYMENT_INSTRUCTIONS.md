# Admin API Deployment Instructions

## Overview

This document provides step-by-step instructions for deploying the Admin API with the Trash/Recycle Bin feature.

## Prerequisites

- Docker and Docker Compose installed
- All service containers stopped except MySQL (or be prepared to recreate MySQL)
- Backup of MySQL data if in production

## Deployment Steps

### Step 1: Update MySQL Database

The `admin_db` database needs to be created with proper permissions. This was added to `scripts/.init.sql` but requires recreating the MySQL container.

#### Option A: Fresh Development Environment

If this is a fresh development environment or you don't have critical data:

```bash
# Stop all services
docker compose down

# Remove MySQL data volume
docker volume rm officework__mysql_db

# Start MySQL to initialize with updated init.sql
docker compose up -d mysql

# Wait for MySQL to be healthy (30-60 seconds)
docker compose ps mysql

# Verify admin_db was created
docker exec mysql mysql -uroot -p$(cat .secrets/mysql_root_passwd.txt) -e "SHOW DATABASES;"
```

#### Option B: Existing Environment with Data

If you have existing data in MySQL:

```bash
# 1. Backup existing databases
docker exec mysql mysqldump -uroot -p$(cat .secrets/mysql_root_passwd.txt) --all-databases > backup.sql

# 2. Stop MySQL
docker compose stop mysql

# 3. Remove and recreate
docker compose rm -f mysql
docker volume rm officework__mysql_db

# 4. Start MySQL
docker compose up -d mysql

# Wait for MySQL to be healthy
sleep 60

# 5. Restore data
docker exec -i mysql mysql -uroot -p$(cat .secrets/mysql_root_passwd.txt) < backup.sql

# 6. Verify
docker exec mysql mysql -uroot -p$(cat .secrets/mysql_root_passwd.txt) -e "SHOW DATABASES;"
```

### Step 2: Build and Start Admin API

```bash
# Build admin-api with new dependencies
docker compose build admin-api

# Start admin-api
docker compose up -d admin-api

# Check logs
docker compose logs -f admin-api
```

### Step 3: Run Database Migrations

```bash
# Enter admin-api container
docker compose exec admin-api bash

# Check current migration status
alembic current

# Run migrations
alembic upgrade head

# Verify migration
alembic current
# Should show: 002 (head)

# Exit container
exit
```

### Step 4: Verify Tables Created

```bash
# Check tables in admin_db
docker exec mysql mysql -uroot -p$(cat .secrets/mysql_root_passwd.txt) admin_db -e "SHOW TABLES;"

# Expected output:
# +----------------------+
# | Tables_in_admin_db   |
# +----------------------+
# | alembic_version      |
# | audit_logs           |
# | module_settings      |
# | system_logs          |
# | system_modules       |
# | trash_config         |
# | trash_items          |
# +----------------------+
```

### Step 5: Verify Default Data

```bash
# Check default system modules
docker exec mysql mysql -uroot -p$(cat .secrets/mysql_root_passwd.txt) admin_db -e \
  "SELECT module_name, display_name, status FROM system_modules;"

# Check default trash configs
docker exec mysql mysql -uroot -p$(cat .secrets/mysql_root_passwd.txt) admin_db -e \
  "SELECT module_name, resource_type, auto_delete_days FROM trash_config;"
```

### Step 6: Test API Endpoints

```bash
# Get access token
export TEMP_TOKEN=$(curl -s -X POST http://localhost:8001/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@example.com","password":"admin123"}' | python -m json.tool | grep temp_token | cut -d'"' -f4)

export ACCESS_TOKEN=$(curl -s -X POST http://localhost:8001/api/v1/auth/verify-otp \
  -H "Content-Type: application/json" \
  -d "{\"temp_token\":\"$TEMP_TOKEN\",\"otp_code\":\"000000\"}" | python -m json.tool | grep access_token | cut -d'"' -f4)

# Test module settings endpoint
curl -X GET http://localhost:8005/api/v1/admin/module-settings/ \
  -H "Authorization: Bearer $ACCESS_TOKEN" | python -m json.tool

# Test trash config endpoint
curl -X GET http://localhost:8005/api/v1/admin/trash/config/ \
  -H "Authorization: Bearer $ACCESS_TOKEN" | python -m json.tool

# Test trash stats endpoint
curl -X GET http://localhost:8005/api/v1/admin/trash/stats \
  -H "Authorization: Bearer $ACCESS_TOKEN" | python -m json.tool

# Check API documentation
# Open in browser: http://localhost:8005/docs
```

### Step 7: Verify Scheduled Tasks

```bash
# Check if scheduler started
docker compose logs admin-api | grep -i "trash cleanup scheduler"

# Should see:
# "Trash cleanup scheduler started successfully"

# Test manual cleanup
curl -X POST http://localhost:8005/api/v1/admin/trash/cleanup/scheduled \
  -H "Authorization: Bearer $ACCESS_TOKEN" | python -m json.tool
```

### Step 8: Update Nginx Configuration

The nginx configuration should already include the admin-api routes. Verify:

```bash
# Check nginx config includes admin-api
docker compose exec nginx cat /etc/nginx/nginx.conf | grep -A 10 "admin-api"

# Should see the upstream and location blocks

# Reload nginx if needed
docker compose exec nginx nginx -s reload
```

### Step 9: Test via API Gateway

```bash
# Test via API Gateway (port 8000)
curl -X GET http://localhost:8000/api/v1/admin/trash/stats \
  -H "Authorization: Bearer $ACCESS_TOKEN" | python -m json.tool

# Should return trash statistics
```

## Troubleshooting

### Issue: Database Permission Denied

**Error**: `(1044, "Access denied for user 'officework'@'%' to database 'admin_db'")`

**Solution**: MySQL needs to be recreated with updated init.sql (see Step 1)

### Issue: Migration Fails with URL Encoding Error

**Error**: `ValueError: invalid interpolation syntax`

**Solution**: Already fixed in [alembic/env.py](alembic/env.py:42). If you see this, ensure you have the latest code.

### Issue: Admin API Unhealthy

**Symptoms**: `docker compose ps` shows admin-api as unhealthy

**Debug**:
```bash
# Check logs
docker compose logs admin-api --tail 100

# Check if database is accessible
docker compose exec admin-api python -c "from app.core.database import engine; print(engine.connect())"

# Restart service
docker compose restart admin-api
```

### Issue: Trash Cleanup Not Running

**Debug**:
```bash
# Check scheduler logs
docker compose logs admin-api | grep -i scheduler

# Run manual cleanup
docker compose exec admin-api python -m app.tasks.trash_cleanup

# Check APScheduler jobs
docker compose exec admin-api python -c "from app.tasks.trash_cleanup import scheduler; print(scheduler.get_jobs())"
```

### Issue: Missing Dependencies

**Error**: `ModuleNotFoundError: No module named 'apscheduler'`

**Solution**:
```bash
# Rebuild with updated requirements.txt
docker compose build admin-api
docker compose up -d admin-api
```

## Rollback Procedure

If you need to rollback the deployment:

### Rollback Database Migrations

```bash
docker compose exec admin-api alembic downgrade 001

# Or rollback all the way
docker compose exec admin-api alembic downgrade base
```

### Restore MySQL Backup

```bash
# If you made a backup in Step 1
docker exec -i mysql mysql -uroot -p$(cat .secrets/mysql_root_passwd.txt) < backup.sql
```

### Revert Code Changes

```bash
# Checkout previous version
git checkout <previous-commit-hash>

# Rebuild and restart
docker compose build admin-api
docker compose up -d admin-api
```

## Post-Deployment Checklist

- [ ] MySQL container recreated with admin_db
- [ ] Database migrations applied successfully
- [ ] All 7 tables created in admin_db
- [ ] Default system_modules data inserted
- [ ] Default trash_config data inserted
- [ ] Admin API responds to health check
- [ ] Module settings endpoints working
- [ ] Trash endpoints working
- [ ] Trash cleanup scheduler running
- [ ] Nginx routing configured
- [ ] API Gateway routes working
- [ ] API documentation accessible

## Monitoring

### Health Checks

```bash
# Admin API health
curl http://localhost:8005/health

# Via API Gateway
curl http://localhost:8000/api/v1/admin/health
```

### Logs

```bash
# Real-time logs
docker compose logs -f admin-api

# Filter for errors
docker compose logs admin-api | grep ERROR

# Filter for trash cleanup
docker compose logs admin-api | grep "trash cleanup"
```

### Database Monitoring

```bash
# Check trash item count
docker exec mysql mysql -uroot -p$(cat .secrets/mysql_root_passwd.txt) admin_db -e \
  "SELECT COUNT(*) as trash_items FROM trash_items;"

# Check trash by module
docker exec mysql mysql -uroot -p$(cat .secrets/mysql_root_passwd.txt) admin_db -e \
  "SELECT module_name, COUNT(*) as count FROM trash_items GROUP BY module_name;"

# Check recent audit logs
docker exec mysql mysql -uroot -p$(cat .secrets/mysql_root_passwd.txt) admin_db -e \
  "SELECT action, module_name, resource_type, created_at FROM audit_logs ORDER BY created_at DESC LIMIT 10;"
```

## Production Considerations

### Before Production Deployment

1. **Security Review**
   - Ensure all endpoints require authentication
   - Review permanent delete confirmation requirements
   - Audit trail for all operations

2. **Performance Testing**
   - Test with large trash datasets (1000+ items)
   - Benchmark cleanup operations
   - Monitor database growth

3. **Backup Strategy**
   - Automated MySQL backups
   - Trash retention policy
   - Disaster recovery procedures

4. **Monitoring & Alerts**
   - Set up monitoring for trash size
   - Alert on failed cleanup jobs
   - Track restore success rate

5. **Documentation**
   - User guide for trash management
   - Admin procedures
   - API integration guide

### Production Environment Variables

Update docker-compose.yml for production:

```yaml
admin-api:
  environment:
    ENVIRONMENT: production
    DEBUG: "false"
    # ... other production settings
```

## Support

For issues or questions:
- Check logs: `docker compose logs admin-api`
- Review API docs: http://localhost:8005/docs
- See [TRASH_FEATURE_GUIDE.md](TRASH_FEATURE_GUIDE.md) for usage guide
- Check [services/admin-api/README.md](README.md) for API documentation

## Version History

- **v1.0.0** - Initial release
  - Module settings management
  - Audit logging
  - System monitoring

- **v1.1.0** - Trash/Recycle Bin feature
  - Soft delete functionality
  - Trash management endpoints
  - Automatic cleanup scheduler
  - SoftDeleteMixin for models
