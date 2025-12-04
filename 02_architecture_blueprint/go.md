### Directory Structure Explained

Go's idiomatic project structure emphasizes clarity and separation of concerns. The `internal` directory is a key feature, as it prevents other applications from importing its code.

```text
go/services/catalog/
├── cmd/catalog/main.go        # Wire HTTP server and dependencies
├── internal/app/              # Use cases; orchestrates domain and ports
├── internal/domain/           # Entities, value objects, domain services
├── internal/ports/            # Interfaces for repositories, publishers, clients
├── internal/adapters/         # Postgres, Redis, Kafka, HTTP clients
├── internal/platform/         # Logging, config, middleware, health
└── internal/tests/            # Unit, integration, contract
```

- **`cmd/catalog/main.go`**: The entry point of your application. This is where you initialize your dependencies (like database connections and loggers), wire them up, and start the HTTP server.

- **`internal/app/`**: This directory contains the application's use cases. Each use case should be in its own file. The use cases orchestrate the domain logic and interact with the ports.

- **`internal/domain/`**: The heart of your application. It contains the core business logic, models, and rules.
  - It's common to have sub-packages within `domain` for different domain concepts (e.g., `product`, `order`).

- **`internal/ports/`**: Defines the interfaces that your application uses to interact with the outside world. These interfaces are the "ports" in the hexagonal architecture.
  - For example, you might have a `ProductRepository` interface for storing and retrieving products.

- **`internal/adapters/`**: This is where you implement the outbound ports. Adapters are responsible for interacting with external systems like databases, message brokers, and other APIs.
  - Each adapter should implement one or more of the interfaces defined in the `ports` directory.

- **`internal/platform/`**: This directory contains the code that is specific to your platform, such as logging, configuration, and HTTP middleware.

- **`internal/tests/`**: Contains the tests for your application. Go's testing tools are powerful, and you should leverage them to write a comprehensive test suite.

### Sample Flow Explained

The sample flow demonstrates how a use case is executed within the hexagonal architecture.

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

1. **`FetchProduct`**: This is a use case handler that takes a `context.Context` and a product ID as input.
2. **`context.WithTimeout`**: The `context.WithTimeout` function creates a new context with a timeout. This is important for preventing long-running requests from tying up resources.
3. **`s.Repo.Get(...)`**: The handler uses the repository to fetch the product from the database.
4. **`errgroup.WithContext`**: The `errgroup` package is used to fetch the inventory and pricing information concurrently. This is a good example of how to leverage Go's concurrency features to improve performance.
5. **`MapProduct(product)`**: Finally, the handler converts the domain object into a Data Transfer Object (DTO) before returning it.

### Dependency Injection in Go

Go doesn't have a built-in dependency injection container like some other languages, but it's easy to implement dependency injection manually. The most common way to do this is to use constructor injection.

Here's an example of how you can use constructor injection to provide a `ProductRepository` to your `Service`:

```go
// internal/app/service.go
type Service struct {
    Repo ProductRepository
}

func NewService(repo ProductRepository) *Service {
    return &Service{Repo: repo}
}
```

In this example, the `NewService` function is a constructor that takes a `ProductRepository` as input and returns a new `Service`. When you create a new `Service`, you can pass in a mock `ProductRepository` for testing.
