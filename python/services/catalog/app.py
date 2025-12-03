from __future__ import annotations

import asyncio
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel

from .adapters.http_clients import InventoryHttpClient, PricingHttpClient, ReviewsHttpClient
from .ports import InventoryClient, PricingClient, ReviewsClient
from .service_layer.queries import UpstreamTimeout, fetch_product

app = FastAPI(title="Catalog Service (Clean Code Cookbook)")


class ProductResponse(BaseModel):
    id: str
    inventory: int
    price: float
    currency: str
    reviews: list[str]


async def get_http_client():
    # Placeholder for an httpx.AsyncClient or similar
    import httpx

    async with httpx.AsyncClient(timeout=0.5) as client:
        yield client


async def get_inventory_client(
    http = Depends(get_http_client),
) -> InventoryClient:
    return InventoryHttpClient(http=http)


async def get_pricing_client(
    http = Depends(get_http_client),
) -> PricingClient:
    return PricingHttpClient(http=http)


async def get_reviews_client(
    http = Depends(get_http_client),
) -> ReviewsClient:
    return ReviewsHttpClient(http=http)


@app.get("/products/{product_id}", response_model=ProductResponse)
async def get_product(
    product_id: str,
    inventory: Annotated[InventoryClient, Depends(get_inventory_client)],
    pricing: Annotated[PricingClient, Depends(get_pricing_client)],
    reviews: Annotated[ReviewsClient, Depends(get_reviews_client)],
):
    try:
        product = await fetch_product(
            product_id,
            inventory=inventory,
            pricing=pricing,
            reviews=reviews,
            timeout_seconds=0.2,
        )
    except UpstreamTimeout as exc:
        raise HTTPException(status_code=504, detail=str(exc)) from exc

    return ProductResponse(
        id=product.id,
        inventory=product.inventory.available,
        price=product.price.amount,
        currency=product.price.currency,
        reviews=product.reviews,
    )


@app.on_event("startup")
async def on_startup() -> None:
    # Hook for warmups; left empty for brevity.
    await asyncio.sleep(0)
