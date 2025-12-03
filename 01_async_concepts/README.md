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

*   [Python asyncio solution](./python.md)
*   [Go goroutines + errgroup](./go.md)

### 4. Zero‑to‑Hero Path for This Module
- Step 1: Run the blocking vs async scripts; measure timing with 5/50/500 concurrent requests.
- Step 2: Add timeouts and retries with jitter; observe latency distributions.
- Step 3: Introduce a semaphore/worker pool to cap fan‑out; add tracing spans per upstream call.
- Step 4: Ship the aggregator as a FastAPI handler (Python) and Gin/Chi handler (Go) with metrics and structured logs.
- Step 5: Write tests: unit tests for orchestration, integration tests with mocked upstream delays, contract tests for response shape.

### 5. What Success Looks Like
- Measurable improvement: 10x concurrency with the same hardware; predictable p99 with controlled timeouts.
- Code is readable, typed, and testable; cancellation works end‑to‑end; observability shows spans per upstream call.