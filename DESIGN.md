# Clean Code Cookbook: Technical Design Specification

This document outlines the technical design, vision, and architectural principles for the "Clean Code Cookbook." It serves as a guide for contributors and a statement of the project's technical direction.

## 1. Vision & Philosophy

The "Clean Code Cookbook" is not just a collection of code snippets; it's a curated guide to writing robust, scalable, and maintainable backend systems in Python and Go. Our philosophy is rooted in the following principles:

*   **Pragmatism over Dogma:** We favor practical, real-world solutions over theoretical purity.
*   **Clarity and Simplicity:** Code should be self-documenting and easy to reason about.
*   **Strong Architectural Foundations:** We advocate for clean, decoupled architectures that stand the test of time.
*   **Zero-to-Hero Explanations:** We aim to make complex concepts accessible to developers of all levels.

## 2. Target Audience

This cookbook is for:

*   **Mid-level Engineers:** Who want to level up their backend development skills.
*   **Senior Engineers & Architects:** Who are looking for a common language and set of best practices to establish within their teams.
*   **Developers transitioning to Python or Go:** Who want to learn idiomatic and production-ready patterns.

## 3. Core Concepts

This section will be expanded to cover the fundamental principles of clean code, drawing from industry best practices and our own experience. We will start by integrating and refining the existing content.

### 3.1. The Async Mental Model: Stop Waiting, Start Reacting

This module moves from blocking, thread‑bound thinking to event‑loop and goroutine mindsets. We focus on real operational wins: higher throughput, lower memory, predictable latency.

#### 1. Problem: The Cost of Blocking
- Traditional Python web stacks (WSGI) and naive Go code often run one request per OS thread.
- Blocking I/O (DB calls, HTTP calls, `time.Sleep`) parks the thread and wastes RAM/CPU cycles.
- If 500 threads each wait on a 1s DB call, your maximum throughput is ~500 RPS regardless of CPU headroom.

#### 2. Solution: Event Loops and Goroutines
- Python: `asyncio` schedules many tasks on a single thread; tasks yield on `await` and free the event loop.
- Go: lightweight goroutines multiplex onto OS threads; `context.Context` controls cancellation/timeouts; channels coordinate work.
- Async is contagious: any blocking call inside async code blocks the entire loop (Python) or strand goroutines (Go). Use async/native clients.

#### 3. Real‑World Example — HTTP Fan‑Out Aggregator
**Problem:** Build a product endpoint that queries three upstream services (`inventory`, `pricing`, `reviews`) within 200ms p99.

##### 3.1 Blocking (anti‑pattern)
```python
# Takes ~600ms+ because calls run serially.
def fetch_product_blocking(id: str) -> dict:
    inv = inventory.get(id)          # blocks thread
    price = pricing.get(id)          # blocks thread
    reviews = reviews.get(id)        # blocks thread
    return {"id": id, "inventory": inv, "price": price, "reviews": reviews}
```

##### 3.2 Python asyncio solution
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

##### 3.3 Go goroutines + errgroup
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

#### 4. Patterns and Guardrails
- Prefer `asyncio.TaskGroup` (Python 3.11+) over `gather` for better error propagation.
- Always set timeouts; propagate `context.Context` (Go) and cancellation (Python) to downstream calls.
- Apply backpressure: semaphores for concurrency limits; worker pools for CPU‑bound work.
- Avoid blocking calls inside async code (`time.sleep`, synchronous HTTP clients). Use `asyncio.to_thread` or process pools for CPU‑heavy tasks.

#### 5. Zero‑to‑Hero Path for This Module
- Step 1: Run the blocking vs async scripts; measure timing with 5/50/500 concurrent requests.
- Step 2: Add timeouts and retries with jitter; observe latency distributions.
- Step 3: Introduce a semaphore/worker pool to cap fan‑out; add tracing spans per upstream call.
- Step 4: Ship the aggregator as a FastAPI handler (Python) and Gin/Chi handler (Go) with metrics and structured logs.
- Step 5: Write tests: unit tests for orchestration, integration tests with mocked upstream delays, contract tests for response shape.

#### 6. What Success Looks Like
- Measurable improvement: 10x concurrency with the same hardware; predictable p99 with controlled timeouts.
- Code is readable, typed, and testable; cancellation works end‑to‑end; observability shows spans per upstream call.

### 3.2. The Hexagonal Blueprint: The Anatomy of a Scalable Python/Go System

