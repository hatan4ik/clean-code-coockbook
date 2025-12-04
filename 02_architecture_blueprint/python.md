### Directory Structure Explained

A well-defined directory structure is crucial for maintaining a clean and scalable codebase. It separates concerns, making it easier to find code, understand its purpose, and test it in isolation.

```text
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

- **`app.py`**: The entry point of your service. This is where you instantiate your FastAPI application, wire up your routes, and configure dependency injection. It should be kept minimal and focused on application assembly.

- **`config.py`**: Defines the application's configuration using Pydantic settings. This allows you to leverage environment variables and `.env` files for configuration, and get type-safe validation for free.

- **`domain/`**: This is the heart of your application. It contains the core business logic, models, and rules.
  - **`models.py`**: Defines your domain entities and value objects. These are plain Python objects (or Pydantic models/dataclasses) that represent the concepts of your domain. They should not contain any infrastructure-related code.
  - **`events.py`**: Defines the domain events that are raised when something significant happens in your domain.
  - **`services.py`**: Contains the domain services, which orchestrate the domain logic. These services should be pure and have no knowledge of the outside world (e.g., no database calls, no API requests).

- **`adapters/`**: This is where you implement the outbound ports. Adapters are responsible for interacting with external systems like databases, message brokers, and other APIs.
  - **`repositories.py`**: Implements the repository pattern for data access. It translates domain objects into database records and vice versa.
  - **`messaging.py`**: Implements the logic for sending and receiving messages from a message broker.
  - **`http_clients.py`**: Contains the clients for interacting with other HTTP services.

- **`ports/`**: Defines the inbound and outbound ports of your application. Ports are interfaces (or abstract base classes in Python) that define the contract between your application and the outside world.
  - **`repository.py`**: Defines the repository interface. The domain services will depend on this interface, not on the concrete implementation in the `adapters` layer.
  - **`notifier.py`**: Defines an interface for sending notifications.

- **`service_layer/`**: This layer orchestrates the application's use cases.
  - **`unit_of_work.py`**: Implements the Unit of Work pattern, which ensures that all database operations within a single use case are executed in a single transaction.
  - **`handlers.py`**: Contains the use case handlers. Each handler is responsible for a single use case, and it orchestrates the domain services and repositories to achieve the desired outcome.

- **`tests/`**: Contains the tests for your application.
  - **`unit/`**: Unit tests for your domain logic and services. These tests should be fast and have no external dependencies.
  - **`integration/`**: Integration tests for your adapters. These tests will interact with real external systems (e.g., a test database).
  - **`e2e/`**: End-to-end tests that test the entire application, from the API endpoints to the database.

### Sample Flow Explained

The sample flow demonstrates how a use case is executed within the hexagonal architecture.

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

1. **`fetch_product`**: This is a use case handler that takes a command (`FetchProduct`) and a `UnitOfWork` as input.
2. **`UnitOfWork`**: The `UnitOfWork` (uow) is a dependency that is injected into the handler. It provides access to the repositories and manages the transaction.
3. **`async with uow`**: The `async with` statement ensures that the transaction is automatically committed or rolled back when the block is exited.
4. **`uow.products.get(...)`**: The handler uses the product repository to fetch the product from the database.
5. **`asyncio.gather(...)`**: The handler then fetches the inventory and pricing information concurrently using `asyncio.gather`. This is a good example of how to leverage asyncio to improve performance.
6. **`ProductDTO.from_domain(product)`**: Finally, the handler converts the domain object into a Data Transfer Object (DTO) before returning it. This is important to avoid leaking domain objects to the outside world.

### Dependency Injection in FastAPI

FastAPI has a powerful dependency injection system that makes it easy to wire up your application. You can use it to inject dependencies into your route handlers, and FastAPI will take care of creating and managing the dependencies for you.

Here's an example of how you can use dependency injection to provide a `UnitOfWork` to your route handlers:

```python
# app.py
from fastapi import Depends, FastAPI
from .service_layer.unit_of_work import UnitOfWork

app = FastAPI()

def get_uow():
    # This is a simplified example. In a real application, you would
    # get the UoW from a dependency injection container.
    return UnitOfWork()

@app.get("/products/{product_id}")
async def get_product(product_id: str, uow: UnitOfWork = Depends(get_uow)):
    # ...
```

In this example, the `get_uow` function is a dependency that provides a `UnitOfWork`. The `Depends` function tells FastAPI that the `uow` parameter of the `get_product` function depends on the `get_uow` function. When a request comes in for `/products/{product_id}`, FastAPI will call the `get_uow` function and inject the returned `UnitOfWork` into the `get_product` function.
