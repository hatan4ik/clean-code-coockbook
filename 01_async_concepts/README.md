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

#### 3.1 Blocking (anti‑pattern)
```python
# Takes ~600ms+ because calls run serially.
def fetch_product_blocking(id: str) -> dict:
    inv = inventory.get(id)          # blocks thread
    price = pricing.get(id)          # blocks thread
    reviews = reviews.get(id)        # blocks thread
    return {"id": id, "inventory": inv, "price": price, "reviews": reviews}
```

#### 3.2 Python asyncio solution
```python
import asyncio
from asyncio import TaskGroup, TimeoutError

async def fetch_product(id: str) -> dict:
    try:
        async with TaskGroup() as tg:
            inv = tg.create_task(inventory.get(id, timeout=0.2))
            price = tg.create_task(pricing.get(id, timeout=0.2))
            reviews = tg.create_task(reviews.get(id, timeout=0.2))
    except TimeoutError:
        # bubble up to API layer to return 504 or partial data
        raise

    return {
        "id": id,
        "inventory": await inv,
        "price": await price,
        "reviews": await reviews or [],
    }
```

#### 3.3 Go goroutines + errgroup
```go
import (
    "context"
    "time"
    "golang.org/x/sync/errgroup"
)

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

### 4. Patterns and Guardrails
- Prefer `asyncio.TaskGroup` (Python 3.11+) over `gather` for better error propagation.
- Always set timeouts; propagate `context.Context` (Go) and cancellation (Python) to downstream calls.
- Apply backpressure: semaphores for concurrency limits; worker pools for CPU‑bound work.
- Avoid blocking calls inside async code (`time.sleep`, synchronous HTTP clients). Use `asyncio.to_thread` or process pools for CPU‑heavy tasks.

### 5. Zero‑to‑Hero Path for This Module
- Step 1: Run the blocking vs async scripts; measure timing with 5/50/500 concurrent requests.
- Step 2: Add timeouts and retries with jitter; observe latency distributions.
- Step 3: Introduce a semaphore/worker pool to cap fan‑out; add tracing spans per upstream call.
- Step 4: Ship the aggregator as a FastAPI handler (Python) and Gin/Chi handler (Go) with metrics and structured logs.
- Step 5: Write tests: unit tests for orchestration, integration tests with mocked upstream delays, contract tests for response shape.

### 6. What Success Looks Like
- Measurable improvement: 10x concurrency with the same hardware; predictable p99 with controlled timeouts.
- Code is readable, typed, and testable; cancellation works end‑to‑end; observability shows spans per upstream call.