This module defines the reference architecture for all cookbook examples. The goal: isolate pure domain logic, keep I/O behind ports, and make services testable and replaceable.

#### 1. Directory Templates

##### Python (FastAPI/asyncio)
```
python/services/catalog/
├── app.py                     # FastAPI wiring (DI, routes, middlewares)
├── config.py                  # Pydantic settings
├── domain/
│   ├── models.py              # Entities/value objects (dataclasses/pydantic)
│   ├── events.py              # Domain events
│   └── services.py            # Pure orchestrators, no I/O
├── adapters/
│   ├── repositories.py        # Postgres/Redis implementations
│   ├── messaging.py           # Kafka/NATS producers
│   └── http_clients.py        # Async HTTP clients to upstreams
├── ports/
│   ├── repository.py          # Protocols/ABCs
│   └── notifier.py
├── service_layer/
│   ├── unit_of_work.py        # Transaction boundaries
│   └── handlers.py            # Command/query handlers
└── tests/
    ├── unit/
    ├── integration/
    └── e2e/
```

##### Go (Chi/Gin or net/http)
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

#### 2. Request Lifecycle (example: GET /products/{id})
1) Transport layer validates inputs and creates a request context (trace/span IDs, timeouts).
2) Application handler calls a use case (`FetchProduct`) that orchestrates domain logic.
3) Use case talks to ports (`ProductRepository`, `InventoryClient`, `MessageBus`) provided via DI.
4) Adapters implement ports; they map errors to domain errors and handle retries/idempotency.
5) Response DTOs are serialized; metrics and traces are emitted; deadlines respected.

#### 3. Key Patterns
- **Ports and Adapters:** Interfaces live close to consumers; adapters register via constructors/factories.
- **Unit of Work:** Wrap DB operations in a transaction; emit domain events; publish via outbox.
- **DTOs vs Domain:** Keep domain models free from framework types. Map at the edges.
- **Configuration:** 12‑factor, environment driven; validate at startup; secrets from env/SM.
- **Validation:** Input validation at transport layer; business invariants in domain; database constraints enforce last line of defense.
- **Error Model:** Typed errors with HTTP mapping; avoid panics/exceptions crossing layers; include correlation IDs.

#### 4. Sample Flow (Python)
```python
# service_layer/handlers.py
async def fetch_product(cmd: FetchProduct, uow: UnitOfWork) -> ProductDTO:
    async with uow:
        product = await uow.products.get(cmd.product_id)
        inv, price = await asyncio.gather(
            uow.inventory.get(cmd.product_id),
            uow.pricing.get(cmd.product_id),
        )
        product.inventory = inv
        product.price = price
        return ProductDTO.from_domain(product)
```

#### 5. Sample Flow (Go)
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

#### 6. Checklists
- Separation: domain has zero imports from web/DB/messaging frameworks.
- Observability: every handler emits traces, metrics (latency, errors), structured logs with correlation IDs.
- Failure modes: timeouts on all I/O, retries with jitter for idempotent calls, circuit breakers for flaky upstreams.
- Testing: unit (domain/services), integration (adapters with real deps via testcontainers), contract (API schemas), e2e (happy path).

#### 7. Extension Topics
- CQRS: split read models from write models for high‑read domains.
- Event sourcing: persist events, rebuild aggregates, snapshotting strategy.
- Modular monolith vs microservices: start modular; extract when bounded contexts and operational readiness justify it.

## 4. Language-Specific Guidelines

### 4.1. Python: The Modernization Module

This section provides a deep dive into writing clean, robust, and performant Python code, with a focus on modern paradigms.

*   **Declarative Data with Pydantic:** We will move beyond basic dataclasses and embrace `Pydantic` for creating self-documenting, type-hinted, and validated data models.
    *   **Problem:** Standard Python dataclasses don't enforce type correctness at runtime, leading to subtle bugs.
    *   **Solution:** Use Pydantic models to get runtime data validation, serialization, and even JSON Schema generation for free.
    *   **Example:**
        ```python
        from pydantic import BaseModel, EmailStr, PositiveInt

        class UserProfile(BaseModel):
            username: str
            email: EmailStr
            age: PositiveInt
        ```

*   **Strict Typing with `mypy`:** We will enforce a strict type-checking culture.
    *   **Rationale:** Static type analysis catches a significant percentage of bugs before the code ever runs. It also serves as a form of documentation.
    *   **Implementation:** We will integrate `mypy --strict` into our CI pipeline. All new code must pass static analysis.

