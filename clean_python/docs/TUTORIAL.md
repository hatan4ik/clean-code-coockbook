# Python Hexagonal Architecture: Complete Tutorial

**Time to complete:** 2-3 hours  
**Prerequisites:** Basic Python, async/await basics  
**Goal:** Build a production-ready user management service from scratch

---

## Part 1: Understanding the Problem (15 min)

### Traditional Approach (What NOT to do)

```python
# app.py - Everything mixed together
from flask import Flask, request
import psycopg2

app = Flask(__name__)

@app.route('/users', methods=['POST'])
def create_user():
    data = request.json
    
    # Validation mixed with HTTP
    if '@' not in data['email']:
        return {'error': 'Invalid email'}, 400
    
    # Database logic in endpoint
    conn = psycopg2.connect("postgresql://localhost/mydb")
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO users (username, email) VALUES (%s, %s)",
        (data['username'], data['email'])
    )
    conn.commit()
    conn.close()
    
    return {'status': 'created'}, 201
```

**Problems:**
1. ❌ Can't test without PostgreSQL running
2. ❌ Can't swap to MongoDB without rewriting everything
3. ❌ Business rules (email validation) mixed with HTTP
4. ❌ No transaction safety (what if commit fails?)
5. ❌ Blocking I/O (handles 1 request at a time)

### Hexagonal Approach (What we'll build)

```python
# Clean separation of concerns

# domain/models.py - Pure business logic
class User(BaseModel):
    email: str
    
    @field_validator('email')
    def validate_email(cls, v):
        if '@' not in v:
            raise ValueError('Invalid email')
        return v

# domain/ports.py - What we need (interface)
class UserRepository(Protocol):
    async def add(self, user: User) -> None: ...

# adapters/orm.py - How we do it (PostgreSQL)
class SqlAlchemyUserRepository(UserRepository):
    async def add(self, user: User) -> None:
        self.session.add(_to_record(user))

# service_layer/handlers.py - Use case
async def register_user(username, email, uow):
    async with uow:
        user = User(username=username, email=email)  # Validates
        await uow.users.add(user)
        await uow.commit()  # Atomic
        return user

# entrypoints/api.py - HTTP interface
@app.post('/users')
async def create_user(data: RegisterRequest, uow = Depends(get_uow)):
    return await register_user(data.username, data.email, uow)
```

**Benefits:**
1. ✅ Test domain logic without database
2. ✅ Swap PostgreSQL → MongoDB by changing adapter only
3. ✅ Business rules in domain layer
4. ✅ Transaction safety via UnitOfWork
5. ✅ Async I/O (handles 1000s of concurrent requests)

---

## Part 2: Building the Domain Layer (30 min)

### Step 1: Create the Project Structure

```bash
mkdir user_service && cd user_service
mkdir -p src/{domain,adapters,service_layer,entrypoints} tests
touch src/{domain,adapters,service_layer,entrypoints}/__init__.py
```

### Step 2: Define the Domain Model

**File: `src/domain/models.py`**

```python
import re
from uuid import UUID, uuid4
from datetime import datetime
from pydantic import BaseModel, Field, field_validator

class User(BaseModel):
    """
    Domain Entity: User
    
    Contains:
    - Data (id, username, email, etc.)
    - Business rules (validation, behavior)
    
    Does NOT contain:
    - Database logic
    - HTTP logic
    - External dependencies
    """
    id: UUID = Field(default_factory=uuid4)
    username: str
    email: str
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.now)

    @field_validator("username")
    @classmethod
    def validate_username(cls, v: str) -> str:
        """Business rule: Username must be alphanumeric."""
        if not re.match("^[a-zA-Z0-9_]+$", v):
            raise ValueError("Username must be alphanumeric")
        if len(v) < 3:
            raise ValueError("Username must be at least 3 characters")
        return v
    
    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        """Business rule: Email must be valid format."""
        if not re.match(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$", v):
            raise ValueError("Invalid email format")
        return v
    
    def deactivate(self) -> None:
        """Business behavior: Deactivate user account."""
        self.is_active = False
    
    def can_receive_email(self) -> bool:
        """Business rule: Only active users receive emails."""
        return self.is_active
```

**Test it:**

