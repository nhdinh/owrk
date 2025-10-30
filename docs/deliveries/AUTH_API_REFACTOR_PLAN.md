# AUTH-API REFACTOR PLAN

## Mục tiêu
Refactor auth-api để đáp ứng đầy đủ các yêu cầu kiến trúc mới từ `03. System_Architecture.md` section 5.1

## Các yêu cầu bắt buộc

### 1. ✅ Repository Pattern
- **Trạng thái**: Đã có
- **Location**: `app/repositories/`
- **Files**: `base_repository.py`, `user_repository.py`, `role_repository.py`

### 2. ✅ Unit of Work Pattern
- **Trạng thái**: Đã có
- **Location**: `app/core/unit_of_work.py`

### 3. ✅ CQRS Pattern - Commands & Queries
- **Trạng thái**: Đã tạo cấu trúc cơ bản
- **Created**:
  - `app/core/message_bus.py` - Message Bus implementation
  - `app/schemas/commands/` - Command DTOs
  - `app/schemas/queries/` - Query DTOs
- **Cần làm tiếp**:
  - Tạo Command Handlers
  - Tạo Query Handlers
  - Tích hợp Message Bus vào API endpoints

### 4. ✅ Service Layer
- **Trạng thái**: Đã có
- **Location**: `app/services/auth_service.py`

### 5. ✅ RabbitMQ Integration
- **Trạng thái**: Đã có
- **Location**: `app/core/rabbitmq.py`, `app/consumers/`

### 6. ❌ Separate Versioning Tables
- **Trạng thái**: Chưa có
- **Cần tạo**:
  - `user_history` table
  - `role_history` table
  - Trigger/logic để tự động lưu version khi update

### 7. ✅ Read Models (MongoDB)
- **Trạng thái**: Đã tạo
- **Created**:
  - `app/read_models/user_read_model.py`
  - `app/read_repositories/user_read_repository.py`

## Cấu trúc thư mục mới

```
services/auth-api/app/
├── __init__.py
├── main.py
├── api/
│   └── v1/
│       ├── endpoints/      # API routes (thin layer)
│       │   ├── auth.py     # Chỉ gọi Command/Query handlers
│       │   ├── users.py
│       │   └── roles.py
│       └── router.py
├── commands/               # ✅ NEW - CQRS Write side
│   ├── __init__.py
│   └── handlers/
│       ├── __init__.py
│       ├── create_user_handler.py
│       ├── update_user_handler.py
│       ├── delete_user_handler.py
│       ├── login_handler.py
│       └── verify_otp_handler.py
├── queries/                # ✅ NEW - CQRS Read side
│   ├── __init__.py
│   └── handlers/
│       ├── __init__.py
│       ├── get_user_handler.py
│       ├── get_users_list_handler.py
│       └── search_users_handler.py
├── core/
│   ├── __init__.py
│   ├── config.py
│   ├── database.py         # MySQL connection
│   ├── mongo_db.py         # MongoDB connection
│   ├── rabbitmq.py
│   ├── security.py
│   ├── dependencies.py
│   ├── unit_of_work.py
│   ├── message_bus.py      # ✅ NEW
│   └── events.py
├── models/                 # SQLAlchemy models (Write DB - MySQL)
│   ├── __init__.py
│   ├── base.py
│   ├── user.py
│   ├── user_history.py     # ✅ NEW - Versioning table
│   ├── role.py
│   └── role_history.py     # ✅ NEW - Versioning table
├── read_models/            # ✅ NEW - MongoDB models
│   ├── __init__.py
│   └── user_read_model.py
├── repositories/           # Write repositories (MySQL)
│   ├── __init__.py
│   ├── base_repository.py
│   ├── user_repository.py
│   └── role_repository.py
├── read_repositories/      # ✅ NEW - Read repositories (MongoDB)
│   ├── __init__.py
│   └── user_read_repository.py
├── schemas/
│   ├── __init__.py
│   ├── auth_schema.py      # Keep for backward compatibility
│   ├── user_schema.py      # Keep for response DTOs
│   ├── commands/           # ✅ NEW - Command DTOs
│   │   ├── __init__.py
│   │   ├── user_commands.py
│   │   └── auth_commands.py
│   └── queries/            # ✅ NEW - Query DTOs
│       ├── __init__.py
│       └── user_queries.py
├── services/               # Domain services (business logic)
│   ├── __init__.py
│   └── auth_service.py
├── consumers/              # RabbitMQ event consumers
│   ├── __init__.py
│   └── user_event_consumer.py
└── utils/
    ├── __init__.py
    └── helpers.py
```

## Các bước thực hiện

### Phase 1: Tạo Versioning Tables ✅ Cần làm ngay

1. **Tạo UserHistory model**
   - File: `app/models/user_history.py`
   - Chứa snapshot của User entity mỗi khi có thay đổi
   - Fields: id, user_id, version, changed_at, changed_by, + all user fields

2. **Tạo RoleHistory model**
   - File: `app/models/role_history.py`
   - Tương tự như UserHistory

3. **Tạo Alembic migration**
   - Tạo bảng `user_history`
   - Tạo bảng `role_history`
   - Tạo indexes

### Phase 2: Tạo Command Handlers

1. **User Commands**
   - `CreateUserHandler` - Tạo user mới
   - `UpdateUserHandler` - Update user info (save to history)
   - `DeleteUserHandler` - Soft delete user
   - `ActivateUserHandler` - Kích hoạt user
   - `DeactivateUserHandler` - Vô hiệu hóa user

