from __future__ import annotations

from dataclasses import dataclass
from typing import List


@dataclass(slots=True)
class Inventory:
    available: int


@dataclass(slots=True)
class Price:
    currency: str
    amount: float


@dataclass(slots=True)
class Product:
    id: str
    inventory: Inventory
    price: Price
    reviews: List[str]