*   **Metaprogramming for Developer Experience (DX):** We will explore how to use decorators and metaclasses to reduce boilerplate and create more expressive APIs.
    *   **Use Case:** Creating a simple decorator to automatically add logging to a function or a metaclass to register plugins.
    *   **Example (Decorator for timing):**
        ```python
        import time
        from functools import wraps

        def timing_decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                start = time.perf_counter()
                result = func(*args, **kwargs)
                end = time.perf_counter()
                print(f"{func.__name__} took {end - start:.4f} seconds")
                return result
            return wrapper
        ```

*   **Advanced `asyncio` Patterns:** We will go beyond basic `await` calls and explore the patterns needed for building resilient, high-concurrency systems.
    *   **Structured Concurrency with `TaskGroup`:** How to manage the lifecycle of multiple related tasks in a way that is robust and easy to reason about.
    *   **Resource Management:** Using `asyncio.Semaphore` to limit access to a resource (e.g., a connection pool) and `asyncio.Queue` for producer-consumer patterns.

*   **Dependency Injection for Testability:** We will demonstrate how to structure code to facilitate easy testing and component swapping.
    *   **Principle:** "Depend on abstractions, not on concretions."
    *   **Implementation:** We will show how to pass dependencies (like a database connection or an API client) into functions and classes, rather than having them create their own. This makes it trivial to replace them with fakes or mocks in tests.

### 4.2. Go: The Systems Module

This section focuses on architecting Go systems based on the philosophy of "simplicity as a feature." We emphasize clarity, performance, and maintainability.

*   **Simplicity and Readability:** Go's design prioritizes code that is easy to read and understand.
    *   **Guideline:** Avoid overly complex abstractions. A little bit of repeated code is often better than a complex abstraction that is hard to understand.
    *   **Example:** We will favor simple, clear function and package names. Error handling is explicit and verbose for a reason: it makes the control flow obvious.

*   **Concurrency with Goroutines and Channels:** We will explore Go's powerful and simple concurrency model.
    *   **Philosophy:** "Do not communicate by sharing memory; instead, share memory by communicating."
    *   **Pattern (Worker Pool):** A common and powerful pattern is the worker pool, where a fixed number of goroutines (workers) process tasks from a channel. This is a great way to control concurrency and resource usage.
    *   **Example (Worker Pool):**
        ```go
        func worker(id int, jobs <-chan int, results chan<- int) {
            for j := range jobs {
                fmt.Println("worker", id, "started job", j)
                time.Sleep(time.Second) // Simulate work
                fmt.Println("worker", id, "finished job", j)
                results <- j * 2
            }
        }

        func main() {
            numJobs := 5
            jobs := make(chan int, numJobs)
            results := make(chan int, numJobs)

            for w := 1; w <= 3; w++ {
                go worker(w, jobs, results)
            }

            for j := 1; j <= numJobs; j++ {
                jobs <- j
            }
            close(jobs)

            for a := 1; a <= numJobs; a++ {
                <-results
            }
        }
        ```

*   **Interface-Driven Design:** Interfaces are at the heart of Go's flexibility.
    *   **Principle:** "Accept interfaces, return structs." This allows for easy mocking in tests and decoupling of components.
    *   **Example:** Instead of depending on a concrete `*sql.DB`, a service should depend on an interface that defines the methods it needs. This allows you to provide a real database in production and a mock database in tests.
        ```go
        // In the domain layer
        type UserStore interface {
            GetUser(ctx context.Context, id string) (*User, error)
        }

        // In the service layer
        type UserService struct {
            store UserStore
        }

        func (s *UserService) GetUser(ctx context.Context, id string) (*User, error) {
            return s.store.GetUser(ctx, id)
        }
        ```

*   **Error Handling as a First-Class Citizen:** We will demonstrate robust error handling strategies.
    *   **Guideline:** Errors are values. They should be handled explicitly and gracefully.
    *   **Technique:** We will use `errors.As` and `errors.Is` for checking specific error types, and wrap errors to provide context.
        ```go
        if err != nil {
            return fmt.Errorf("failed to process user %s: %w", userID, err)
        }
        ```

## 5. Architectural Patterns

This section will explore architectural patterns beyond the hexagonal blueprint, providing real-world examples and use cases. Topics will include:

*   **CQRS (Command Query Responsibility Segregation):**
    *   **Concept:** Separating the models used for writing data (Commands) from the models used for reading data (Queries).
    *   **Use Case:** High-throughput systems where read and write patterns are vastly different. For example, an e-commerce site might have millions of product views (queries) for every purchase (command).
