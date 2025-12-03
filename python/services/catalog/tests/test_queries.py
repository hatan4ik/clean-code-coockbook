import asyncio
import pytest

from python.services.catalog.domain.models import Inventory, Price
from python.services.catalog.service_layer.queries import (
    UpstreamTimeout,
    fetch_product,
)


class StubClient:
    def __init__(self, value, delay: float = 0.0, raises: Exception | None = None):
        self.value = value
        self.delay = delay
        self.raises = raises

    async def get(self, product_id: str, *, timeout: float | None = None):
        if self.delay and timeout and self.delay > timeout:
            # mimic upstream timeout
            await asyncio.sleep(timeout)
            raise asyncio.TimeoutError
        if self.delay:
            await asyncio.sleep(self.delay)
        if self.raises:
            raise self.raises
        return self.value


@pytest.mark.asyncio
async def test_fetch_product_happy_path():
    inv = StubClient(Inventory(available=3))
    price = StubClient(Price(currency="USD", amount=9.99))
    reviews = StubClient(["ok", "great"])

    product = await fetch_product(
        "p1", inventory=inv, pricing=price, reviews=reviews, timeout_seconds=0.2
    )

    assert product.id == "p1"
    assert product.inventory.available == 3
    assert product.price.amount == 9.99
    assert product.reviews == ["ok", "great"]


@pytest.mark.asyncio
async def test_fetch_product_timeout_bubbles():
    inv = StubClient(Inventory(available=3), delay=0.3)
    price = StubClient(Price(currency="USD", amount=9.99))
    reviews = StubClient(["ok"])

    with pytest.raises(UpstreamTimeout):
        await fetch_product(
            "p1", inventory=inv, pricing=price, reviews=reviews, timeout_seconds=0.1
        )
