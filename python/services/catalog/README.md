# Catalog Reference (Python)

Purpose: a runnable slice that demonstrates strict typing, Pydantic contracts, async fan-out with timeouts/cancellation, and hexagonal separation (ports/adapters vs domain).

## What’s here
- `domain/`: pure models.
- `ports.py`: contracts for upstream clients.
- `service_layer/queries.py`: `fetch_product` use case with `asyncio.TaskGroup`.
- `adapters/http_clients.py`: example async clients using `httpx` semantics.
- `tests/test_queries.py`: pytest-asyncio fan-out test with stub clients.

## How to run tests (example)
```bash
python -m pip install pytest pytest-asyncio
pytest python/services/catalog/tests -q
```

## Key takeaways
- Pydantic (optional) for request/response DTOs; mypy enforces port contracts.
- Deadlines enforced at call sites; cancellation propagates across tasks.
- Domain is framework-free; adapters are swappable.
