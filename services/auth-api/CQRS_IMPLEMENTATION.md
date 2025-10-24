# CQRS Pattern Implementation - Auth Service

**Date**: 2025-10-21
**Status**: ✅ Implemented
**Pattern**: Command Query Responsibility Segregation (CQRS)

---

## 📋 Overview

Auth Service has been refactored to implement the **CQRS pattern** with **Event-Driven Architecture**, following the system architecture design.

### Architecture

```
┌──────────────────────────────────────────────────────┐
│                  COMMANDS (Write)                    │
│                                                      │
│  User Action (Create/Update/Delete)                 │
│         ↓                                            │
│  AuthService (Business Logic)                       │
│         ↓                                            │
│  UserRepository (Write) → MySQL                     │
│         ↓                                            │
│  Publish Event → RabbitMQ                           │
└──────────────────────────────────────────────────────┘
                         ↓
┌──────────────────────────────────────────────────────┐
│              EVENT BUS (RabbitMQ)                    │
│  Exchange: auth.events                               │
│  Routing Keys: user.*, role.*                        │
└──────────────────────────────────────────────────────┘
                         ↓
┌──────────────────────────────────────────────────────┐
│                  QUERIES (Read)                      │
│                                                      │
│  Event Consumer listens                             │
│         ↓                                            │
│  UserReadRepository updates MongoDB                 │
│         ↓                                            │
│  Fast queries from MongoDB                          │
└──────────────────────────────────────────────────────┘
```

---

## 🗂️ File Structure

### New Files Created

```
services/auth-api/app/
├── consumers/                           # NEW: Event Consumers
│   ├── __init__.py
│   └── user_event_consumer.py          # Handles user events
├── core/
│   └── events.py                        # NEW: Domain Events
├── repositories/
│   ├── user_repository.py               # UPDATED: Publishes events
│   └── user_read_repository.py          # NEW: MongoDB read repo
└── main.py                              # UPDATED: Starts consumer
```

---

## 🔄 CQRS Components

### 1. Write Side (Commands) - MySQL

**File**: `app/repositories/user_repository.py`

**Responsibilities**:
- Handle CREATE, UPDATE, DELETE operations
- Ensure data consistency and integrity
- Publish domain events to RabbitMQ

**Key Methods**:
```python
def create(self, entity: User) -> User:
    """Create user in MySQL and publish UserCreated event"""
    user = super().create(entity)
    asyncio.create_task(UserEvents.user_created(user_to_event_data(user)))
    return user

def update(self, entity: User) -> User:
    """Update user in MySQL and publish UserUpdated event"""
    user = super().update(entity)
    asyncio.create_task(UserEvents.user_updated(user_to_event_data(user)))
    return user

def delete(self, entity_id: int) -> bool:
    """Delete user from MySQL and publish UserDeleted event"""
    result = super().delete(entity_id)
    asyncio.create_task(UserEvents.user_deleted(entity_id))
    return result
```

### 2. Read Side (Queries) - MongoDB

**File**: `app/repositories/user_read_repository.py`

**Responsibilities**:
- Handle all READ operations (queries)
- Denormalized data for fast lookups
- Updated via event consumers

**Key Methods**:
```python
async def get_by_id(self, user_id: int) -> Optional[Dict]:
    """Fast lookup by ID from MongoDB"""

async def get_by_email(self, email: str) -> Optional[Dict]:
    """Fast lookup by email (indexed)"""

async def search_users(self, search_term: str) -> List[Dict]:
    """Full-text search on name, email, username"""

async def get_users_statistics(self) -> Dict:
    """Aggregated statistics (MongoDB aggregation pipeline)"""

async def upsert_user(self, user_data: Dict) -> bool:
    """Update MongoDB (called by event consumer)"""
```

**Indexes Created**:
- `id` (unique)
- `email` (unique)
- `username`
- `role_id`
- `department_id`
- `is_active`
- `mfa_enabled`
- `user_type`
- Text index on `full_name`, `email`, `username` for search

### 3. Domain Events

**File**: `app/core/events.py`

**Event Types**:
- `user.created` - User created
- `user.updated` - User updated
- `user.deleted` - User deleted
- `user.activated` - User activated
- `user.deactivated` - User deactivated
- `user.logged_in` - User logged in
- `user.mfa_enabled` - MFA enabled
- `user.mfa_disabled` - MFA disabled
- `user.password_changed` - Password changed
- `role.created`, `role.updated`, `role.deleted` - Role events

