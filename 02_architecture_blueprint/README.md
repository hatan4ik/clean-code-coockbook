# Module 2: The Hexagonal Blueprint

## The Anatomy of a Scalable Python/Go System

This module defines the reference architecture for all cookbook examples. The goal: isolate pure domain logic, keep I/O behind ports, and make services testable and replaceable.

### 1. Directory Templates

* [Python (FastAPI/asyncio)](./python.md)
* [Go (Chi/Gin or net/http)](./go.md)

### 2. Request Lifecycle (example: GET /products/{id})

1) Transport layer validates inputs and creates a request context (trace/span IDs, timeouts).
2) Application handler calls a use case (`FetchProduct`) that orchestrates domain logic.
3) Use case talks to ports (`ProductRepository`, `InventoryClient`, `MessageBus`) provided via DI.
4) Adapters implement ports; they map errors to domain errors and handle retries/idempotency.
5) Response DTOs are serialized; metrics and traces are emitted; deadlines respected.

### 3. Key Patterns
* **Ports and Adapters:** Interfaces live close to consumers; adapters register via constructors/factories.
* **Unit of Work:** Wrap DB operations in a transaction; emit domain events; publish via outbox.
* **DTOs vs Domain:** Keep domain models free from framework types. Map at the edges.
* **Configuration:** 12‑factor, environment driven; validate at startup; secrets from env/SM.
* **Validation:** Input validation at transport layer; business invariants in domain; database constraints enforce last line of defense.
* **Error Model:** Typed errors with HTTP mapping; avoid panics/exceptions crossing layers; include correlation IDs.

### 4. Sample Flows

These links provide concrete, line-by-line examples of how a request flows through the hexagonal architecture, from the web handler to the domain logic and back. They illustrate the key patterns in action.

* [Python](./python.md#sample-flow-python)
* [Go](./go.md#sample-flow-go)

### 5. Checklists
* Separation: domain has zero imports from web/DB/messaging frameworks.
* Observability: every handler emits traces, metrics (latency, errors), structured logs with correlation IDs.
* Failure modes: timeouts on all I/O, retries with jitter for idempotent calls, circuit breakers for flaky upstreams.
* Testing: unit (domain/services), integration (adapters with real deps via testcontainers), contract (API schemas), e2e (happy path).

### 6. Extension Topics
* CQRS: split read models from write models for high‑read domains.
* Event sourcing: persist events, rebuild aggregates, snapshotting strategy.
* Modular monolith vs microservices: start modular; extract when bounded contexts and operational readiness justify it.
