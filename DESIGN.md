# Clean Code Cookbook: Technical Design Specification

Product mindset: this is a knowledge system that codifies how to build production-grade Python and Go services with minimal cognitive load and guardrails against tech debt. Pillars: **Idiomatic Consistency**, **Performance Scalability**, **Operational Excellence**.

## 1) Purpose & Scope

- Teach engineers to ship maintainable, observable, and scalable backends in Python and Go.
- Provide zero→hero tracks with runnable examples, tests, and infra templates.
- Align language idioms with architecture (hexagonal/clean), concurrency patterns, and production hygiene (security, CI, observability).

## 2) Target Audience & Outcomes

- Audience: mid/senior backend engineers, tech leads, and architects moving between Python/Go or leveling up to production standards.
- Outcomes: design features with clean boundaries; ship with types, tests, tracing, and guardrails; debug confidently in prod.

## 3) Architecture Pillars (Problem → Solution)

- **Idiomatic Consistency:** Problem: “script” mindset (globals, dynamic drift, ad-hoc layouts). Solution: strict typing/contracts, clear layering, enforced style/lint/type gates.
- **Performance Scalability:** Problem: blocking I/O, unbounded fan-outs, goroutine leaks. Solution: async/await with backpressure (Python), goroutines/errgroup with context deadlines (Go), hedging/circuit breakers.
- **Operational Excellence:** Problem: dark launches and brittle ops. Solution: structured logs, metrics, tracing, health/readiness, CI/CD gates, security scanning, and rollout playbooks.

## 4) Track Overviews (Zero → Hero)

### 4.1 Python Modernization (flexible foundation)

- **Core shifts:** strict typing (`mypy --strict`), Pydantic data contracts, async-first orchestration, hexagonal layout.
- **Real-world thread:** Catalog fan-out API (inventory/pricing/reviews) with `asyncio.TaskGroup`, timeouts, retries, tracing.
- **Zero→Hero milestones:**
  1. Type the edges: enable strict mypy; wrap inputs in Pydantic models; kill implicit `Any`.
  2. Concurrency: convert blocking handlers to `async`, add timeouts/backpressure, handle cancellation.
  3. Architecture: refactor to ports (Protocols) + adapters, unit-of-work + outbox, DTO mappers.
  4. Reliability/Obs: structlog JSON, OpenTelemetry tracing, Prometheus metrics, circuit breakers.
  5. Ops: containerize, Make/CI targets (ruff, mypy, pytest), secrets scanning.

### 4.2 Go Systems (performance engine)

- **Core shifts:** simplicity-as-feature, interfaces at consumers, context-first concurrency, standard layout (`/cmd`, `/internal/...`, `/pkg`).
- **Real-world thread:** Same catalog fan-out with `errgroup`, deadlines, circuit breakers; repository + UoW around `sql.Tx`.
- **Zero→Hero milestones:**
  1. Interfaces + DTO/domain separation; table-driven tests.
  2. Concurrency with context deadlines, worker pools, leak prevention.
  3. Ports/adapters with outbox; structured errors and wrapping.
  4. Obs/reliability: zap/zerolog, Prometheus, OTEL tracing, gobreaker/hedged requests.
  5. Ops: gofmt/golangci-lint/staticcheck, `go test -race`, container + CI.

### 4.3 Polyglot Architecture (Python “brains”, Go “brawn”)

- **Core shifts:** single contract via Protobuf; consistent deadlines/auth/tracing across stacks; interoperable DTOs and error envelopes.
- **Real-world thread:** Python recommender service (ML-ish) + Go API gateway; gRPC unary + streaming; codegen in CI.
- **Zero→Hero milestones:**
  1. Define proto, generate clients/servers for both languages.
  2. Wire unary path with deadlines, mTLS/JWT, trace propagation.
  3. Add streaming scenario; handle backpressure and cancellation.
  4. Contract evolution (versioning, backward-compatible changes) and E2E contract tests.
  5. Observability dashboard unifying traces/logs/metrics across languages.

## 5) Repository Structure (current + planned)

- `01_async_concepts/` — async mental model and fan-out examples.
- `02_architecture_blueprint/` — hexagonal blueprint, Python/Go layouts.
- `03_language_specific_guidelines/` — Python & Go tracks (typing, DI, concurrency, testing).
- `04_polyglot_architecture/` — gRPC/interop patterns.
- `05_tooling_and_best_practices/` — CI/CD, linting, observability, security.
- `06_contribution_guidelines/` — contribution rules.
- Planned: `python/services/catalog` and `go/services/catalog` reference apps; `proto/` contracts; `tooling/` with Make/CI templates.

## 6) Problem/Solution Threads (copyable patterns)

- **HTTP fan-out (catalog):** Problem: three upstreams with 200ms budget. Solutions: Python `asyncio.TaskGroup` + timeouts + retries; Go `errgroup` + context deadlines; circuit breakers + partial fallbacks.
- **Transactional workflow (orders):** Problem: inventory reserve + payment auth needs atomicity. Solutions: Python UoW + outbox; Go `sql.Tx` + outbox + repository interfaces.
- **Observability + resilience:** Problem: diagnose latency spikes. Solutions: structlog/zap JSON, OTEL traces with upstream spans, Prometheus SLIs, breakers/hedging.

## 7) Quality Gates (must-pass)

- Python: `ruff check --fix`, `ruff format`, `mypy --strict`, `pytest -q` (plus pytest-asyncio/hypothesis as needed).
- Go: `gofmt`, `golangci-lint`, `staticcheck`, `go test ./... -race -count=1`.
- Security: secrets scanning, SAST (CodeQL/Snyk), dependency/SBOM scanning.
- CI: GitHub Actions templates under `tooling/` (to be added) running the gates per PR.

## 8) Operational Practices

- Config: 12-factor; Pydantic settings (Python); env/config packages (Go).
- Failure handling: timeouts everywhere; retries with jitter only for idempotent ops; circuit breakers on flaky upstreams; graceful shutdown.
- Release: container builds, blue/green or canary, health/readiness endpoints, feature flags where needed.

## 9) Documentation & Examples

- Every pattern ships with: README, runnable slice, and tests. Decision log updates land here when we adjust direction.
- Cross-links:
  - Async mental model: `01_async_concepts/README.md`
  - Hex blueprint: `02_architecture_blueprint/README.md`
  - Language guides: `03_language_specific_guidelines/python/README.md`, `03_language_specific_guidelines/go/README.md`
  - Polyglot: `04_polyglot_architecture/README.md` and `grpc.md`
  - Tooling: `05_tooling_and_best_practices/README.md`
  - Contributions: `06_contribution_guidelines/CONTRIBUTING.md`

## 10) Next Actions

- Seed catalog reference apps (Python/Go) with fan-out example, tracing, tests.
- Add `proto/` with recommender contract and codegen steps; Python server + Go client demo.
- Add `tooling/` with Makefiles and CI templates to enforce gates.
- Deepen language guideline chapters (typing/contracts, concurrency/backpressure, DI, testing) with runnable code.