```python
# tests/test_domain_models.py
import pytest
from src.domain.models import User

def test_user_creation():
    user = User(username="john_doe", email="john@example.com")
    assert user.username == "john_doe"
    assert user.is_active is True

def test_invalid_username():
    with pytest.raises(ValueError, match="alphanumeric"):
        User(username="john@doe", email="john@example.com")

def test_invalid_email():
    with pytest.raises(ValueError, match="Invalid email"):
        User(username="john", email="not-an-email")

def test_deactivate():
    user = User(username="john", email="john@example.com")
    user.deactivate()
    assert user.is_active is False
    assert user.can_receive_email() is False
```

**Run:** `pytest tests/test_domain_models.py -v`

**Key Insight:** Domain tests need NO database, NO API, NO external dependencies. Pure logic.

### Step 3: Define the Port (Interface)

**File: `src/domain/ports.py`**

```python
from typing import Protocol, Optional
from uuid import UUID
from .models import User

class UserRepository(Protocol):
    """
    Port (Interface): What the domain needs.
    
    The domain says: "I need a way to save and retrieve users."
    The domain does NOT say: "Use PostgreSQL" or "Use MongoDB"
    
    Any adapter that implements these methods will work.
    """
    
    async def add(self, user: User) -> None:
        """Save a new user."""
        ...

    async def get_by_email(self, email: str) -> Optional[User]:
        """Find user by email."""
        ...
    
    async def get_by_id(self, user_id: UUID) -> Optional[User]:
        """Find user by ID."""
        ...
    
    async def update(self, user: User) -> None:
        """Update existing user."""
        ...
```

**Key Insight:** This is a Protocol (duck typing), not an abstract base class. Any class with these methods automatically implements the interface.

---

## Part 3: Building the Adapter Layer (30 min)

### Step 4: Implement SQLAlchemy Adapter

**File: `src/adapters/orm.py`**

```python
from datetime import datetime
from typing import Optional
from uuid import UUID
from sqlalchemy import Boolean, DateTime, String, select
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.models import User
from src.domain.ports import UserRepository


class Base(DeclarativeBase):
    """SQLAlchemy base for all ORM models."""
    pass


class UserRecord(Base):
    """
    Persistence Model: How we store users in the database.
    
    This is SEPARATE from the domain model.
    Why? Because database structure != business logic structure.
    """
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    username: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)


def _to_record(user: User) -> UserRecord:
    """Translate domain model → database record."""
    return UserRecord(
        id=str(user.id),
        username=user.username,
        email=user.email,
        is_active=user.is_active,
        created_at=user.created_at,
    )


def _to_domain(record: UserRecord) -> User:
    """Translate database record → domain model."""
    return User.model_validate({
        "id": record.id,
        "username": record.username,
        "email": record.email,
        "is_active": record.is_active,
        "created_at": record.created_at,
    })


class SqlAlchemyUserRepository(UserRepository):
    """
    Adapter: Implements UserRepository using SQLAlchemy.
    
    This is ONE way to implement the port.
    We could also have:
    - MongoDBUserRepository
    - InMemoryUserRepository (for testing)
    - RedisUserRepository
    
    All would implement the same interface.
    """
    
    def __init__(self, session: AsyncSession):
        self.session = session

    async def add(self, user: User) -> None:
        """Add user to session (does NOT commit)."""
        self.session.add(_to_record(user))

    async def get_by_email(self, email: str) -> Optional[User]:
        """Query user by email."""
        stmt = select(UserRecord).where(UserRecord.email == email)
        result = await self.session.execute(stmt)
        record = result.scalar_one_or_none()
        return _to_domain(record) if record else None
    
    async def get_by_id(self, user_id: UUID) -> Optional[User]:
        """Query user by ID."""
        stmt = select(UserRecord).where(UserRecord.id == str(user_id))
        result = await self.session.execute(stmt)
        record = result.scalar_one_or_none()
        return _to_domain(record) if record else None
    
    async def update(self, user: User) -> None:
        """Update existing user."""
        stmt = select(UserRecord).where(UserRecord.id == str(user.id))
        result = await self.session.execute(stmt)
        record = result.scalar_one_or_none()
        if record:
            record.username = user.username
            record.email = user.email
            record.is_active = user.is_active
```

**Test it:**

