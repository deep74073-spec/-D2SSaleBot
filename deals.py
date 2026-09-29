"""
D2S Sale Bot - Deal Source
"""

from dataclasses import dataclass
from typing import List


@dataclass
class Deal:
    product: str
    price: str
    old_price: str
    link: str
    image_url: str


MIN_DISCOUNT = 20


def discount_percent(price: str, old_price: str) -> int:
    try:
        current = float(price.replace(",", "").replace("₹", "").strip())
        original = float(old_price.replace(",", "").replace("₹", "").strip())

        if original <= 0 or current >= original:
            return 0

        return round((original - current) / original * 100)
    except (ValueError, TypeError):
        return 0


def filter_deals(deals: List[Deal]) -> List[Deal]:
    return [
        deal for deal in deals
        if discount_percent(deal.price, deal.old_price) >= MIN_DISCOUNT
    ]


def fetch_deals() -> List[Deal]:
    # Official/approved deal source will be connected here.
    return []
