### Directory Templates

#### Python (FastAPI/asyncio)
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

### Sample Flow (Python)
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
