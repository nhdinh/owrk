# 🚀 DEPLOYMENT - TRIỂN KHAI & VẬN HÀNH

## Giới thiệu

Thư mục này chứa tất cả tài liệu liên quan đến **deployment, CI/CD, monitoring và vận hành hệ thống**.

---

## 📚 Danh sách Tài liệu

### 1. [Docker_Setup.md](Docker_Setup.md) ✅
**Mô tả**: Hướng dẫn setup Docker và Docker Compose cho dự án

**Nội dung chính**:
- **Docker Compose Configuration**:
  - 6 microservices
  - PostgreSQL, Redis, RabbitMQ
  - Nginx API Gateway
- **Container Status**: Health checks, restart policies
- **Networking**: Internal network cho services
- **Volumes**: Data persistence
- **Environment Variables**: Configuration management

**Commands**:
```bash
docker-compose up -d              # Start all services
docker-compose down               # Stop all services
docker-compose logs -f [service]  # View logs
docker-compose ps                 # Service status
```

**Đối tượng đọc**: DevOps Engineers, Developers

---

### 2. [CI_CD_Pipeline.md](CI_CD_Pipeline.md) 📝 TODO
**Mô tả**: GitHub Actions workflow cho CI/CD

**Nội dung dự kiến**:

#### CI Pipeline (Continuous Integration)
```yaml
# .github/workflows/ci.yml
name: CI Pipeline

on:
  push:
    branches: [develop, main]
  pull_request:
    branches: [develop]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-cov

      - name: Run tests
        run: pytest --cov=app --cov-report=xml

      - name: Upload coverage
        uses: codecov/codecov-action@v3

  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run linters
        run: |
          black --check .
          flake8 .
          mypy .
```

#### CD Pipeline (Continuous Deployment)
```yaml
# .github/workflows/cd.yml
name: CD Pipeline

on:
  push:
    branches: [develop, main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - name: Build Docker images
        run: docker-compose build

      - name: Push to registry
        run: docker-compose push

      - name: Deploy to staging (develop)
        if: github.ref == 'refs/heads/develop'
        run: |
          ssh deploy@staging "cd /app && docker-compose pull && docker-compose up -d"

      - name: Deploy to production (main)
        if: github.ref == 'refs/heads/main'
        run: |
          ssh deploy@prod "cd /app && docker-compose pull && docker-compose up -d"
```

**Deployment Strategy**: Blue-Green Deployment

**Đối tượng đọc**: DevOps Engineers

---

### 3. [Production_Deployment.md](Production_Deployment.md) 📝 TODO
**Mô tả**: Hướng dẫn deploy production

**Nội dung dự kiến**:

#### Pre-deployment Checklist
- [ ] All tests passing
- [ ] Security scan passed
- [ ] Database backup created
- [ ] Rollback plan prepared
- [ ] Stakeholders notified
- [ ] Maintenance window scheduled

#### Production Environment
```yaml
# Infrastructure
- Cloud Provider: AWS / Azure / GCP
- Region: [Your Region]
- Availability Zones: Multi-AZ

# Compute
- EC2 Instances: 3x t3.large (8GB RAM, 2 vCPU)
- Load Balancer: Application Load Balancer
- Auto Scaling: Min 2, Max 6 instances

# Database
- RDS PostgreSQL: db.t3.medium (Multi-AZ)
- ElastiCache Redis: cache.t3.micro
- RabbitMQ: Amazon MQ

# Storage
- S3: File storage (invoices, warranties)
- CloudFront: CDN for static assets

# Security
- VPC: Private subnets for backend
- Security Groups: Restricted access
- SSL Certificate: AWS Certificate Manager
- WAF: DDoS protection
```

#### Deployment Steps
1. **Backup**: Create database snapshot
2. **Database Migration**: Run Alembic migrations
3. **Build**: Build Docker images
4. **Deploy**: Blue-green deployment
5. **Smoke Test**: Verify critical endpoints
6. **Monitor**: Watch metrics for 1 hour
7. **Rollback**: If issues detected

#### Rollback Procedure
```bash
# Rollback to previous version
docker-compose down
docker-compose pull [previous-tag]
docker-compose up -d

# Rollback database
psql -U postgres -d asset_management < backup_[timestamp].sql
```

**Đối tượng đọc**: DevOps Engineers, Tech Lead

---

### 4. [Monitoring_Guide.md](Monitoring_Guide.md) 📝 TODO
**Mô tả**: Setup monitoring, logging và alerting

**Nội dung dự kiến**:

#### Monitoring Stack
```
┌─────────────────────────────────────┐
│         Grafana Dashboard           │
│  (Visualization & Alerting)         │
└────────────┬────────────────────────┘
             │
             ▼
┌─────────────────────────────────────┐
│          Prometheus                 │
│  (Metrics Collection & Storage)     │
└────────────┬────────────────────────┘
             │
             ▼
┌─────────────────────────────────────┐
│     Application Services            │
│  (Expose /metrics endpoint)         │
└─────────────────────────────────────┘
```

#### Key Metrics
**Application Metrics**:
- Request rate (requests/sec)
- Response time (p50, p95, p99)
- Error rate (4xx, 5xx)
- Active users

**System Metrics**:
- CPU usage
- Memory usage
- Disk I/O
- Network bandwidth

**Database Metrics**:
- Connection pool size
- Query execution time
- Slow queries
- Deadlocks

