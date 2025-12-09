# Quick Start Guide (15 Minutes)

Get the repo running and understand the architecture in 15 minutes.

## 1. Clone and Setup (2 min)

```bash
git clone <repo-url>
cd clean-code-coockbook

# Python setup
cd clean_python
pip install -e .
pip install pytest pytest-asyncio

# Go setup (optional)
cd ../go_track/clean_go_system
go mod download
```

## 2. Run Python Tests (2 min)

```bash
cd clean_python
pytest tests/ -v
```

**Expected output:**
```
tests/test_domain_models.py::test_user_creation PASSED
tests/test_adapters_repository.py::test_add_user PASSED
tests/test_service_layer.py::test_register_user_service_happy_path PASSED
```

**What just happened?**
- Domain tests ran WITHOUT database
- Adapter tests used in-memory SQLite
- Service tests verified full use case flow

## 3. Understand the Flow (5 min)

**Trace a request:** User registration

```
HTTP POST /users
    ↓
entrypoints/api.py
    ↓ calls
service_layer/handlers.py::register_user_service()
    ↓ uses
service_layer/unit_of_work.py (transaction boundary)
    ↓ calls
domain/ports.py::UserRepository (interface)
    ↓ implemented by
adapters/orm.py::SqlAlchemyUserRepository
    ↓ writes to
Database
```

**Key files to read (in order):**

1. `src/domain/models.py` (30 lines) - Business logic
2. `src/domain/ports.py` (10 lines) - Interface
3. `src/service_layer/handlers.py` (20 lines) - Use case
4. `src/entrypoints/api.py` (30 lines) - HTTP endpoint

**Total:** ~90 lines to understand the entire flow.

**Extra async hex example:** Try `pytest tests/test_async_hex_example.py -v` and browse `src/async_hex_example/` for a lightweight project service with an in-memory unit of work.

## 4. Run the API (3 min)

```bash
cd clean_python
uvicorn src.entrypoints.api:app --reload
```

**Test it:**
```bash
# Register user
curl -X POST http://localhost:8000/users \
  -H "Content-Type: application/json" \
  -d '{"username": "test_user", "email": "test@example.com"}'

# Expected: {"user_id": "...", "status": "active"}

# Try duplicate (should fail)
curl -X POST http://localhost:8000/users \
  -H "Content-Type: application/json" \
  -d '{"username": "another", "email": "test@example.com"}'

# Expected: {"detail": "User test@example.com already exists"}
```

## 5. Understand the Architecture (3 min)

### Hexagonal Architecture Diagram

```
┌─────────────────────────────────────────────────────────┐
│                    ENTRYPOINTS                          │
│  (HTTP, CLI, gRPC - External World)                     │
│                                                          │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐             │
│  │ FastAPI  │  │   CLI    │  │  gRPC    │             │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘             │
└───────┼─────────────┼─────────────┼────────────────────┘
        │             │             │
        └─────────────┴─────────────┘
                      │
┌─────────────────────┼─────────────────────────────────┐
│              SERVICE LAYER                             │
│  (Use Cases - Application Logic)                       │
│                     │                                  │
│  ┌──────────────────▼──────────────────┐              │
│  │  register_user_service()            │              │
│  │  deactivate_user_service()          │              │
│  └──────────────────┬──────────────────┘              │
└────────────────────┼────────────────────────────────────┘
                     │
                     │ uses
                     │
┌────────────────────▼────────────────────────────────────┐
│                 DOMAIN LAYER                            │
│  (Business Logic - Pure, No Dependencies)               │
│                                                          │
│  ┌─────────────┐         ┌──────────────────┐          │
│  │   Models    │         │      Ports       │          │
│  │             │         │  (Interfaces)    │          │
│  │  User       │         │  UserRepository  │          │
│  │  - validate │         │  - add()         │          │
│  │  - deactivate│        │  - get_by_email()│          │
│  └─────────────┘         └──────────────────┘          │
└─────────────────────────────────┬───────────────────────┘
                                  │
                                  │ implemented by
                                  │
┌─────────────────────────────────▼───────────────────────┐
│                    ADAPTERS                             │
│  (Infrastructure - Swappable Implementations)           │
│                                                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │ SQLAlchemy   │  │   MongoDB    │  │  InMemory    │ │
│  │ Repository   │  │  Repository  │  │  Repository  │ │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘ │
└─────────┼──────────────────┼──────────────────┼─────────┘
          │                  │                  │
          ▼                  ▼                  ▼
    PostgreSQL           MongoDB          RAM (tests)
```

### Key Principles

**1. Dependency Rule:** Dependencies point INWARD
- Domain depends on NOTHING
- Service layer depends on domain
- Adapters depend on domain
- Entrypoints depend on service layer

**2. Ports & Adapters:**
- **Port** = Interface (what we need)
- **Adapter** = Implementation (how we do it)
- Swap adapters without touching domain

**3. Async All The Way:**
- Every I/O operation is `async`
- Handles 1000s of concurrent requests
- Single service, massive throughput

## 6. Next Steps

**Beginner:**
- Read [README.md](./README.md) for full learning path
- Complete [Python Tutorial](./clean_python/docs/TUTORIAL.md)

**Intermediate:**
- Add a new feature (update user, list users)
- Swap SQLAlchemy → MongoDB adapter
- Add caching layer (Redis)

**Advanced:**
- Explore Go service (`go_track/clean_go_system/`)
- Connect Python + Go via gRPC
- Deploy to production

## Common Questions

**Q: Why so many layers?**  
A: Each layer has ONE responsibility. Easy to test, easy to change.

**Q: Isn't this over-engineering?**  
A: For a 100-line script, yes. For a production service that needs to scale and evolve, no.

**Q: Can I use this in production?**  
A: Yes! This is production-grade architecture used by major companies.

**Q: What if I only know Python?**  
A: Perfect! Start with Track 1 (Python). Ignore Go for now.

**Q: What if I only know Go?**  
A: Start with Track 2 (Go). Ignore Python for now.

**Q: How long to learn this?**  
A: 2-3 hours for basics, 1-2 weeks to feel comfortable, 1-2 months to master.

---

**Ready to dive deeper?** → [Full README](./README.md)
