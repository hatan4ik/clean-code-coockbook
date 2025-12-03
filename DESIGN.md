# Clean Code Cookbook: Technical Design Specification

Principal AI Engineer view on building a zero‑to‑hero, production‑grade cookbook for backend engineers in Python and Go. This document is the single source of truth for scope, audience, structure, examples, and quality bars.

## 1) Purpose, Scope, Outcomes
- Teach engineers to ship maintainable, observable, and scalable backends in Python and Go through opinionated patterns plus runnable examples.
- Cover the path from fundamentals to production concerns: readability → concurrency → architecture → data + APIs → testing → operations.
- Deliver paired Python/Go examples for the same real‑world problems (HTTP orchestration, data access, resilience, observability).
- Produce artifacts that can be copied into real services (not just snippets): small reference apps, test suites, infra templates.

## 2) Audience and Success Criteria
- Audience: mid/senior backend engineers, tech leads, and architects switching stacks (Python ⇄ Go) or levelling up production craft.
- Success: readers can (a) design a feature with clean boundaries, (b) ship it with tests, tracing, and guardrails, (c) debug it in prod.
- Style: pragmatic FAANG‑like standards, security first, automated verification, minimal ceremony.

## 3) Core Principles and Non‑Goals
- Principles: clarity over cleverness, pure domain separated from I/O, testability by design, explicit contracts, incremental delivery.
- Non‑goals: UI concerns, exhaustive language syntax coverage, academic patterns without operational value, vendor lock‑in to one cloud.

## 4) Repository Layout
```
clean-code-coockbook/
├── DESIGN.md                      # This specification
├── 01_async_concepts/             # Async mental models and concurrency primitives
│   └── README.md
├── 02_architecture_blueprint/     # Hexagonal / modular monolith blueprints
│   └── STRUCTURE.md
├── python/                        # Python reference implementations (FastAPI/asyncio)
│   ├── services/
│   ├── libs/                      # Shared helpers (logging, config, middlewares)
│   └── tests/
├── go/                            # Go reference implementations (net/http, Gin, gRPC)
│   ├── services/
│   ├── pkg/                       # Shared packages (logging, config, middleware)
│   └── internal/tests/
└── tooling/                       # CI/CD, linting, devcontainers, docker-compose, Makefiles
```

## 5) Content Tracks and Deliverables
- Foundations (language‑idiomatic clean code): naming, pure functions, error contracts, dependency management.
- Concurrency and async: asyncio vs goroutines/channels; when to prefer threads/processes; backpressure and cancellation.
- Architecture: hexagonal layering, domain models, application services, adapters/ports, event‑driven extensions.
- API design: REST (FastAPI/Gin), gRPC, pagination/versioning, idempotency, authN/Z, schema evolution.
- Data and state: SQL/NoSQL adapters, caching (Redis), idempotent workflows, transactions/unit of work.
- Reliability and observability: structured logging, metrics, tracing (OpenTelemetry), health/readiness, rate limiting, circuit breaking.
- Testing strategy: test pyramid, property tests, contract tests, testcontainers, fixtures/builders, golden files (Go).
- Operations: packaging (Poetry/Hatch; Go modules), container images, CI gates, migrations, rollout patterns (blue/green, canary).

## 6) Real‑World Example Threads (paired Python/Go)

### 6.1 HTTP Orchestrator (Fan‑out/Fan‑in)
- Problem: Aggregate product data from `inventory`, `pricing`, and `reviews` services with tight latency budgets; upstreams can be slow.
- Python solution: async fan‑out with `asyncio.TaskGroup`, timeouts, fallbacks.

```python
# python/services/catalog/handlers.py
from asyncio import TaskGroup, TimeoutError
from .clients import inventory, pricing, reviews

async def fetch_product(product_id: str) -> dict:
    async with TaskGroup() as tg:
        inv = tg.create_task(inventory.get(product_id, timeout=0.2))
        price = tg.create_task(pricing.get(product_id, timeout=0.2))
        revs = tg.create_task(reviews.get(product_id, timeout=0.2))
    return {
        "id": product_id,
        "inventory": await inv,
        "price": await price,
        "reviews": await revs or [],
    }
```

- Go solution: goroutines + `context.Context` for cancellation, `errgroup` for error propagation.