#### Alerting Rules
```yaml
# prometheus/alerts.yml
groups:
  - name: application_alerts
    rules:
      - alert: HighErrorRate
        expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.05
        for: 5m
        annotations:
          summary: "High error rate detected"

      - alert: SlowResponse
        expr: http_request_duration_seconds{quantile="0.95"} > 1
        for: 5m
        annotations:
          summary: "API response time > 1s"

      - alert: HighMemoryUsage
        expr: container_memory_usage_bytes / container_spec_memory_limit_bytes > 0.9
        for: 5m
        annotations:
          summary: "Container memory usage > 90%"
```

#### Logging Stack (ELK)
```
Application Logs → Logstash → Elasticsearch → Kibana
```

**Log Levels**:
- ERROR: Application errors
- WARN: Warning conditions
- INFO: Informational messages
- DEBUG: Debug information (dev only)

**Log Format** (JSON):
```json
{
  "timestamp": "2025-10-20T10:30:00Z",
  "level": "ERROR",
  "service": "auth-service",
  "message": "Failed to verify OTP",
  "user_id": 123,
  "trace_id": "abc123",
  "error": "Invalid OTP code"
}
```

#### Dashboards
- **Overview Dashboard**: System health, key metrics
- **Service Dashboard**: Per-service metrics
- **Database Dashboard**: Database performance
- **Business Dashboard**: Business metrics (assets, requests, etc.)

**Đối tượng đọc**: DevOps Engineers, SRE, Tech Lead

---

## 🔧 Environment Configuration

### Development
```bash
# .env.development
DEBUG=true
LOG_LEVEL=DEBUG
DATABASE_URL=postgresql://user:pass@localhost:5432/asset_dev
REDIS_URL=redis://localhost:6379/0
```

### Staging
```bash
# .env.staging
DEBUG=false
LOG_LEVEL=INFO
DATABASE_URL=postgresql://user:pass@staging-db:5432/asset_staging
REDIS_URL=redis://staging-redis:6379/0
```

### Production
```bash
# .env.production (stored in AWS Secrets Manager)
DEBUG=false
LOG_LEVEL=WARNING
DATABASE_URL=postgresql://user:pass@prod-db.rds.amazonaws.com:5432/asset_prod
REDIS_URL=redis://prod-redis.elasticache.amazonaws.com:6379/0
```

---

## 🔐 Secrets Management

### Development
- `.env.local` files (not committed to git)

### Staging/Production
- **AWS Secrets Manager**: Database credentials, API keys
- **Environment Variables**: Non-sensitive config
- **Rotation**: Automatic secret rotation every 90 days

```python
# Example: Retrieve secrets
import boto3

client = boto3.client('secretsmanager')
secret = client.get_secret_value(SecretId='prod/database/password')
database_password = secret['SecretString']
```

---

## 📊 Performance Targets

| Environment | Response Time | Uptime | Concurrent Users |
|-------------|---------------|--------|------------------|
| Development | < 500ms | - | 10 |
| Staging | < 300ms | 95% | 100 |
| Production | < 200ms | 99.5% | 1000+ |

---

## 🔄 Deployment Schedule

### Staging
- **Automatic**: Every push to `develop` branch
- **Frequency**: Multiple times per day

### Production
- **Scheduled**: Weekly on Saturday 2:00 AM
- **Emergency**: Anytime for critical fixes
- **Maintenance Window**: Saturday 2:00 AM - 6:00 AM

---

## 🆘 Incident Response

### Severity Levels
- **P1 (Critical)**: System down, data loss
  - Response: < 15 minutes
  - Resolution: < 2 hours

- **P2 (High)**: Major feature broken
  - Response: < 1 hour
  - Resolution: < 8 hours

- **P3 (Medium)**: Minor feature broken
  - Response: < 4 hours
  - Resolution: < 24 hours

- **P4 (Low)**: UI issue, minor bug
  - Response: < 24 hours
  - Resolution: Next sprint

### On-Call Rotation
- **Primary**: Tech Lead
- **Secondary**: Senior Developer
- **Escalation**: CTO

### Incident Process
1. **Detect**: Alert triggered
2. **Respond**: On-call engineer responds
3. **Diagnose**: Identify root cause
4. **Resolve**: Implement fix
5. **Document**: Write incident report
6. **Improve**: Implement preventive measures

---

## 📈 Capacity Planning

### Current Capacity
- Users: 100 active users
- Requests: 1,000 req/min
- Storage: 100 GB

### 6-Month Projection
- Users: 500 active users (5x growth)
- Requests: 5,000 req/min
- Storage: 500 GB

### Scaling Strategy
- **Horizontal Scaling**: Add more instances
- **Vertical Scaling**: Upgrade instance types
- **Database Sharding**: If > 1TB data
- **CDN**: For static assets

---

## 🔗 Tài liệu Liên quan

### Upstream
- [System Architecture](../design/01_System_Architecture.md)
- [Implementation Plan](../development/Implementation_Plan.md)

### External Resources
- [Docker Documentation](https://docs.docker.com)
- [GitHub Actions Docs](https://docs.github.com/en/actions)
- [Prometheus Docs](https://prometheus.io/docs)
- [AWS Best Practices](https://aws.amazon.com/architecture/well-architected)

---

## 👥 Liên hệ

- **DevOps Lead**: devops@assetmanagement.com
- **On-Call**: oncall@assetmanagement.com
- **Emergency**: +84-xxx-xxx-xxx

---

[⬅️ Back to Development](../development/README.md) | [⬅️ Back to Index](../INDEX.md) | [➡️ Next: Guides](../guides/README.md)
