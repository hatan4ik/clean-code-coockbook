# Language Tracks Technical Design Specification

Architectural lens: Idiomatic Consistency, Performance Scalability, Operational Excellence. Zero-to-hero progression: primitives → patterns → production slices with tests/observability.

## Python Modernization Module (Async-first, Typed, DX)
- Goals: modern idiomatic Python; strict typing (`mypy --strict`); async-by-default orchestration; developer experience accelerators.
- Scope: Ruff lint/format; dataclasses/pydantic VOs; error taxonomies; `asyncio.TaskGroup` with timeouts/cancellation; semaphores/backpressure; CPU offload via process pools; ports as `Protocol`; unit of work + outbox; DTO mappers; simple DI wiring; structlog JSON + OpenTelemetry + Prometheus; retries/circuit breakers; pytest + pytest-asyncio + Hypothesis; contract/integration via testcontainers.
- Key problem/solution threads: strict typing + Pydantic contracts (see `python/mypy.md`), async fan-out (`01_async_concepts/README.md`), hexagonal flow (`02_architecture_blueprint/python.md`).
- Deliverables: `python/services/catalog` reference (fan-out/fan-in) with tests and tracing; pyproject/ruff/mypy configs; Make targets and CI jobs (lint/format/type/test).
- Zero→Hero path: CRUD + typing → async orchestration with timeouts → hexagonal refactor (ports/UoW/outbox) → resilience/observability → container/CI rollout.

## Go Systems Module (Simplicity, Interfaces, Concurrency)
- Goals: simplicity-as-feature; interface-driven design; predictable concurrency; perf + observability defaults.
- Scope: standard layout (`/cmd`, `/internal/app|domain|ports|adapters|platform`, `/pkg` for shared); goroutines/channels/errgroup; context propagation; backpressure (worker pools, rate limiters); leak avoidance; ports near consumers; DTO/domain separation; `sql.Tx` unit of work; outbox; structured logs (zap/zerolog), Prometheus, OpenTelemetry, graceful shutdown, circuit breakers/hedged requests; table-driven tests, testify/mock, golden files, race detector, integration with docker-compose/testcontainers-go.
- Key problem/solution threads: interfaces + layout (`02_architecture_blueprint/go.md`), fan-out with deadlines (`01_async_concepts/go.md`), error handling/testing guides (per go/*).
- Deliverables: `go/services/catalog` mirroring Python example; gofmt/golangci-lint/staticcheck configs; Make targets and CI pipeline.
- Zero→Hero path: CRUD with interfaces → concurrency patterns with deadlines → ports/adapters refactor + UoW → resilience/observability → container/CI rollout.

## Polyglot Architecture Bridge (Python “brains”, Go “brawn”)
- Goals: teach interop patterns so Python ML/data services and Go high-throughput edges compose cleanly.
- Scope: protobuf contracts as single source; versioning/backward compatibility; codegen for both stacks; gRPC unary/streaming and when to prefer REST; timeout/deadline alignment; retries/idempotency keys; auth (mTLS/JWT); trace propagation/correlation IDs; DTO parity and error envelopes; deployment and rollout guardrails (health/readiness, SLOs, blue/green/canary).
- Key problem/solution threads: gRPC contract + Python service + Go client (`04_polyglot_architecture/grpc.md`), cross-stack tracing/auth/timeout alignment.
- Deliverables: `proto/recommendations.proto`; Python recommender service; Go gateway client; E2E example invoking both; CI codegen step and lint/type/test gates for generated code.
- Zero→Hero path: define proto + codegen → unary call path with tracing/auth → streaming example → contract versioning exercise → E2E test across both runtimes.

## Cross-Cutting Enforcement
- Quality gates: Python (`ruff check --fix`, `ruff format`, `mypy --strict`, `pytest -q`); Go (`gofmt`, `golangci-lint`, `staticcheck`, `go test ./... -race -count=1`).
- Tooling: Make targets and GitHub Actions templates under `tooling/`; secrets scanning and SAST; SBOM/dependency scanning.
- Documentation: each pattern gets a README, runnable slice, and tests colocated; decision log updates in `DESIGN.md`.
