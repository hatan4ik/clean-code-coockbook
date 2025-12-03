from __future__ import annotations

from typing import Protocol

from .domain.models import Inventory, Price


class InventoryClient(Protocol):
    async def get(self, product_id: str, *, timeout: float | None = None) -> Inventory: ...


class PricingClient(Protocol):
    async def get(self, product_id: str, *, timeout: float | None = None) -> Price: ...


class ReviewsClient(Protocol):
    async def get(self, product_id: str, *, timeout: float | None = None) -> list[str]: ...
