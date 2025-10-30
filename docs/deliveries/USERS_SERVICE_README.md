# Users API and Frontend Services

## Overview

This document describes the new **users-api** and **users-frontend** microservices that have been separated from the auth-api service for better modularity and separation of concerns.

## Architecture

### Services Created

1. **users-api** (Port 8090)
   - Handles user and role management
   - Shares the `auth_db` database with auth-api
   - Provides REST API endpoints for user CRUD operations
   - Manages role and permission assignments

2. **users-frontend** (Port 3002)
   - User interface for user and role management
   - Built with FastAPI + Jinja2 templates
   - Bootstrap-based responsive UI

## API Endpoints

### Users API (users-api:8000)

#### User Management
- `GET /api/v1/users` - List all users (with pagination and filtering)
- `GET /api/v1/users/active` - Get active users only
- `GET /api/v1/users/{user_id}` - Get user by ID
- `POST /api/v1/users` - Create new user
- `PUT /api/v1/users/{user_id}` - Update user
- `DELETE /api/v1/users/{user_id}` - Soft delete user
- `POST /api/v1/users/{user_id}/activate` - Activate user
- `POST /api/v1/users/{user_id}/deactivate` - Deactivate user
- `POST /api/v1/users/{user_id}/unlock` - Unlock locked user
- `POST /api/v1/users/change-password` - Change current user's password
- `POST /api/v1/users/{user_id}/reset-password` - Admin: Reset user password

#### Role Management
- `GET /api/v1/roles` - List all roles
- `GET /api/v1/roles/{role_id}` - Get role details
- `POST /api/v1/roles` - Create new role
- `PUT /api/v1/roles/{role_id}` - Update role
- `DELETE /api/v1/roles/{role_id}` - Soft delete role

#### Permission Management
- `GET /api/v1/roles/permissions/all` - Get all permissions
- `POST /api/v1/roles/{role_id}/permissions/{permission_id}` - Add permission to role
- `DELETE /api/v1/roles/{role_id}/permissions/{permission_id}` - Remove permission from role

## Frontend Routes

### Users Frontend (users-fe:3002)

- `/users/` - List all users
- `/users/create` - Create new user form
- `/users/{user_id}` - View user details
- `/roles/` - List all roles
- `/roles/{role_id}` - View role details

## Nginx Routing

The API Gateway (Nginx) routes requests as follows:

- `http://localhost:8000/api/v1/users/*` → users-api
- `http://localhost:8000/api/v1/roles/*` → users-api
- `http://localhost:8000/users/*` → users-fe
- `http://localhost:8000/roles/*` → users-fe
- `http://localhost:8000/docs/users` → users-api Swagger docs

## Database Shared Schema

Both auth-api and users-api share the same MySQL database (`auth_db`):

### Tables Used
- `users` - User accounts
- `roles` - Role definitions
- `permissions` - Permission definitions
- `role_permissions` - Many-to-many relationship

## Security

### Authentication
All API endpoints require JWT authentication except for read-only operations that may be configured differently.

### Authorization
Endpoints use permission-based access control:
- `user:read` - View users
- `user:create` - Create users
- `user:update` - Update users
- `user:delete` - Delete users
- `role:read` - View roles
- `role:create` - Create roles
- `role:update` - Update roles
- `role:delete` - Delete roles

## Running the Services

### Start Services
```bash
# Start infrastructure (MySQL, MongoDB, Redis, RabbitMQ)
docker start mysql mongodb redis rabbitmq

# Build and start users services
docker compose build users-api users-fe
docker compose up -d users-api users-fe
```

### Check Status
```bash
docker compose ps users-api users-fe
```

### View Logs
```bash
docker compose logs -f users-api
docker compose logs -f users-fe
```

## Accessing Services

- **Users API Docs**: http://localhost:8090/docs
- **Users Frontend**: http://localhost:3002/users
- **Via Gateway**: http://localhost:8000/users
- **API via Gateway**: http://localhost:8000/api/v1/users

## Development

### Directory Structure

```
services/
├── users-api/
│   ├── app/
│   │   ├── api/v1/endpoints/  # API routes
│   │   ├── core/              # Config, security, dependencies
│   │   ├── models/            # SQLAlchemy models
│   │   ├── schemas/           # Pydantic schemas
│   │   ├── repositories/      # Data access layer
│   │   ├── services/          # Business logic
│   │   └── main.py            # App entry point
│   ├── Dockerfile
│   └── requirements.txt
│
└── users-frontend/
    ├── app/
    │   ├── templates/         # Jinja2 templates
    │   ├── static/            # CSS, JS
    │   ├── routers/           # Route handlers
    │   └── main.py
    ├── Dockerfile
    └── requirements.txt
```

### Adding New Endpoints

1. Create schema in `app/schemas/`
2. Add business logic in `app/services/` (if needed)
3. Create endpoint in `app/api/v1/endpoints/`
4. Update router in `app/api/v1/router.py`

### Testing

Access the Swagger documentation to test API endpoints:
```
http://localhost:8090/docs
```

Or use curl:
```bash
# Get access token from auth service first
TOKEN=$(curl -s -X POST http://localhost:8088/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@example.com","password":"admin123"}' \
  | jq -r '.temp_token')

# List users
curl -X GET http://localhost:8090/api/v1/users \
  -H "Authorization: Bearer $TOKEN"
```

## Migration from auth-api

The following endpoints have been MOVED from auth-api to users-api:
- `/api/v1/users/*` - All user management endpoints
- `/api/v1/roles/*` - All role management endpoints

**Important**: Update any clients calling these endpoints to use the new service or route through the Nginx gateway which handles the routing automatically.

## Future Enhancements

1. **Department Management**: Add dedicated endpoints for department CRUD
2. **Bulk Operations**: Support bulk user creation/updates
3. **Advanced Filtering**: Add more filter options (by department, role, date range)
4. **User Import/Export**: CSV/Excel import and export
5. **Activity Audit**: Track user management actions
6. **Permission Templates**: Pre-defined permission sets for common roles

## Troubleshooting

### Service Won't Start
Check logs:
```bash
docker compose logs users-api
docker compose logs users-fe
```

### Database Connection Issues
Verify MySQL is running and accessible:
```bash
docker exec -it mysql mysql -uofficework_dbu -p -e "USE auth_db; SHOW TABLES;"
```

### Permission Denied Errors
Ensure the user has the required permissions:
- Check user's role in database
- Verify role has necessary permissions
- Check JWT token is valid and not expired

## Contact

For questions or issues, please refer to:
- Main Project README: [README.md](README.md)
- Architecture Documentation: [docs/03. System_Architecture.md](docs/03.%20System_Architecture.md)
- API Specification: [docs/05. API_Specification.md](docs/05. API_Specification.md)
