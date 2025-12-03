### Directory Templates

#### Go (Chi/Gin or net/http)
```
go/services/catalog/
├── cmd/catalog/main.go        # Wire HTTP server and dependencies
├── internal/app/              # Use cases; orchestrates domain and ports
├── internal/domain/           # Entities, value objects, domain services
├── internal/ports/            # Interfaces for repositories, publishers, clients
├── internal/adapters/         # Postgres, Redis, Kafka, HTTP clients
├── internal/platform/         # Logging, config, middleware, health
└── internal/tests/            # Unit, integration, contract
```

### Sample Flow (Go)
```go
// internal/app/fetch_product.go
func (s Service) FetchProduct(ctx context.Context, id string) (ProductDTO, error) {
    ctx, cancel := context.WithTimeout(ctx, 250*time.Millisecond)
    defer cancel()

    product, err := s.Repo.Get(ctx, id)
    if err != nil { return ProductDTO{}, err }

    group, ctx := errgroup.WithContext(ctx)
    var inv Inventory
    var price Price
    group.Go(func() error { var e error; inv, e = s.Inventory.Get(ctx, id); return e })
    group.Go(func() error { var e error; price, e = s.Pricing.Get(ctx, id); return e })
    if err := group.Wait(); err != nil { return ProductDTO{}, err }

    product.Inventory = inv
    product.Price = price
    return MapProduct(product), nil
}
```