**Event Structure**:
```json
{
  "event_type": "user.created",
  "timestamp": "2025-10-21T10:30:00.000Z",
  "service": "auth-service",
  "data": {
    "id": 1,
    "email": "user@example.com",
    "full_name": "John Doe",
    "is_active": true,
    ...
  },
  "metadata": {
    "ip_address": "192.168.1.1"
  }
}
```

**Helper Functions**:
```python
def user_to_event_data(user) -> Dict:
    """Convert User model to safe event data (excludes password)"""

def role_to_event_data(role) -> Dict:
    """Convert Role model to event data"""
```

### 4. Event Consumer

**File**: `app/consumers/user_event_consumer.py`

**Responsibilities**:
- Listen to events from RabbitMQ
- Update MongoDB read model
- Handle event failures (logging, retry)

**Event Handlers**:
```python
async def _handle_user_created(self, user_data: Dict):
    """Insert user into MongoDB"""

async def _handle_user_updated(self, user_data: Dict):
    """Update user in MongoDB"""

async def _handle_user_deleted(self, data: Dict):
    """Delete user from MongoDB"""

async def _handle_user_logged_in(self, data: Dict, metadata: Dict):
    """Update last_login info in MongoDB"""
```

**Queue Configuration**:
- Exchange: `auth.events`
- Queue: `auth.read_model_updater`
- Routing Keys: `user.*`, `role.*`
- Durable: Yes (survives RabbitMQ restart)

---

## 🚀 How It Works

### Write Flow (Commands)

1. **User Action**: Admin creates a new user via API
2. **Endpoint**: `POST /api/v1/users`
3. **Service Layer**: `UserService.create_user()`
4. **Write Repository**: `UserRepository.create()` writes to MySQL
5. **Event Publishing**: Publishes `user.created` event to RabbitMQ
6. **Response**: Returns created user to client

### Read Flow (Queries)

1. **User Action**: User requests list of users via API
2. **Endpoint**: `GET /api/v1/users`
3. **Service Layer**: `UserService.get_users()`
4. **Read Repository**: `UserReadRepository.find_all()` queries MongoDB
5. **Response**: Fast response with denormalized data

### Event Processing

1. **Event Published**: RabbitMQ receives `user.created` event
2. **Consumer Listening**: `UserEventConsumer` receives event
3. **Handler**: Calls `_handle_user_created()`
4. **MongoDB Update**: Inserts/updates user in MongoDB
5. **Acknowledgement**: Event marked as processed

---

## 💡 Benefits

### 1. Performance
- **Fast Reads**: MongoDB optimized for queries with indexes
- **Scalability**: Read and write databases can scale independently
- **Reduced Load**: MySQL only handles writes, MongoDB handles reads

### 2. Flexibility
- **Denormalization**: MongoDB can store pre-joined data for complex queries
- **Custom Indexes**: Create indexes specific to query patterns
- **Aggregations**: Use MongoDB aggregation pipeline for analytics

### 3. Reliability
- **Event Sourcing**: Full audit trail of all changes
- **Eventual Consistency**: Read model eventually consistent with write model
- **Fault Tolerance**: Events stored in RabbitMQ (durable queue)

### 4. Maintainability
- **Separation of Concerns**: Clear separation between writes and reads
- **Independent Evolution**: Read and write models can evolve independently
- **Easy Testing**: Test commands and queries separately

---

## 📊 Data Flow Example

### Creating a User

```
1. POST /api/v1/users
   Body: {"email": "user@example.com", "full_name": "John Doe"}

2. AuthService.create_user()
   ↓
3. UserRepository.create(user) → MySQL
   INSERT INTO auth_db.users ...
   ↓
4. UserEvents.user_created(user_data) → RabbitMQ
   Publish: {event_type: "user.created", data: {...}}
   ↓
5. Response: 201 Created
   {"id": 1, "email": "user@example.com", ...}

[Background Process]
6. UserEventConsumer receives event
   ↓
7. UserReadRepository.upsert_user(user_data) → MongoDB
   db.users.updateOne({id: 1}, {$set: {...}}, {upsert: true})
   ↓
8. MongoDB updated (read model now has user)
```

### Querying Users

```
1. GET /api/v1/users?is_active=true

2. UserService.get_active_users()
   ↓
3. UserReadRepository.get_active_users() → MongoDB
   db.users.find({is_active: true}).limit(100)
   ↓
4. Response: 200 OK (< 10ms)
   [{"id": 1, "email": "user@example.com", ...}, ...]
```

---

## ⚙️ Configuration

### Environment Variables

