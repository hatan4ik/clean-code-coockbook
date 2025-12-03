from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import Any

from ..domain.models import Inventory, Price


@dataclass(slots=True)
class InventoryHttpClient:
    http: Any  # expect an httpx.AsyncClient-like object

    async def get(self, product_id: str, *, timeout: float | None = None) -> Inventory:
        resp = await self.http.get(f"/inventory/{product_id}", timeout=timeout)
        resp.raise_for_status()
        data = resp.json()
        return Inventory(available=int(data["available"]))


@dataclass(slots=True)
class PricingHttpClient:
    http: Any

    async def get(self, product_id: str, *, timeout: float | None = None) -> Price:
        resp = await self.http.get(f"/pricing/{product_id}", timeout=timeout)
        resp.raise_for_status()
        data = resp.json()
        return Price(currency=data["currency"], amount=float(data["amount"]))


@dataclass(slots=True)
class ReviewsHttpClient:
    http: Any

    async def get(self, product_id: str, *, timeout: float | None = None) -> list[str]:
        resp = await self.http.get(f"/reviews/{product_id}", timeout=timeout)
        resp.raise_for_status()
        data = resp.json()
        # Safeguard against slow endpoints by streaming if supported; simplified here
        await asyncio.sleep(0)
        return [str(r) for r in data.get("reviews", [])]
