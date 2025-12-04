# Module 1: The Async Mental Model

## Stop Waiting, Start Reacting

This module moves from blocking, thread‑bound thinking to event‑loop and goroutine mindsets. We focus on real operational wins: higher throughput, lower memory, predictable latency.

### 1. Problem: The Cost of Blocking

- Traditional Python web stacks (WSGI) and naive Go code often run one request per OS thread.
- Blocking I/O (DB calls, HTTP calls, `time.Sleep`) parks the thread and wastes RAM/CPU cycles.
- If 500 threads each wait on a 1s DB call, your maximum throughput is ~500 RPS regardless of CPU headroom.

### 2. Solution: Event Loops and Goroutines

- Python: `asyncio` schedules many tasks on a single thread; tasks yield on `await` and free the event loop.
- Go: lightweight goroutines multiplex onto OS threads; `context.Context` controls cancellation/timeouts; channels coordinate work.
- Async is contagious: any blocking call inside async code blocks the entire loop (Python) or strand goroutines (Go). Use async/native clients.

### 3. Real‑World Example — HTTP Fan‑Out Aggregator

**Problem:** Build a product endpoint that queries three upstream services (`inventory`, `pricing`, `reviews`) within 200ms p99.

- [Python asyncio solution](./python.md)
- [Go goroutines + errgroup](./go.md)

### 4. Zero‑to‑Hero Path (Do This, Measure It)

- **Step 1 — Baseline:** Run blocking vs async scripts; record latency at 5/50/500 concurrency.
- **Step 2 — Deadlines & Jittered Retries:** Add per-upstream timeouts and bounded retries; watch p95/p99 shift.
- **Step 3 — Backpressure:** Introduce semaphores/worker pools to cap fan‑out; validate no overload of upstreams.
- **Step 4 — Ship It:** Expose the fan‑out as a FastAPI handler (Python) and Gin/Chi handler (Go) with structured logs and trace spans per upstream.
- **Step 5 — Tests:** Unit-test orchestration; integration tests with delayed/failing upstream fakes; contract tests for response shape.
- **Step 6 — Resilience:** Add circuit breakers/hedged requests; ensure cancellation propagates; prove graceful degradation (partial responses when safe).

### 5. What Success Looks Like

- Measurable improvement: 10x concurrency with the same hardware; predictable p99 with controlled timeouts.
- Code is readable, typed, and testable; cancellation works end‑to‑end; observability shows spans per upstream call.

### 6. Patterns and Guardrails

- **Timeout discipline:** per-upstream deadlines slightly below the request deadline; fail fast to protect the system.
- **Backpressure:** semaphores or bounded worker pools to cap fan-out; shed load early when saturated.
- **Cancellation propagation:** never swallow `CancelledError`/context cancellations; ensure spawned tasks are supervised and cleaned up.
- **Error typing:** raise/return typed errors for timeouts vs failures; prefer partial responses over total failure when safe.
- **Avoid blocking in async:** no `time.sleep`/blocking clients in async code; offload CPU to process pools.

### 7. Measure & Observe (make it visible)

- Latency histograms: p50/p95/p99 for the overall request and per-upstream spans.
- Concurrency/backpressure: current semaphore usage, queue lengths, in-flight tasks/goroutines.
- Errors vs timeouts vs cancellations: separate metrics to diagnose the true bottleneck.
- Saturation signals: CPU, event loop lag (Python), goroutine count/blocking profiles (Go).
- Load-test matrices: vary concurrency (5/50/500) and upstream delay/failure rates; plot the knee of the curve and validate breakers/timeouts.