```env
# MySQL (Write Database)
DATABASE_HOST=mysql
DATABASE_PORT=3306
DATABASE_USER=officework_dbu
DATABASE_NAME=auth_db

# MongoDB (Read Database)
MONGODB_URL=mongodb://admin:secret123@mongodb:27017/
MONGODB_DB_NAME=auth_read_db

# RabbitMQ (Event Bus)
RABBITMQ_URL=amqp://guest:guest@rabbitmq:5672/
```

### MongoDB Collections

- `users` - User read model
- `roles` - Role read model (future)

---

## 🧪 Testing CQRS

### Test Write Operations

```bash
# Create user (should publish event)
curl -X POST http://localhost:8088/api/v1/users \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer TOKEN" \
  -d '{"email":"test@example.com","full_name":"Test User","password":"Test123"}'
```

### Test Read Operations

```bash
# Query users from MongoDB
curl -X GET http://localhost:8088/api/v1/users \
  -H "Authorization: Bearer TOKEN"

# Search users (uses MongoDB text index)
curl -X GET "http://localhost:8088/api/v1/users?search=test" \
  -H "Authorization: Bearer TOKEN"
```

### Verify Event Publishing

```bash
# Check RabbitMQ management UI
http://localhost:15672

# Login: guest/guest
# Check exchange: auth.events
# Check queue: auth.read_model_updater
```

### Verify MongoDB Data

```bash
# Connect to MongoDB
docker exec -it mongodb mongosh

use auth_read_db
db.users.find().pretty()
db.users.countDocuments()
```

---

## 🔧 Troubleshooting

### Events Not Being Consumed

**Symptom**: MySQL updated but MongoDB not updated

**Check**:
```bash
# Check consumer logs
docker compose logs -f auth-api | grep "Event"

# Check RabbitMQ queue
# Should see messages in auth.read_model_updater queue
```

**Solution**:
- Verify RabbitMQ connection in logs
- Check consumer is initialized: Look for "✅ Event consumer initialized"
- Restart service: `docker compose restart auth-api`

### MongoDB Not Updating

**Symptom**: Events consumed but MongoDB unchanged

**Check**:
```bash
# Check MongoDB connection
docker compose logs -f auth-api | grep "MongoDB"

# Check indexes
docker exec -it mongodb mongosh
use auth_read_db
db.users.getIndexes()
```

**Solution**:
- Verify MongoDB connection string
- Check user_event_consumer logs for errors
- Manually trigger index creation: Restart service

### Eventual Consistency Delay

**Symptom**: User created but not immediately in search results

**Explanation**: This is expected behavior with CQRS
- Write returns immediately
- Event processing takes ~100-500ms
- Read model eventually consistent

**Solution**:
- For critical flows, poll or wait briefly
- Use write model (MySQL) for immediate consistency needs
- Implement read-your-writes pattern if needed

---

## 🚦 Current Status

### Implemented ✅
- [x] Write repositories with event publishing
- [x] Read repositories for MongoDB
- [x] Domain events (UserEvents, RoleEvents)
- [x] Event consumer for user events
- [x] RabbitMQ integration
- [x] MongoDB indexes
- [x] Background consumer task
- [x] Error handling and logging

### Pending ⏸️
- [ ] Update endpoints to use read repositories for queries
- [ ] Implement RoleReadRepository
- [ ] Add event replay mechanism (for rebuilding read model)
- [ ] Add dead letter queue for failed events
- [ ] Implement circuit breaker for event publishing
- [ ] Add metrics and monitoring

---

## 📚 Related Files

- **Write Repos**: [app/repositories/user_repository.py](app/repositories/user_repository.py)
- **Read Repos**: [app/repositories/user_read_repository.py](app/repositories/user_read_repository.py)
- **Events**: [app/core/events.py](app/core/events.py)
- **Consumer**: [app/consumers/user_event_consumer.py](app/consumers/user_event_consumer.py)
- **Main App**: [app/main.py](app/main.py)
- **RabbitMQ**: [app/core/rabbitmq.py](app/core/rabbitmq.py)
- **MongoDB**: [app/core/mongo_db.py](app/core/mongo_db.py)

---

## 📖 References

- [CQRS Pattern](https://martinfowler.com/bliki/CQRS.html) - Martin Fowler
- [Event-Driven Architecture](https://aws.amazon.com/event-driven-architecture/)
- [System Architecture Doc](../../docs/03.%20System_Architecture.md)
- [CLAUDE.md](../../CLAUDE.md) - Section 8: Design Patterns

---

**Version**: 1.0
**Author**: Generated by Claude AI
**Last Updated**: 2025-10-21