*   **Event Sourcing:**
    *   **Concept:** Persisting the state of a business object as a sequence of immutable events. The current state is derived by replaying the events.
    *   **Use Case:** Systems requiring a full audit trail or the ability to replay events to reconstruct state at any point in time. This is common in finance and banking applications.
*   **Microservices vs. The Modular Monolith:**
    *   **Concept:** A balanced comparison of distributed systems versus well-structured single-process applications. We will argue that for most projects, starting with a modular monolith is the more pragmatic choice.
    *   **Use Case:** Helping architects make informed decisions based on team size, domain complexity, and operational maturity.
*   **API Design Deep Dive:**
    *   **REST:** Best practices for building RESTful APIs, including versioning, pagination, and HATEOAS. We will also cover how to document REST APIs with OpenAPI.
    *   **gRPC:** A look at when to use gRPC for high-performance, low-latency communication between services. We will cover the topics of streaming, deadlines, and metadata.

## 8. The Polyglot Architecture Bridge

This section details how to effectively integrate Python and Go services, leveraging the strengths of each language to build a cohesive, high-performance system. We will focus on gRPC as the communication protocol and Protocol Buffers (Protobuf) as the interface definition language.

### 8.1. The "Why": Python for Brains, Go for Brawn

*   **Python's Strength:** Unparalleled ecosystem for data science, machine learning, and rapid prototyping. It's our choice for services that require complex calculations, data analysis, or ML model serving (the "Brains").
*   **Go's Strength:** Exceptional performance for concurrent I/O, networking, and CPU-intensive tasks that can be parallelized. It's our choice for high-throughput API gateways, data processors, and other performance-critical services (the "Brawn").

### 8.2. The "How": gRPC and Protocol Buffers

gRPC provides a high-performance, language-agnostic framework for remote procedure calls (RPCs). We use it for several key reasons:

*   **Performance:** gRPC uses HTTP/2 for transport and Protocol Buffers for serialization, which is significantly faster than JSON-over-HTTP.
*   **Streaming:** It supports client-side, server-side, and bidirectional streaming, enabling real-time communication patterns.
*   **Strongly-Typed Contracts:** By defining our service interfaces with Protobuf, we get a single source of truth for our data structures and service methods. This contract is used to auto-generate client and server code in both Python and Go, eliminating entire classes of integration errors.

### 8.3. Real-World Example: A Recommendation Service

Let's design a system where a Go-based API gateway provides user-facing product information, and it calls a Python-based recommendation service to get personalized product suggestions.

#### 8.3.1. The Protobuf Contract (`proto/recommendations.proto`)

First, we define the service contract. This `.proto` file is the single source of truth.

```protobuf
syntax = "proto3";

package recommendations;

option go_package = "gen/go/recommendations";

// The recommendation service definition.
service Recommender {
  // Retrieves a list of personalized product recommendations.
  rpc GetRecommendations(RecommendationRequest) returns (RecommendationResponse) {}
}

// The request message containing the user ID.
message RecommendationRequest {
  string user_id = 1;
  int32 max_results = 2;
}

// The response message containing a list of recommended product IDs.
message RecommendationResponse {
  repeated string product_ids = 1;
}
```

#### 8.3.2. The Python Service (The "Brains")

The Python service implements the `Recommender` interface. It's responsible for the complex logic of generating recommendations.

**Directory Structure:**

```text
recommendation_service/
├── pyproject.toml
├── src/
│   └── recommendations/
│       ├── main.py         # The gRPC server
│       ├── service.py      # The implementation of the Recommender service
│       └── ml_model.py     # The (pretend) ML model
└── proto/
    └── recommendations.proto
```

**`service.py` (Implementation):**

```python
# recommendations/service.py
from recommendations_pb2 import RecommendationResponse
from recommendations_pb2_grpc import RecommenderServicer

class RecommendationService(RecommenderServicer):
    def GetRecommendations(self, request, context):
        # In a real system, this would call a complex ML model
        # with the request.user_id.
        print(f"Received recommendation request for user: {request.user_id}")
        
        # Pretend we have some logic to get recommendations
        recommended_ids = [f"product_{i}" for i in range(request.max_results)]
        
        return RecommendationResponse(product_ids=recommended_ids)
```

#### 8.3.3. The Go Service (The "Brawn")

The Go service is a client of the Python gRPC service. It might be an API gateway that aggregates data from multiple sources.

**Directory Structure:**