2. **Auth Commands**
   - `LoginHandler` - Xử lý login step 1
   - `VerifyOTPHandler` - Xử lý OTP verification
   - `RefreshTokenHandler` - Refresh token
   - `LogoutHandler` - Đăng xuất

### Phase 3: Tạo Query Handlers

1. **User Queries**
   - `GetUserByIdHandler` - Get user by ID (from MongoDB)
   - `GetUserByEmailHandler` - Get user by email
   - `GetUsersListHandler` - List users with pagination/filters
   - `SearchUsersHandler` - Full-text search
   - `GetUserHistoryHandler` - Get version history

### Phase 4: Refactor API Endpoints

1. **Refactor `/api/v1/endpoints/users.py`**
   - Remove business logic
   - Use MessageBus to dispatch Commands/Queries
   - Keep only validation và error handling

2. **Refactor `/api/v1/endpoints/auth.py`**
   - Tương tự như users.py

3. **Example**:
```python
@router.post("/users", response_model=UserResponse)
async def create_user(
    user_data: UserCreate,
    current_user: User = Depends(get_current_user),
    bus: MessageBus = Depends(get_message_bus)
):
    # Create command
    command = CreateUserCommand(
        email=user_data.email,
        full_name=user_data.full_name,
        password=user_data.password,
        role_id=user_data.role_id,
        created_by=current_user.id
    )

    # Execute via Message Bus
    result = await bus.execute_command(command)
    return result
```

### Phase 5: Register Handlers với Message Bus

1. **Update `app/main.py`**
   - Import tất cả handlers
   - Register với message_bus khi startup

```python
from app.core.message_bus import message_bus
from app.commands.handlers import CreateUserHandler, UpdateUserHandler
from app.queries.handlers import GetUserByIdHandler

@app.on_event("startup")
async def register_handlers():
    # Register command handlers
    message_bus.register_command_handler(CreateUserCommand, CreateUserHandler())
    message_bus.register_command_handler(UpdateUserCommand, UpdateUserHandler())

    # Register query handlers
    message_bus.register_query_handler(GetUserByIdQuery, GetUserByIdHandler())
```

### Phase 6: Testing

1. **Unit Tests**
   - Test command handlers
   - Test query handlers
   - Test versioning logic

2. **Integration Tests**
   - Test API endpoints
   - Test event publishing
   - Test MongoDB sync

3. **Docker Compose Test**
   - Build và restart auth-api
   - Test all endpoints
   - Verify data in MySQL và MongoDB

## Priority Order

### 🔥 HIGH PRIORITY (Làm ngay)
1. ✅ Message Bus - DONE
2. ✅ Command/Query DTOs - DONE
3. ✅ Read Models - DONE
4. ❌ Versioning Tables (UserHistory, RoleHistory)
5. ❌ Command Handlers (at least CreateUser, UpdateUser)
6. ❌ Query Handlers (at least GetUser, GetUsersList)

### 📋 MEDIUM PRIORITY (Làm sau)
7. Refactor API endpoints
8. Register all handlers
9. Update event consumers

### ✨ LOW PRIORITY (Optional)
10. Full test coverage
11. Performance optimization
12. Documentation

## Files Created So Far

✅ **DONE**:
- `app/core/message_bus.py` - Message Bus implementation
- `app/schemas/commands/__init__.py`
- `app/schemas/commands/user_commands.py` - User command DTOs
- `app/schemas/commands/auth_commands.py` - Auth command DTOs
- `app/schemas/queries/__init__.py`
- `app/schemas/queries/user_queries.py` - User query DTOs
- `app/read_models/__init__.py`
- `app/read_models/user_read_model.py` - Denormalized user model
- `app/read_repositories/__init__.py`
- `app/read_repositories/user_read_repository.py` - MongoDB repository

## Next Steps

1. **Tạo UserHistory và RoleHistory models**
2. **Tạo Alembic migration cho versioning tables**
3. **Implement CreateUserHandler và UpdateUserHandler với versioning logic**
4. **Implement GetUserByIdHandler và GetUsersListHandler**
5. **Test handlers independently**
6. **Refactor một endpoint để demo (ví dụ: POST /users)**

## Notes

- Tất cả Command handlers phải save version history
- Tất cả Command handlers phải publish events to RabbitMQ
- Tất cả Query handlers phải đọc từ MongoDB (fast reads)
- Write operations vẫn dùng MySQL (strong consistency)
- Event consumers sẽ sync data từ MySQL sang MongoDB

## Estimated Effort

- **Phase 1 (Versioning)**: 2-3 hours
- **Phase 2 (Command Handlers)**: 4-5 hours
- **Phase 3 (Query Handlers)**: 2-3 hours
- **Phase 4 (Refactor Endpoints)**: 3-4 hours
- **Phase 5 (Register Handlers)**: 1-2 hours
- **Phase 6 (Testing)**: 3-4 hours

**Total**: ~15-21 hours

## References

- Architecture Doc: `docs/03. System_Architecture.md` section 5.1
- CQRS Pattern: https://martinfowler.com/bliki/CQRS.html
- Repository Pattern: https://docs.microsoft.com/en-us/dotnet/architecture/microservices/microservice-ddd-cqrs-patterns/infrastructure-persistence-layer-design
