from __future__ import annotations

import asyncio
from asyncio import TaskGroup, TimeoutError

from ..domain.models import Product
from ..ports import InventoryClient, PricingClient, ReviewsClient


class UpstreamTimeout(RuntimeError):
    """Raised when any upstream exceeds its deadline."""


async def fetch_product(
    product_id: str,
    *,
    inventory: InventoryClient,
    pricing: PricingClient,
    reviews: ReviewsClient,
    timeout_seconds: float = 0.2,
) -> Product:
    """
    Fan-out to three upstreams with a shared deadline.
    Cancels siblings on timeout and bubbles a typed error.
    """
    try:
        async with TaskGroup() as tg:
            inv_task = tg.create_task(inventory.get(product_id, timeout=timeout_seconds))
            price_task = tg.create_task(pricing.get(product_id, timeout=timeout_seconds))
            reviews_task = tg.create_task(reviews.get(product_id, timeout=timeout_seconds))
    except (TimeoutError, ExceptionGroup) as exc:
        # Python 3.11+ wraps TimeoutError in ExceptionGroup when using TaskGroup
        if isinstance(exc, ExceptionGroup):
            # Check if any sub-exception is TimeoutError
            for sub_exc in exc.exceptions:
                if isinstance(sub_exc, (TimeoutError, asyncio.TimeoutError)):
                    raise UpstreamTimeout("Upstream timed out") from exc
            # Re-raise if it's not a timeout
            raise
        raise UpstreamTimeout("Upstream timed out") from exc

    inv = await inv_task
    price = await price_task
    revs = await reviews_task

    return Product(id=product_id, inventory=inv, price=price, reviews=revs or [])
