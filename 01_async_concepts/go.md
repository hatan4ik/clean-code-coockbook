### Go Goroutines + `errgroup`

This solution uses goroutines and the `golang.org/x/sync/errgroup` package to concurrently fetch data from multiple upstream services. `errgroup` provides a safe and reliable way to manage a group of goroutines, ensuring that if one goroutine returns an error, the others are cancelled.

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

- **`func FetchProduct(...)`**: This defines a function that takes a `context.Context`, a product ID, and a `Clients` struct as input.
- **`context.WithTimeout(...)`**: This creates a new `context.Context` with a timeout. This is important for preventing long-running requests from tying up resources. The `defer cancel()` ensures that the context is cancelled when the function returns.
- **`errgroup.WithContext(...)`**: This creates a new `errgroup` that is associated with the `context.Context`. If the context is cancelled, the `errgroup` will also be cancelled.
- **`group.Go(...)`**: This starts a new goroutine within the `errgroup`. The goroutine will execute the provided function. If the function returns an error, the `errgroup` will cancel the other goroutines and return the error.
- **`group.Wait()`**: This blocks until all the goroutines in the `errgroup` have completed. If any of the goroutines returned an error, `Wait()` will return that error.

### Running and Testing

To run this code, you would typically call this `FetchProduct` function from within an HTTP handler in a web framework like `net/http`, Chi, or Gin.

For testing, you can use Go's built-in testing package. You can create a mock `Clients` struct that returns canned data, and then call `FetchProduct` with a test context.

### Dependency Injection

In this example, the `Clients` struct is a form of dependency injection. The `FetchProduct` function doesn't create the clients itself; it receives them as an argument. This makes the function easier to test, as you can pass in mock clients during testing.

```go
type Clients struct {
    Inventory *InventoryClient
    Pricing   *PricingClient
    Reviews   *ReviewsClient
}
```

This pattern is very common in Go and is a great way to write clean, testable code.

### Backpressure and Deadlines

Cap concurrent work and enforce deadlines to keep tail latency predictable.

```go
package catalog

import (
    "context"
    "time"
    "golang.org/x/sync/semaphore"
)

var sem = semaphore.NewWeighted(50)

func FetchMany(ctx context.Context, ids []string, c Clients) ([]Product, error) {
    ctx, cancel := context.WithTimeout(ctx, 250*time.Millisecond)
    defer cancel()

    results := make([]Product, len(ids))
    g, ctx := errgroup.WithContext(ctx)

    for i, id := range ids {
        i, id := i, id
        g.Go(func() error {
            if err := sem.Acquire(ctx, 1); err != nil {
                return err
            }
            defer sem.Release(1)
            p, err := FetchProduct(ctx, id, c)
            if err != nil {
                return err
            }
            results[i] = p
            return nil
        })
    }

    if err := g.Wait(); err != nil {
        return nil, err
    }
    return results, nil
}
```

- `semaphore.Weighted` limits concurrency across requests; avoids overload.
- Context deadline keeps the whole batch bounded; partials can be returned if desired.
