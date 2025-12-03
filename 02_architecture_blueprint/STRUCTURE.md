# Module 2: The Hexagonal Blueprint
## The Anatomy of a Scalable Python/Go System

This module defines the reference architecture for all cookbook examples. The goal: isolate pure domain logic, keep I/O behind ports, and make services testable and replaceable.

### 1. Directory Templates

#### Python (FastAPI/asyncio)
```
python/services/catalog/
├── app.py                     # FastAPI wiring (DI, routes, middlewares)
├── config.py                  # Pydantic settings
├── domain/
│   ├── models.py              # Entities/value objects (dataclasses/pydantic)
│   ├── events.py              # Domain events
│   └── services.py            # Pure orchestrators, no I/O
├── adapters/
│   ├── repositories.py        # Postgres/Redis implementations
│   ├── messaging.py           # Kafka/NATS producers
│   └── http_clients.py        # Async HTTP clients to upstreams
├── ports/
│   ├── repository.py          # Protocols/ABCs
│   └── notifier.py
├── service_layer/
│   ├── unit_of_work.py        # Transaction boundaries
│   └── handlers.py            # Command/query handlers
└── tests/
    ├── unit/
    ├── integration/
    └── e2e/
```

#### Go (Chi/Gin or net/http)
```
go/services/catalog/
├── cmd/catalog/main.go        # Wire HTTP server and dependencies
├── internal/app/              # Use cases; orchestrates domain and ports
├── internal/domain/           # Entities, value objects, domain services
├── internal/ports/            # Interfaces for repositories, publishers, clients
├── internal/adapters/         # Postgres, Redis, Kafka, HTTP clients
├── internal/platform/         # Logging, config, middleware, health
└── internal/tests/            # Unit, integration, contract
```

### 2. Request Lifecycle (example: GET /products/{id})
1) Transport layer validates inputs and creates a request context (trace/span IDs, timeouts).
2) Application handler calls a use case (`FetchProduct`) that orchestrates domain logic.
3) Use case talks to ports (`ProductRepository`, `InventoryClient`, `MessageBus`) provided via DI.
4) Adapters implement ports; they map errors to domain errors and handle retries/idempotency.
5) Response DTOs are serialized; metrics and traces are emitted; deadlines respected.

### 3. Key Patterns
- **Ports and Adapters:** Interfaces live close to consumers; adapters register via constructors/factories.
- **Unit of Work:** Wrap DB operations in a transaction; emit domain events; publish via outbox.
- **DTOs vs Domain:** Keep domain models free from framework types. Map at the edges.
- **Configuration:** 12‑factor, environment driven; validate at startup; secrets from env/SM.
- **Validation:** Input validation at transport layer; business invariants in domain; database constraints enforce last line of defense.
- **Error Model:** Typed errors with HTTP mapping; avoid panics/exceptions crossing layers; include correlation IDs.

### 4. Sample Flow (Python)
```python
# service_layer/handlers.py
async def fetch_product(cmd: FetchProduct, uow: UnitOfWork) -> ProductDTO:
    async with uow:
        product = await uow.products.get(cmd.product_id)
        inv, price = await asyncio.gather(
            uow.inventory.get(cmd.product_id),
            uow.pricing.get(cmd.product_id),
        )
        product.inventory = inv
        product.price = price
        return ProductDTO.from_domain(product)
```

### 5. Sample Flow (Go)
```go
// internal/app/fetch_product.go
func (s Service) FetchProduct(ctx context.Context, id string) (ProductDTO, error) {
    ctx, cancel := context.WithTimeout(ctx, 250*time.Millisecond)
    defer cancel()

    product, err := s.Repo.Get(ctx, id)
    if err != nil { return ProductDTO{}, err }

    group, ctx := errgroup.WithContext(ctx)
    var inv Inventory
    var price Price
    group.Go(func() error { var e error; inv, e = s.Inventory.Get(ctx, id); return e })
    group.Go(func() error { var e error; price, e = s.Pricing.Get(ctx, id); return e })
    if err := group.Wait(); err != nil { return ProductDTO{}, err }

    product.Inventory = inv
    product.Price = price
    return MapProduct(product), nil
}
```

### 6. Checklists
- Separation: domain has zero imports from web/DB/messaging frameworks.
- Observability: every handler emits traces, metrics (latency, errors), structured logs with correlation IDs.
- Failure modes: timeouts on all I/O, retries with jitter for idempotent calls, circuit breakers for flaky upstreams.
- Testing: unit (domain/services), integration (adapters with real deps via testcontainers), contract (API schemas), e2e (happy path).

### 7. Extension Topics
- CQRS: split read models from write models for high‑read domains.
- Event sourcing: persist events, rebuild aggregates, snapshotting strategy.
- Modular monolith vs microservices: start modular; extract when bounded contexts and operational readiness justify it.
