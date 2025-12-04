# Python Language Guidelines (Zero → Hero)

Lens: Idiomatic Consistency, Performance Scalability, Operational Excellence. Each chapter is Problem → Solution with runnable slices and gates.

## Chapter 1 — Strict Typing & Data Contracts

- Problem: dynamic drift (`NoneType` crashes, refactor risk, weak IDE aid).
- Solution: `mypy --strict` + Pydantic data models; ports as `Protocol`; CI gates.
- Read: [mypy.md](./mypy.md), [pydantic.md](./pydantic.md)
- Do: enable strict, model all inputs as Pydantic, define ports as protocols, add CI stage.
- Success: zero implicit `Any`, explicit Optional handling, validated payloads at edges.

## Chapter 2 — Modern Concurrency (Asyncio)

- Problem: blocking I/O caps throughput; hidden latency spikes.
- Solution: `asyncio.TaskGroup`, timeouts, cancellation, semaphores/backpressure.
- Read: [asyncio.md](./asyncio.md), `01_async_concepts/README.md`
- Do: convert blocking handlers, add deadlines and backpressure, test cancellation paths.
- Success: stable p99 under load; cancellation propagates; no blocking calls in async paths.

## Chapter 3 — Application Layout & DI

- Problem: script sprawl; hidden globals; tangled dependencies.
- Solution: hexagonal layout (domain/ports/adapters/service layer), simple DI wiring.
- Read: `02_architecture_blueprint/python.md`, [dependency_injection.md](./dependency_injection.md)
- Do: refactor to ports/adapters, introduce UoW/outbox, use DTO mappers at edges.
- Success: domain free of framework imports; adapters swap via interfaces; tests run fast.

## Chapter 4 — DX, Testing, and Metaprogramming

- Problem: boilerplate, slow feedback loops, brittle tests.
- Solution: fixtures/builders, property tests (Hypothesis), safe metaprogramming for ergonomics.
- Read: [metaprogramming.md](./metaprogramming.md)
- Do: add builders/fixtures, property tests for core logic, avoid dynamic hacks without types.
- Success: fast, isolated tests; metaprogramming guarded by types; clear failure signals.

## Chapter 5 — Operations & Observability

- Problem: dark prod; hard to debug incidents.
- Solution: structlog JSON, OTEL traces, Prometheus metrics, health/readiness, circuit breakers.
- Read: `05_tooling_and_best_practices/observability.md`
- Do: emit traces per request + upstream span, add breakers/retries with jitter, wire dashboards.
- Success: actionable logs/metrics/traces; graceful shutdown; clear SLOs/alerts.

### Topic Links

- **[Asyncio](./asyncio.md)**
- **[Dependency Injection](./dependency_injection.md)**
- **[Metaprogramming](./metaprogramming.md)**
- **[MyPy](./mypy.md)**
- **[Pydantic](./pydantic.md)**