```python
# tests/test_adapters_repository.py
import pytest
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from src.domain.models import User
from src.adapters.orm import Base, SqlAlchemyUserRepository

@pytest.fixture
async def session():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    session_factory = async_sessionmaker(bind=engine, expire_on_commit=False)
    async with session_factory() as session:
        yield session

@pytest.mark.asyncio
async def test_add_and_get_user(session):
    repo = SqlAlchemyUserRepository(session)
    user = User(username="john", email="john@example.com")
    
    await repo.add(user)
    await session.commit()
    
    retrieved = await repo.get_by_email("john@example.com")
    assert retrieved is not None
    assert retrieved.username == "john"

@pytest.mark.asyncio
async def test_get_nonexistent_user(session):
    repo = SqlAlchemyUserRepository(session)
    user = await repo.get_by_email("nonexistent@example.com")
    assert user is None
```

**Key Insight:** We test the adapter with a REAL database (in-memory SQLite). This is an integration test.

---

## Part 4: Building the Service Layer (30 min)

### Step 5: Implement Unit of Work

**File: `src/service_layer/unit_of_work.py`**

```python
from typing import Protocol, Self, Callable
from sqlalchemy.ext.asyncio import AsyncSession
from src.adapters.orm import SqlAlchemyUserRepository

class AbstractUnitOfWork(Protocol):
    """
    Unit of Work: Manages the transaction boundary.
    
    Ensures:
    1. All operations succeed together (atomic)
    2. Or all operations fail together (rollback)
    3. Resources are always cleaned up
    """
    users: SqlAlchemyUserRepository

    async def __aenter__(self) -> Self: ...
    async def __aexit__(self, *args) -> None: ...
    async def commit(self) -> None: ...
    async def rollback(self) -> None: ...


class SqlAlchemyUnitOfWork:
    """
    Concrete implementation using SQLAlchemy.
    
    Usage:
        async with uow:
            await uow.users.add(user)
            await uow.commit()
        # Auto-cleanup happens here
    """
    
    def __init__(self, session_factory: Callable[[], AsyncSession]):
        self.session_factory = session_factory

    async def __aenter__(self) -> Self:
        """Start transaction."""
        self.session: AsyncSession = self.session_factory()
        self.users = SqlAlchemyUserRepository(self.session)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """
        End transaction.
        
        If exception occurred: rollback
        If no commit called: rollback (safety)
        Always: close session
        """
        try:
            if exc_type:
                await self.rollback()
            elif self.session.in_transaction():
                await self.rollback()  # Uncommitted transaction
        finally:
            await self.session.close()

    async def commit(self):
        """Commit all changes."""
        await self.session.commit()

    async def rollback(self):
        """Rollback all changes."""
        await self.session.rollback()
```

### Step 6: Implement Use Cases (Handlers)

**File: `src/service_layer/handlers.py`**

```python
from uuid import UUID
from src.domain.models import User
from src.service_layer.unit_of_work import AbstractUnitOfWork


async def register_user_service(
    username: str, 
    email: str, 
    uow: AbstractUnitOfWork
) -> User:
    """
    Use Case: Register a new user.
    
    Steps:
    1. Check if user already exists (async I/O)
    2. Create domain model (validates business rules)
    3. Save to database (async I/O)
    4. Commit transaction (atomic)
    
    Returns: Created user
    Raises: ValueError if user exists
    """
    async with uow:
        # Check constraint
        existing = await uow.users.get_by_email(email)
        if existing:
            raise ValueError(f"User with email {email} already exists")
        
        # Create domain entity (validates)
        user = User(username=username, email=email)
        
        # Persist
        await uow.users.add(user)
        await uow.commit()
        
        return user


async def deactivate_user_service(
    user_id: UUID,
    uow: AbstractUnitOfWork
) -> User:
    """
    Use Case: Deactivate a user account.
    
    Steps:
    1. Find user (async I/O)
    2. Call domain method (business logic)
    3. Update database (async I/O)
    4. Commit transaction (atomic)
    
    Returns: Updated user
    Raises: ValueError if user not found
    """
    async with uow:
        user = await uow.users.get_by_id(user_id)
        if not user:
            raise ValueError(f"User {user_id} not found")
        
        # Domain logic
        user.deactivate()
        
        # Persist
        await uow.users.update(user)
        await uow.commit()
        
        return user
```

**Test it:**

