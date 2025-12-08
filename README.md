# Clean Code Cookbook: Zero to Hero

**Build production-grade microservices with Python AsyncIO + Go concurrency, connected via gRPC.**

## What You'll Learn

This repository teaches you to architect scalable, maintainable systems using:
- **Python**: Hexagonal architecture with AsyncIO for I/O-bound services
- **Go**: High-performance worker pools for CPU-bound services  
- **gRPC**: Polyglot communication between services
- **Clean Architecture**: Testable, swappable, production-ready patterns

## Learning Path

### 🎯 Start Here: Choose Your Track

**Track 1: Python Developer** → Learn async hexagonal architecture  
**Track 2: Go Developer** → Learn concurrent systems design  
**Track 3: Full Stack** → Master both + gRPC integration

---

## Track 1: Python Modernization (Async Hexagonal Architecture)

### Step 1: Understand the Problem (5 min)
**Read:** [Why Hexagonal Architecture?](./clean_python/docs/README.md)

**The Challenge:** Traditional Python services mix business logic with databases, making them:
- Hard to test (need real database)
- Hard to change (swap SQL → MongoDB breaks everything)
- Slow (blocking I/O)

**The Solution:** Hexagonal architecture + AsyncIO

### Step 2: See the Structure (10 min)
```
clean_python/
├── src/
│   ├── domain/          # Pure business logic (no dependencies)
│   │   ├── models.py    # User entity with validation
│   │   └── ports.py     # Interfaces (what we need, not how)
│   ├── adapters/        # Infrastructure implementations
│   │   └── orm.py       # SQLAlchemy adapter (swappable!)
│   ├── service_layer/   # Use case orchestration
│   │   ├── handlers.py  # register_user_service()
│   │   └── unit_of_work.py  # Transaction management
│   └── entrypoints/     # External interfaces
│       ├── api.py       # FastAPI endpoints
│       └── deps.py      # Dependency injection
└── tests/               # All layers tested independently
```

**Key Insight:** Dependencies point INWARD. Domain knows nothing about databases or APIs.

### Step 3: Read the Code (30 min)

**Start here in order:**

1. **[domain/models.py](./clean_python/src/domain/models.py)** - Pure business logic
   ```python
   class User(BaseModel):
       username: str
       email: str
       
       def can_receive_email(self) -> bool:
           return self.is_active  # Business rule
   ```

2. **[domain/ports.py](./clean_python/src/domain/ports.py)** - What we need (interface)
   ```python
   class UserRepository(Protocol):
       async def add(self, user: User) -> None: ...
       async def get_by_email(self, email: str) -> Optional[User]: ...
   ```

3. **[adapters/orm.py](./clean_python/src/adapters/orm.py)** - How we do it (SQLAlchemy)
   - Implements `UserRepository` protocol
   - Translates domain ↔ database
   - **Swappable**: Replace with MongoDB adapter without touching domain

4. **[service_layer/unit_of_work.py](./clean_python/src/service_layer/unit_of_work.py)** - Transaction safety
   ```python
   async with uow:
       await uow.users.add(user)
       await uow.commit()  # Atomic: all or nothing
   ```

5. **[service_layer/handlers.py](./clean_python/src/service_layer/handlers.py)** - Use cases
   ```python
   async def register_user_service(username, email, uow):
       async with uow:
           existing = await uow.users.get_by_email(email)  # Async I/O
           if existing:
               raise ValueError("User exists")
           user = User(username=username, email=email)
           await uow.users.add(user)
           await uow.commit()
           return user
   ```

6. **[entrypoints/api.py](./clean_python/src/entrypoints/api.py)** - HTTP interface
   ```python
   @app.post("/users")
   async def create_user(data: RegisterRequest, uow = Depends(get_uow)):
       return await handlers.register_user_service(data.username, data.email, uow)
   ```

### Step 4: Run the Tests (10 min)

```bash
cd clean_python
pip install -e .
pytest tests/ -v
```