```text
api_gateway/
├── go.mod
├── main.go                 # The main application
├── client/
│   └── recommendations.go  # The gRPC client for the recommendation service
└── proto/
    └── recommendations.proto
```

**`client/recommendations.go` (Client):**

```go
// client/recommendations.go
package client

import (
	"context"
	"log"

	"google.golang.org/grpc"
	"api_gateway/gen/go/recommendations"
)

type RecommendationClient struct {
	client recommendations.RecommenderClient
}

func NewRecommendationClient(conn *grpc.ClientConn) *RecommendationClient {
	return &RecommendationClient{
		client: recommendations.NewRecommenderClient(conn),
	}
}

func (c *RecommendationClient) GetRecommendations(ctx context.Context, userID string, maxResults int32) ([]string, error) {
	req := &recommendations.RecommendationRequest{
		UserId:     userID,
		MaxResults: maxResults,
	}

	res, err := c.client.GetRecommendations(ctx, req)
	if err != nil {
		log.Printf("Failed to get recommendations: %v", err)
		return nil, err
	}

	return res.ProductIds, nil
}
```

This approach creates a clean separation of concerns, allowing each service to be developed, scaled, and maintained independently, while the gRPC contract ensures they can communicate reliably and efficiently.

## 6. Tooling & Best Practices

This section will cover the tools and practices we recommend for building high-quality software.

*   **Linters and Formatters:**
    *   **Python:** `ruff` for ultra-fast linting and formatting, `mypy` for static type checking, and `black` for uncompromising code formatting.
    *   **Go:** `gofmt` for formatting, `golangci-lint` for a comprehensive and fast linter aggregator.
*   **Continuous Integration & Delivery (CI/CD):**
    *   **Principles:** We advocate for short-lived feature branches, automated testing on every commit, and automated deployments to staging and production.
    *   **Tools:** We will provide examples using `GitHub Actions`, but the principles can be applied to any CI/CD system.
*   **Observability (The Three Pillars):**
    *   **Logging:** Structured, machine-readable logs (e.g., JSON) are a must. We will use `structlog` for Python and `slog` for Go.
    *   **Metrics:** Instrumenting code with `Prometheus` to monitor key performance indicators (KPIs). We will show how to expose a `/metrics` endpoint.
    *   **Tracing:** Using `OpenTelemetry` to trace requests across service boundaries. We will demonstrate how to propagate trace context and export traces to `Jaeger`.
*   **Security First:**
    *   **SAST (Static Application Security Testing):** We use `Snyk` to scan our code for vulnerabilities. See the [Snyk Security Instructions](./.github/instructions/snyk_rules.instructions.md) for more details.
    *   **Dependency Scanning:** Automated scanning of dependencies for known vulnerabilities using `Snyk` or `dependabot`.
    *   **Secrets Management:** We will use `HashiCorp Vault` or a similar tool to manage secrets. We will demonstrate how to fetch secrets at runtime and not store them in environment variables.

## 7. Contribution Guidelines

This section provides clear instructions for how to contribute to the "Clean Code Cookbook." We welcome contributions from the community.

*   **Code Style:**
    *   **Python:** We follow `PEP 8` and use `black` for formatting. `ruff` is used for linting.
    *   **Go:** We follow the standard `gofmt` style. `golangci-lint` is used for linting.
*   **Commit Message Format:**
    *   We use the [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/) specification.
    *   **Example:**
        *   `feat(python): add chapter on structured logging with structlog`
        *   `fix(go): correct worker pool example`
        *   `docs(readme): update contribution guidelines`
*   **Pull Request (PR) Process:**
    1.  **Fork & Branch:** Fork the repository and create a new branch for your feature or bug fix.
    2.  **Develop:** Make your changes. Add new content, fix bugs, or improve existing examples.
    3.  **Test:** If you are adding code, ensure it is accompanied by tests. Run the existing test suite to make sure you haven't introduced any regressions.
    4.  **Lint:** Run the linters to ensure your code adheres to our style guidelines.
    5.  **Submit PR:** Submit a pull request with a clear description of the changes. Reference any related issues.
    6.  **Review:** The PR will be reviewed by at least one core contributor. We will provide feedback and may request changes.
*   **Code of Conduct:**
    *   We are committed to providing a welcoming and inclusive environment for all.
    *   All contributors are expected to adhere to the [Contributor Covenant Code of Conduct](https://www.contributor-covenant.org/version/2/1/code_of_conduct/). Any violations will be taken seriously.