```go
// go/services/catalog/handler.go
func FetchProduct(ctx context.Context, id string, c Clients) (Product, error) {
	ctx, cancel := context.WithTimeout(ctx, 200*time.Millisecond)
	defer cancel()

	group, ctx := errgroup.WithContext(ctx)
	var inv Inventory
	var price Price
	var revs []Review

	group.Go(func() error { var err error; inv, err = c.Inventory.Get(ctx, id); return err })
	group.Go(func() error { var err error; price, err = c.Pricing.Get(ctx, id); return err })
	group.Go(func() error { var err error; revs, err = c.Reviews.Get(ctx, id); return err })

	if err := group.Wait(); err != nil {
		return Product{}, err
	}
	return Product{ID: id, Inventory: inv, Price: price, Reviews: revs}, nil
}
```

### 6.2 Transactional Workflow with Unit of Work
- Problem: Place order with inventory reservation and payment authorization; ensure atomicity and retries.
- Python: domain service uses Unit of Work, emits events; adapters implemented with SQLAlchemy + message bus.
- Go: service layer uses repository interfaces and `sql.Tx`, publishes to Kafka via outbox pattern.

### 6.3 Observability and Resilience
- Problem: Debug latency spikes and partial failures.
- Python: `structlog` JSON logs, OpenTelemetry traces, circuit breaker decorator (Tenacity/async).
- Go: middleware injecting trace/span IDs, Prometheus metrics, circuit breaker with `sony/gobreaker`.

## 7) Architecture Standards

### 7.1 Python (Hexagonal, Async‑first)
- Entry: FastAPI/CLI; application services orchestrate domain logic and ports.
- Ports: `Repository`, `Notifier`, `MessageBus` protocols; adapters for Postgres/Redis/Kafka.
- Concurrency: async I/O first; for CPU, offload to `concurrent.futures.ProcessPoolExecutor`.
- Config: 12‑factor via Pydantic settings; strict typing; Ruff + mypy; Poetry/Hatch.

### 7.2 Go (Standard Layout, Interface‑driven)
- Layout: `/cmd/<service>/main.go`, `/internal/<service>/` for domain/app, `/pkg/` for shared libs.
- Interfaces at consumer side; structs at provider side.
- Concurrency: goroutines/channels; cancellation with context; rate limits via token buckets.
- Tooling: `gofmt`, `golangci-lint`, `staticcheck`, `go test -race`.

## 8) Patterns to Teach (with runnable slices)
- Async patterns: fan‑out/fan‑in, worker pools, timeouts, retries with jitter, bulkheads.
- Data patterns: repository/unit of work, outbox/inbox, idempotency keys, pagination, optimistic locking.
- API patterns: versioning, error envelopes, validation, auth middlewares, input/output DTOs.
- Reliability: circuit breakers, hedged requests, rate limiting, graceful shutdown, health/readiness.
- Testing: table‑driven tests (Go), property tests (Hypothesis), contract tests (pact), fixture isolation.

## 9) Zero‑to‑Hero Path
- Phase 1: Foundations — idiomatic language basics, formatting, typing/interfaces, simple CRUD with tests.
- Phase 2: Async/Concurrency — implement the HTTP orchestrator; add backpressure and cancellation.
- Phase 3: Architecture — refactor to ports/adapters; add caching and unit of work.
- Phase 4: Reliability — add tracing, metrics, structured logging, retries/circuit breakers.
- Phase 5: Operations — containerize, add CI gates (lint, fmt, typecheck, tests), blue/green rollout.
- Each phase ships both Python and Go variants plus checklists and “copy/paste” skeletons.

## 10) Tooling and Quality Gates
- Python: `ruff check --fix`, `ruff format`, `mypy --strict`, `pytest -q`, `pytest --hypothesis-profile=ci`.
- Go: `gofmt -w ./...`, `golangci-lint run`, `go test ./... -race -count=1`.
- CI: pre-commit hooks, GitHub Actions workflows for lint/type/test, testcontainers for integration, SBOM + dependency scanning.
- Security: secrets scanning, SAST (Snyk or CodeQL), least privilege for service accounts, secure defaults for TLS.

## 11) Contribution and Governance
- Conventional commits; small, reviewable PRs; require tests for new content or code.
- Documentation close to code: every pattern has a README, runnable sample, and tests.
- Decision log inside `DESIGN.md` (append notes per change); avoid rewrites without rationale.

## 12) Next Steps to Materialize
- Seed `python/services/catalog` and `go/services/catalog` with the HTTP orchestrator example above, including tests and tracing.
- Flesh out `01_async_concepts` with deeper asyncio and goroutine patterns and real metrics/benchmarks.
- Expand `02_architecture_blueprint` with Python/Go side-by-side project skeletons and a guided refactor checklist.
- Add tooling under `tooling/` (Makefiles, lint configs, CI examples).