```python
# tests/test_service_layer.py
import pytest
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from src.domain.models import User
from src.service_layer import handlers
from src.service_layer.unit_of_work import SqlAlchemyUnitOfWork
from src.adapters.orm import Base

@pytest.fixture
async def uow():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    session_factory = async_sessionmaker(bind=engine, expire_on_commit=False)
    return SqlAlchemyUnitOfWork(session_factory)

@pytest.mark.asyncio
async def test_register_user_success(uow):
    user = await handlers.register_user_service("john", "john@example.com", uow)
    
    assert user.username == "john"
    assert user.email == "john@example.com"
    
    # Verify it was committed
    async with uow:
        retrieved = await uow.users.get_by_email("john@example.com")
        assert retrieved is not None

@pytest.mark.asyncio
async def test_register_duplicate_user(uow):
    await handlers.register_user_service("john", "john@example.com", uow)
    
    with pytest.raises(ValueError, match="already exists"):
        await handlers.register_user_service("jane", "john@example.com", uow)

@pytest.mark.asyncio
async def test_deactivate_user(uow):
    user = await handlers.register_user_service("john", "john@example.com", uow)
    
    deactivated = await handlers.deactivate_user_service(user.id, uow)
    
    assert deactivated.is_active is False
```

---

## Part 5: Building the API Layer (20 min)

### Step 7: Create FastAPI Endpoints

**File: `src/entrypoints/api.py`**

```python
from uuid import UUID
from fastapi import FastAPI, HTTPException, Depends, status
from pydantic import BaseModel

from src.service_layer import handlers
from src.service_layer.unit_of_work import AbstractUnitOfWork
from src.entrypoints.deps import get_uow

app = FastAPI(title="User Service")


# DTOs (Data Transfer Objects)
class RegisterRequest(BaseModel):
    username: str
    email: str


class UserResponse(BaseModel):
    user_id: str
    username: str
    email: str
    is_active: bool


@app.post("/users", status_code=status.HTTP_201_CREATED, response_model=UserResponse)
async def register_user(
    data: RegisterRequest,
    uow: AbstractUnitOfWork = Depends(get_uow)
):
    """Register a new user."""
    try:
        user = await handlers.register_user_service(
            username=data.username,
            email=data.email,
            uow=uow
        )
        return UserResponse(
            user_id=str(user.id),
            username=user.username,
            email=user.email,
            is_active=user.is_active
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


@app.post("/users/{user_id}/deactivate", response_model=UserResponse)
async def deactivate_user(
    user_id: UUID,
    uow: AbstractUnitOfWork = Depends(get_uow)
):
    """Deactivate a user account."""
    try:
        user = await handlers.deactivate_user_service(user_id, uow)
        return UserResponse(
            user_id=str(user.id),
            username=user.username,
            email=user.email,
            is_active=user.is_active
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}
```

**File: `src/entrypoints/deps.py`**

```python
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from src.config import settings
from src.service_layer.unit_of_work import SqlAlchemyUnitOfWork

# Create engine and session factory
engine = create_async_engine(settings.database_url, echo=settings.echo_sql)
session_factory = async_sessionmaker(bind=engine, expire_on_commit=False)


def get_uow() -> SqlAlchemyUnitOfWork:
    """Dependency injection: Provide UnitOfWork to endpoints."""
    return SqlAlchemyUnitOfWork(session_factory)
```

**File: `src/config.py`**

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str = "sqlite+aiosqlite:///./test.db"
    echo_sql: bool = False

settings = Settings()
```

---

## Part 6: Running and Testing (15 min)

### Step 8: Run the Service

```bash
# Install dependencies
pip install fastapi uvicorn sqlalchemy aiosqlite pydantic pydantic-settings

# Run server
uvicorn src.entrypoints.api:app --reload
```

### Step 9: Test the API

```bash
# Register user
curl -X POST http://localhost:8000/users \
  -H "Content-Type: application/json" \
  -d '{"username": "john_doe", "email": "john@example.com"}'

# Response: {"user_id": "...", "username": "john_doe", "email": "john@example.com", "is_active": true}

# Try duplicate (should fail)
curl -X POST http://localhost:8000/users \
  -H "Content-Type: application/json" \
  -d '{"username": "jane", "email": "john@example.com"}'

# Response: {"detail": "User with email john@example.com already exists"}

# Deactivate user
curl -X POST http://localhost:8000/users/{user_id}/deactivate

