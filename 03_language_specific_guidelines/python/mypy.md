# Strict Typing & Data Contracts (Problem → Solution)

Mindset shift: move from “it runs” scripting to contract-first engineering. Strict typing plus runtime-validated data models eradicate the `AttributeError: 'NoneType' object has no attribute 'x'` class of bugs and make refactors safe.

## Problem: Dynamic Drift

- Hidden `None`s and shape changes leak to prod (runtime crashes, bad data persisted).
- Refactors are risky: no contracts to catch broken call sites.
- Tooling and IDE assistance are weak without types.

## Solution: Compile-Time + Runtime Contracts

- **mypy in strict mode** guards call sites, optionality, and API drift.
- **Pydantic models** validate/normalize external inputs (HTTP/DB/queue) at runtime and expose typed, immutable value objects.
- **Protocols** express ports; concrete adapters must satisfy them (structural typing).

## Minimal “Hello, Strict” Example

```python
from typing import Protocol
from pydantic import BaseModel

class Inventory(Protocol):
    async def get(self, product_id: str) -> int: ...

class ProductIn(BaseModel):
    id: str
    quantity: int

async def reserve(inv: Inventory, payload: ProductIn) -> None:
    current = await inv.get(payload.id)
    if payload.quantity > current:
        raise ValueError("Insufficient stock")
```

- mypy enforces `Inventory.get` signature and `ProductIn` attributes.
- Pydantic rejects malformed payloads before domain logic runs.

## Guardrails (Strict mypy defaults)

Put this in `pyproject.toml` or `mypy.ini` to set the tone repo-wide.

```ini
[mypy]
python_version = 3.11
strict = true
warn_unused_ignores = true
warn_return_any = true
warn_redundant_casts = true
disallow_untyped_calls = true
disallow_untyped_defs = true
disallow_incomplete_defs = true
disallow_untyped_decorators = true
no_implicit_optional = true
```

- Allow narrow opt-outs via per-module overrides; never disable strict globally.

## Real-World Bug Catch

```python
from typing import Optional

def notify_user(email: Optional[str]) -> None:
    send_email(email, "Your order shipped!")  # mypy error: Optional[str]
```

- Fix with explicit guard or by requiring non-optional input:

```python
def notify_user(email: str) -> None:
    send_email(email, "Your order shipped!")
```

## Migration Playbook (Zero → Hero)

1) **Turn on strict** with type stubs; start with leaf modules, then core.
2) **Model inputs**: wrap external payloads in Pydantic models; forbid `dict` passing.
3) **Define ports** as `Protocol` interfaces; have adapters satisfy them.
4) **Kill `Any`**: forbid implicit `Any`; tighten `Optional` handling.
5) **Wire CI**: gate on `ruff check`, `ruff format`, `mypy --strict`, `pytest -q`.
6) **Measure**: track type coverage; budget time each sprint to burn down ignores.

## CI Snippet

```yaml
- name: Lint & typecheck
  run: |
    ruff check .
    ruff format --check .
    mypy --strict .
```

## Success Criteria

- Zero implicit `Any`; optionality handled explicitly.
- All external inputs validated/normalized via Pydantic before domain use.
- Ports defined as protocols; adapters type-check without casts.
- Refactors rely on type errors, not runtime incidents.
