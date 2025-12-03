### Python asyncio solution
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

### Patterns and Guardrails
- Prefer `asyncio.TaskGroup` (Python 3.11+) over `gather` for better error propagation.
- Avoid blocking calls inside async code (`time.sleep`, synchronous HTTP clients). Use `asyncio.to_thread` or process pools for CPU‑heavy tasks.