**Notice:** Tests use in-memory SQLite. No Docker, no setup. That's the power of hexagonal architecture.

### Step 5: Understand Async (15 min)

**Read:** [01_async_concepts/python.md](./01_async_concepts/python.md)

**Key Concepts:**
- `async def` = function that can pause
- `await` = pause here until I/O completes
- Event loop handles thousands of concurrent requests

**Why it matters:**
```python
# Blocking (handles 1 request at a time)
def get_user(email):
    return db.query(email)  # Waits 50ms, blocks thread

# Async (handles 1000s of requests concurrently)
async def get_user(email):
    return await db.query(email)  # Pauses, lets other requests run
```

### Step 6: Swap the Adapter (Exercise - 30 min)

**Challenge:** Replace SQLAlchemy with MongoDB without touching domain/service layers.

**Steps:**
1. Create `adapters/mongodb.py`
2. Implement `UserRepository` protocol
3. Update `deps.py` to use MongoDB adapter
4. Run tests - they should still pass!

**Solution:** [See example in docs](./clean_python/docs/README.md#swapping-adapters)

### Step 7: Add a Feature (Exercise - 45 min)

**Challenge:** Add "deactivate user" functionality.

**Requirements:**
1. Add `deactivate()` method to User model
2. Add `get_by_id()` to UserRepository port
3. Implement in SQLAlchemy adapter
4. Create `deactivate_user_service()` handler
5. Add `/users/{id}/deactivate` endpoint
6. Write tests

**This teaches you:** How to extend the architecture properly.

---

## Track 2: Go Systems Programming (High-Performance Backend)

### Step 1: Understand Go's Strengths (5 min)

**Read:** [01_async_concepts/go.md](./01_async_concepts/go.md)

**Go excels at:**
- CPU-bound work (image processing, data transformation)
- High-throughput services (10K+ req/sec)
- Concurrent processing (goroutines are cheap)

**Python excels at:**
- I/O-bound work (database queries, API calls)
- Rapid development (less boilerplate)
- ML/AI integration (NumPy, TensorFlow)

### Step 2: See the Structure (10 min)

```
go_track/clean_go_system/
├── cmd/server/          # Application entry point
│   └── main.go
├── internal/
│   ├── domain/          # Business entities
│   │   └── product.go
│   ├── core/            # Use cases
│   │   └── service.go
│   └── adapter/         # Infrastructure
│       ├── repository.go
│       └── http.go
└── pkg/                 # Shared utilities
    └── logger/
```

### Step 3: Read the Code (30 min)

**Start here:**

1. **[internal/domain/product.go](./go_track/clean_go_system/internal/domain/product.go)** - Entities
2. **[internal/core/service.go](./go_track/clean_go_system/internal/core/service.go)** - Business logic
3. **[internal/adapter/repository.go](./go_track/clean_go_system/internal/adapter/repository.go)** - Data access
4. **[cmd/server/main.go](./go_track/clean_go_system/cmd/server/main.go)** - Wiring

### Step 4: Understand Goroutines (15 min)

**Read:** [03_language_specific_guidelines/go/concurrency.md](./03_language_specific_guidelines/go/concurrency.md)

**Key Pattern: Worker Pool**
```go
// Process 1000 items concurrently with 10 workers
jobs := make(chan Item, 1000)
results := make(chan Result, 1000)

for w := 0; w < 10; w++ {
    go worker(jobs, results)  // Goroutine = lightweight thread
}

for _, item := range items {
    jobs <- item  // Send to worker pool
}
```

### Step 5: Run the Service (10 min)

```bash
cd go_track/clean_go_system
go run cmd/server/main.go
```

### Step 6: Add Concurrency (Exercise - 45 min)

**Challenge:** Add batch processing endpoint that processes 1000 items concurrently.

**Requirements:**
1. Create worker pool (10 workers)
2. Process items in parallel
3. Collect results
4. Return aggregated response

---

## Track 3: Polyglot Architecture (Python + Go via gRPC)

### Step 1: Understand the Use Case (5 min)

**Read:** [04_polyglot_architecture/README.md](./04_polyglot_architecture/README.md)

**Scenario:** E-commerce platform
- **Python service**: User management (I/O-bound, database-heavy)
- **Go service**: Product recommendations (CPU-bound, ML inference)
- **Communication**: gRPC (fast, type-safe, bidirectional)

### Step 2: Define the Contract (10 min)

**[proto/user_bridge.proto](./proto/user_bridge.proto)**
```protobuf
service UserService {
  rpc GetUser(GetUserRequest) returns (UserResponse);
}

message GetUserRequest {
  string user_id = 1;
}

message UserResponse {
  string user_id = 1;
  string email = 2;
  bool is_active = 3;
}
```

**Key Insight:** Proto file is the contract. Both services generate code from it.

### Step 3: Generate Code (5 min)

```bash
# Python
python -m grpc_tools.protoc -I./proto --python_out=. --grpc_python_out=. proto/user_bridge.proto

# Go
protoc --go_out=. --go-grpc_out=. proto/user_bridge.proto
```

### Step 4: Implement Services (30 min)

**Python (Server):**
```python
class UserServicer(user_bridge_pb2_grpc.UserServiceServicer):
    async def GetUser(self, request, context):
        user = await get_user_from_db(request.user_id)
        return user_bridge_pb2.UserResponse(
            user_id=user.id,
            email=user.email,
            is_active=user.is_active
        )
```

**Go (Client):**
```go
conn, _ := grpc.Dial("localhost:50051")
client := pb.NewUserServiceClient(conn)
resp, _ := client.GetUser(ctx, &pb.GetUserRequest{UserId: "123"})
```

### Step 5: Run the System (10 min)

```bash
# Terminal 1: Python service
cd python/services/catalog
python app.py

# Terminal 2: Go service
cd go/services/catalog
go run cmd/server/main.go

# Terminal 3: Test
grpcurl -plaintext localhost:50051 list
```

---

## Architecture Patterns Reference

### Hexagonal Architecture (Ports & Adapters)

**Problem:** Tightly coupled code
```python
# BAD: Business logic mixed with database
def register_user(username, email):
    conn = psycopg2.connect("postgresql://...")  # Coupled to PostgreSQL
    cursor = conn.cursor()
    cursor.execute("INSERT INTO users...")  # Can't test without DB
```

**Solution:** Separate concerns
```python
# GOOD: Business logic pure, adapter swappable
async def register_user_service(username, email, uow: AbstractUnitOfWork):
    async with uow:  # Works with ANY database
        user = User(username=username, email=email)  # Pure domain logic
        await uow.users.add(user)  # Port (interface)
        await uow.commit()
```

**Benefits:**
- ✅ Test without database (use fake adapter)
- ✅ Swap PostgreSQL → MongoDB (change adapter only)
- ✅ Business logic stays pure

### Unit of Work Pattern

**Problem:** Scattered transactions
```python
# BAD: Manual transaction management everywhere
def transfer_money(from_id, to_id, amount):
    conn.begin()
    try:
        deduct(from_id, amount)
        add(to_id, amount)
        conn.commit()
    except:
        conn.rollback()  # Easy to forget!
```

**Solution:** Centralized transaction boundary
```python
# GOOD: Automatic transaction management
async def transfer_money(from_id, to_id, amount, uow):
    async with uow:  # Auto-rollback on exception
        await uow.accounts.deduct(from_id, amount)
        await uow.accounts.add(to_id, amount)
        await uow.commit()  # Atomic
```

### Repository Pattern

**Problem:** SQL scattered everywhere
```python
# BAD: SQL in business logic
def get_active_users():
    return db.execute("SELECT * FROM users WHERE is_active = true")
```

**Solution:** Encapsulate data access
```python
# GOOD: Repository hides implementation
class UserRepository:
    async def get_active_users(self) -> List[User]:
        # Implementation hidden, can change anytime
        pass
```

---

## Testing Strategy

### Layer-by-Layer Testing

**1. Domain Layer (Pure Logic)**
```python
def test_user_validation():
    with pytest.raises(ValueError):
        User(username="invalid@name", email="test@example.com")
```
No database, no API, just pure logic.

**2. Adapter Layer (Integration)**
```python
async def test_sqlalchemy_repository():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    # Test actual database operations
```

**3. Service Layer (Use Cases)**
```python
async def test_register_user_service():
    uow = SqlAlchemyUnitOfWork(session_factory)
    user = await register_user_service("test", "test@example.com", uow)
    assert user.username == "test"
```

**4. API Layer (End-to-End)**
```python
async def test_create_user_endpoint():
    response = await client.post("/users", json={"username": "test", "email": "test@example.com"})
    assert response.status_code == 201
```

---

## Common Patterns

### Dependency Injection
```python
# BAD: Hard-coded dependency
class UserService:
    def __init__(self):
        self.repo = SqlAlchemyUserRepository()  # Can't swap

# GOOD: Injected dependency
class UserService:
    def __init__(self, repo: UserRepository):  # Any implementation
        self.repo = repo
```

### Async Context Managers
```python
async with uow:  # __aenter__
    await uow.users.add(user)
    await uow.commit()
# __aexit__ (auto-cleanup, even on exception)
```

### Protocol-Based Interfaces (Python)
```python
class UserRepository(Protocol):  # No inheritance needed
    async def add(self, user: User) -> None: ...

class SqlAlchemyUserRepository:  # Implicitly implements protocol
    async def add(self, user: User) -> None:
        self.session.add(user)
```

---

## Next Steps

### Beginner → Intermediate
1. ✅ Complete Track 1 (Python) or Track 2 (Go)
2. ✅ Build a simple CRUD service
3. ✅ Write tests for all layers
4. ✅ Swap one adapter (SQL → MongoDB)

### Intermediate → Advanced
1. ✅ Complete Track 3 (Polyglot)
2. ✅ Add observability (logging, metrics, tracing)
3. ✅ Implement CI/CD pipeline
4. ✅ Deploy to production (Docker + Kubernetes)

### Advanced → Expert
1. ✅ Design multi-service architecture
2. ✅ Implement event-driven patterns
3. ✅ Add caching layer (Redis)
4. ✅ Optimize for 10K+ req/sec

---

## Resources

### Documentation
- [Architecture Blueprint](./02_architecture_blueprint/README.md)
- [Python Guidelines](./03_language_specific_guidelines/python/README.md)
- [Go Guidelines](./03_language_specific_guidelines/go/README.md)
- [gRPC Integration](./04_polyglot_architecture/grpc.md)

### External Learning
- **Hexagonal Architecture**: [Alistair Cockburn's original article](https://alistair.cockburn.us/hexagonal-architecture/)
- **AsyncIO**: [Real Python AsyncIO Guide](https://realpython.com/async-io-python/)
- **Go Concurrency**: [Go by Example: Goroutines](https://gobyexample.com/goroutines)
- **gRPC**: [Official gRPC Tutorial](https://grpc.io/docs/languages/python/quickstart/)

---

## FAQ

**Q: Why hexagonal architecture? Isn't it over-engineering?**  
A: For small scripts, yes. For production services that need to scale, change, and be tested, it's essential.

**Q: When should I use Python vs Go?**  
A: Python for I/O-bound (databases, APIs), Go for CPU-bound (data processing, high throughput).

**Q: Do I need to use both Python and Go?**  
A: No. Start with one. Add the other when you have a specific performance need.

**Q: How do I know if my architecture is "clean"?**  
A: Can you swap the database without touching business logic? Can you test without external dependencies? If yes, it's clean.

**Q: What's the learning curve?**  
A: 1-2 weeks to understand concepts, 1-2 months to feel natural, 6 months to master.

---

## Contributing

See [CONTRIBUTING.md](./06_contribution_guidelines/CONTRIBUTING.md)

---

## License

MIT - Use this code to build amazing things.
