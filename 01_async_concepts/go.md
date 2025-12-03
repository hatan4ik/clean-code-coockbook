### Go goroutines + errgroup
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

### Patterns and Guardrails
- Always set timeouts; propagate `context.Context` (Go) and cancellation (Python) to downstream calls.
- Apply backpressure: semaphores for concurrency limits; worker pools for CPU‑bound work.
