# Quick Start Guide - Office Equipment Asset Management System

**Date**: 2025-10-31
**Version**: 2.0
**Status**: Production Ready

---

## 🚀 Quick Access

### Primary URL (API Gateway)
**http://localhost:8000**

### Login Credentials
- **Email**: `admin@example.com`
- **Password**: `admin123`
- **OTP** (if prompted): `000000`

---

## 📋 Table of Contents

1. [Starting the System](#1-starting-the-system)
2. [Accessing Services](#2-accessing-services)
3. [Service Ports](#3-service-ports)
4. [Common Operations](#4-common-operations)
5. [Troubleshooting](#5-troubleshooting)

---

## 1. Starting the System

### Option A: Start Everything

```bash
cd c:\Users\nhdinh\dev\officework
docker compose up -d
```

Wait 30-60 seconds for all services to become healthy.

### Option B: Start Specific Services

```bash
# Start infrastructure only
docker compose up -d mysql mongodb redis rabbitmq

# Start APIs
docker compose up -d auth-api asset-api

# Start frontends
docker compose up -d auth-fe-v2 asset-fe-v2

# Start API gateway
docker compose up -d nginx
```

### Check Status

```bash
# View all services
docker ps

# Or use docker-compose
docker compose ps
```

---

## 2. Accessing Services

### 🌟 Recommended Access (via API Gateway)

All services are accessible through the unified gateway at **http://localhost:8000**

| What You Want                | URL                                      |
|------------------------------|------------------------------------------|
| **Login to System**          | http://localhost:8000/auth/              |
| **Manage Assets**            | http://localhost:8000/assets/            |
| **Manage Users**             | http://localhost:8000/auth/users         |
| **Manage Roles**             | http://localhost:8000/auth/roles         |
| **View API Documentation**   | http://localhost:8000/docs               |
| **Health Check**             | http://localhost:8000/health             |

### 🔧 Direct Access (Development/Testing)

| Service              | Direct URL              | Purpose                  |
|----------------------|-------------------------|--------------------------|
| Auth Frontend V2     | http://localhost:3100   | Bypass gateway           |
| Asset Frontend V2    | http://localhost:3200   | Bypass gateway           |
| Auth API             | http://localhost:8001   | Direct API access        |
| Asset API            | http://localhost:8002   | Direct API access        |
| RabbitMQ Management  | http://localhost:15672  | Message queue admin      |

---

## 3. Service Ports

### Active Services

| Service         | Port | Protocol | Access                          |
|-----------------|------|----------|---------------------------------|
| API Gateway     | 8000 | HTTP     | http://localhost:8000           |
| Auth API        | 8001 | HTTP     | http://localhost:8001           |
| Asset API       | 8002 | HTTP     | http://localhost:8002           |
| Auth Frontend   | 3100 | HTTP     | http://localhost:3100           |
| Asset Frontend  | 3200 | HTTP     | http://localhost:3200           |
| MySQL           | 3306 | TCP      | mysql://localhost:3306          |
| MongoDB         | 27017| TCP      | mongodb://localhost:27017       |
| Redis           | 6379 | TCP      | redis://localhost:6379          |
| RabbitMQ        | 5672 | AMQP     | amqp://localhost:5672           |
| RabbitMQ Mgmt   | 15672| HTTP     | http://localhost:15672          |

### Stopped Services (Legacy)

| Service         | Port | Status  | Replaced By        |
|-----------------|------|---------|-------------------|
| auth-fe (v1)    | 3000 | Stopped | auth-fe-v2        |
| asset-fe (v1)   | 3001 | Stopped | asset-fe-v2       |

---

## 4. Common Operations

### 4.1. Login to System

1. Open browser: http://localhost:8000
2. You'll be redirected to: http://localhost:8000/auth/
3. Enter credentials:
   - Email: `admin@example.com`
   - Password: `admin123`
4. If prompted for OTP, enter: `000000`
5. Click "Login"

### 4.2. Manage Assets

1. After login, navigate to: http://localhost:8000/assets/
2. Or click "Assets" in the navigation menu
3. Available operations:
   - **View Assets**: Browse the asset list
   - **Search**: Use the search bar to find assets
   - **Filter**: Filter by category, status, or type
   - **Create New**: Click "Create Asset" button
   - **View Details**: Click "View" on any asset
   - **Edit**: Click "Edit" on any asset
   - **Delete**: Click "Delete" on any asset (with confirmation)

### 4.3. Manage Users

1. Navigate to: http://localhost:8000/auth/users
2. Available operations:
   - View user list
   - Create new users
   - Edit user details
   - Activate/Deactivate users
   - Reset passwords
   - Assign roles

### 4.4. Manage Roles

1. Navigate to: http://localhost:8000/auth/roles
2. Available operations:
   - View role list
   - Create new roles
   - Edit role details
   - Assign permissions to roles
   - Delete roles (if not in use)

### 4.5. View Logs

```bash
# All services
docker compose logs -f

# Specific service
docker compose logs -f nginx
docker compose logs -f auth-api
docker compose logs -f asset-api

# Last 100 lines
docker compose logs --tail=100 nginx
```

### 4.6. Restart Services

```bash
# Restart specific service
docker compose restart nginx
docker compose restart auth-api

# Restart all services
docker compose restart

# Stop and start (clears state)
docker compose down
docker compose up -d
```

### 4.7. View API Documentation

**Auth API Swagger**:
- Via Gateway: http://localhost:8000/docs/auth
- Direct: http://localhost:8001/docs

**Asset API Swagger**:
- Via Gateway: http://localhost:8000/docs/assets
- Direct: http://localhost:8002/docs

---

## 5. Troubleshooting

### 5.1. Can't Access http://localhost:8000

**Check if API Gateway is running**:
```bash
docker ps | grep api-gateway
```

**If not running, start it**:
```bash
docker compose up -d nginx
```

**Check logs for errors**:
```bash
docker compose logs nginx
```

### 5.2. Login Not Working

**Check auth-api is running**:
```bash
docker ps | grep auth-api
```

**Check auth-api logs**:
```bash
docker compose logs auth-api --tail=50
```

**Try direct access**:
```bash
curl -X POST http://localhost:8001/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@example.com","password":"admin123"}'
```

**Reset admin password** (if needed):
See [API_GATEWAY_CONFIGURATION.md](./API_GATEWAY_CONFIGURATION.md) section 12.

### 5.3. Assets Page Not Loading

**Check asset-api is running**:
```bash
docker ps | grep asset-api
```

**Check asset-fe-v2 is running**:
```bash
docker ps | grep asset-fe-v2
```

**Check logs**:
```bash
docker compose logs asset-api --tail=50
docker compose logs asset-fe-v2 --tail=50
```

### 5.4. 502 Bad Gateway Error

**Possible causes**:
- Backend service is down
- Backend service not responding
- Network connectivity issues

**Fix**:
```bash
# Restart backend services
docker compose restart auth-api asset-api

# Restart gateway
docker compose restart nginx

# Check if services are in same network
docker network inspect officework_backend
```

### 5.5. Services Keep Restarting

**Check resource usage**:
```bash
docker stats
```

**Check service logs for errors**:
```bash
docker compose logs --tail=100
```

**Rebuild services**:
```bash
docker compose down
docker compose build
docker compose up -d
```

### 5.6. Port Already in Use

**Find what's using the port**:
```bash
# Windows
netstat -ano | findstr :8000

# Linux/Mac
lsof -i :8000
```

**Kill the process or use different port**:
Edit `docker-compose.yml` to change port mapping.

### 5.7. Database Connection Errors

**Check database services**:
```bash
docker ps | grep -E "mysql|mongodb|redis|rabbitmq"
```

**Restart infrastructure**:
```bash
docker compose restart mysql mongodb redis rabbitmq
```

**Wait for services to be healthy**:
```bash
# Keep checking until all show (healthy)
docker ps
```

---

## 📚 Additional Resources

- [API Gateway Configuration](./API_GATEWAY_CONFIGURATION.md) - Detailed gateway setup
- [Asset Frontend V2 Complete](./ASSET_FRONTEND_V2_COMPLETE.md) - Frontend implementation guide
- [CLAUDE.md](../../CLAUDE.md) - Complete system documentation
- [System Architecture](../03.%20System_Architecture.md) - Architecture overview

---

## 🎯 Common Use Cases

### Use Case 1: Daily Development

```bash
# Start system
docker compose up -d

# Open browser
open http://localhost:8000

# View logs while working
docker compose logs -f auth-api asset-api
```

### Use Case 2: Testing API Changes

```bash
# Restart API after code change
docker compose restart auth-api

# Test via gateway
curl http://localhost:8000/api/v1/auth/login ...

# Or test directly
curl http://localhost:8001/api/v1/auth/login ...
```

### Use Case 3: Demo/Presentation

```bash
# Ensure everything is running
docker compose ps

# Open main portal
open http://localhost:8000

# Login and navigate to demo features
```

### Use Case 4: Debugging Issues

```bash
# Check all services
docker ps

# View logs from all services
docker compose logs --tail=100

# Focus on specific service
docker compose logs -f auth-api

# Restart problematic service
docker compose restart auth-api
```

---

## ⚡ Quick Commands Reference

```bash
# Start everything
docker compose up -d

# Stop everything
docker compose down

# Restart service
docker compose restart <service-name>

# View logs
docker compose logs -f <service-name>

# Check status
docker compose ps

# Rebuild and restart
docker compose up -d --build <service-name>

# Remove everything (including data)
docker compose down -v
```

---

## 🔐 Default Credentials

| Service         | Username/Email          | Password    |
|-----------------|-------------------------|-------------|
| System Admin    | admin@example.com       | admin123    |
| RabbitMQ        | guest                   | guest       |
| MySQL           | officework_dbu          | (see .secrets/) |
| MongoDB         | admin                   | (see .secrets/) |

---

## ✨ Features Available

### Authentication & Authorization
- ✅ User login with MFA support
- ✅ User management (CRUD)
- ✅ Role management (CRUD)
- ✅ Permission management
- ✅ Profile management

### Asset Management
- ✅ Asset CRUD operations
- ✅ Asset categories
- ✅ Asset search and filters
- ✅ Asset assignment tracking
- ✅ Asset history
- ✅ Financial information
- ✅ Warranty tracking

### System Features
- ✅ API Gateway for unified access
- ✅ Real-time event processing (RabbitMQ)
- ✅ CQRS pattern implementation
- ✅ Read/Write model separation
- ✅ API documentation (Swagger)
- ✅ Health monitoring

---

## 📊 System Health

**Check system health**:
```bash
curl http://localhost:8000/health
```

**Expected response**: `healthy`

**Check individual services**:
```bash
# Auth API
curl http://localhost:8001/health

# Asset API
curl http://localhost:8002/health
```

---

**Last Updated**: 2025-10-31
**Version**: 2.0
**Status**: Production Ready ✅

---

**Need Help?** Check [API_GATEWAY_CONFIGURATION.md](./API_GATEWAY_CONFIGURATION.md) for detailed configuration and troubleshooting.