# Health check
curl http://localhost:8000/health
```

---

## Part 7: Swapping Adapters (Exercise - 30 min)

### Challenge: Replace SQLAlchemy with MongoDB

**Goal:** Prove the architecture is truly decoupled.

**Steps:**

1. **Install MongoDB driver:**
```bash
pip install motor  # Async MongoDB driver
```

2. **Create MongoDB adapter:**

**File: `src/adapters/mongodb.py`**

```python
from typing import Optional
from uuid import UUID
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorCollection
from src.domain.models import User
from src.domain.ports import UserRepository


class MongoDBUserRepository(UserRepository):
    """MongoDB implementation of UserRepository."""
    
    def __init__(self, collection: AsyncIOMotorCollection):
        self.collection = collection

    async def add(self, user: User) -> None:
        await self.collection.insert_one({
            "_id": str(user.id),
            "username": user.username,
            "email": user.email,
            "is_active": user.is_active,
            "created_at": user.created_at.isoformat()
        })

    async def get_by_email(self, email: str) -> Optional[User]:
        doc = await self.collection.find_one({"email": email})
        if not doc:
            return None
        return User.model_validate({
            "id": doc["_id"],
            "username": doc["username"],
            "email": doc["email"],
            "is_active": doc["is_active"],
            "created_at": doc["created_at"]
        })
    
    async def get_by_id(self, user_id: UUID) -> Optional[User]:
        doc = await self.collection.find_one({"_id": str(user_id)})
        if not doc:
            return None
        return User.model_validate({
            "id": doc["_id"],
            "username": doc["username"],
            "email": doc["email"],
            "is_active": doc["is_active"],
            "created_at": doc["created_at"]
        })
    
    async def update(self, user: User) -> None:
        await self.collection.update_one(
            {"_id": str(user.id)},
            {"$set": {
                "username": user.username,
                "email": user.email,
                "is_active": user.is_active
            }}
        )
```

3. **Create MongoDB Unit of Work:**

**File: `src/service_layer/mongodb_uow.py`**

```python
from typing import Self
from motor.motor_asyncio import AsyncIOMotorClient
from src.adapters.mongodb import MongoDBUserRepository


class MongoDBUnitOfWork:
    def __init__(self, mongo_url: str, db_name: str):
        self.client = AsyncIOMotorClient(mongo_url)
        self.db = self.client[db_name]

    async def __aenter__(self) -> Self:
        self.users = MongoDBUserRepository(self.db.users)
        return self

    async def __aexit__(self, *args):
        pass  # MongoDB doesn't need explicit cleanup

    async def commit(self):
        pass  # MongoDB commits automatically

    async def rollback(self):
        pass  # Would need transactions for multi-document operations
```

4. **Update deps.py:**

```python
from src.service_layer.mongodb_uow import MongoDBUnitOfWork

def get_uow() -> MongoDBUnitOfWork:
    return MongoDBUnitOfWork("mongodb://localhost:27017", "user_service")
```

5. **Run tests:**

```bash
pytest tests/test_service_layer.py -v
```

**Result:** All tests pass! Domain and service layers unchanged.

---

## Summary: What You've Learned

### Architecture Layers

1. **Domain** - Pure business logic, no dependencies
2. **Ports** - Interfaces (what we need)
3. **Adapters** - Implementations (how we do it)
4. **Service Layer** - Use case orchestration
5. **Entrypoints** - External interfaces (HTTP, CLI, etc.)

### Key Patterns

- **Hexagonal Architecture** - Dependencies point inward
- **Repository Pattern** - Encapsulate data access
- **Unit of Work** - Manage transactions
- **Dependency Injection** - Provide implementations at runtime
- **Async/Await** - Non-blocking I/O for concurrency

### Testing Strategy

- **Domain** - Pure logic, no external dependencies
- **Adapters** - Integration tests with real infrastructure
- **Service Layer** - Use case tests with real UoW
- **API** - End-to-end tests with test client

### Benefits Achieved

✅ Testable without external dependencies  
✅ Swappable infrastructure (SQL ↔ MongoDB)  
✅ Clear separation of concerns  
✅ Transaction safety  
✅ High concurrency via async  
✅ Production-ready architecture

---

## Next Steps

1. **Add more features:** List users, update user, delete user
2. **Add authentication:** JWT tokens, password hashing
3. **Add caching:** Redis adapter for frequently accessed users
4. **Add events:** Publish "UserRegistered" event to message queue
5. **Add observability:** Logging, metrics, tracing
6. **Deploy:** Docker, Kubernetes, CI/CD

**You're now ready to build production-grade Python microservices!**
