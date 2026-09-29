"""
D2S Sale Bot - Deal Source

The fetch_deals() function is intentionally kept as the integration point
for an approved/authorized deal source.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import List
import hashlib
import json


@dataclass
class Deal:
    product: str
    price: str
    old_price: str
    link: str
    image_url: str


MIN_DISCOUNT = 20
SEEN_FILE = "seen_deals.json"


def discount_percent(price: str, old_price: str) -> int:
    try:
        current = float(
            price.replace(",", "").replace("₹", "").strip()
        )
        original = float(
            old_price.replace(",", "").replace("₹", "").strip()
        )

        if original <= 0 or current >= original:
            return 0

        return round((original - current) / original * 100)

    except (ValueError, TypeError):
        return 0


def deal_key(deal: Deal) -> str:
    raw = f"{deal.product}|{deal.link}".encode()
    return hashlib.sha256(raw).hexdigest()


def load_seen() -> set:
    path = Path(SEEN_FILE)

    if not path.exists():
        return set()

    try:
        return set(json.loads(path.read_text()))
    except (json.JSONDecodeError, OSError):
        return set()


def save_seen(seen: set) -> None:
    Path(SEEN_FILE).write_text(
        json.dumps(sorted(seen), indent=2)
    )


def filter_deals(deals: List[Deal]) -> List[Deal]:
    return [
        deal
        for deal in deals
        if discount_percent(
            deal.price,
            deal.old_price
        ) >= MIN_DISCOUNT
    ]


def remove_duplicates(deals: List[Deal]) -> List[Deal]:
    seen = load_seen()
    fresh = []

    for deal in deals:
        key = deal_key(deal)

        if key not in seen:
            fresh.append(deal)
            seen.add(key)

    save_seen(seen)
    return fresh


def fetch_deals() -> List[Deal]:
    """
    Integration point for the real deal source.

    Do not scrape Amazon pages or bypass Amazon access controls here.
    When an approved/authorized API or feed is available, convert its
    results into Deal objects and return them.
    """

    return []
