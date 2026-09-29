"""
D2S Sale Bot - Deal Source

The source adapter accepts an authorized JSON feed. It does not scrape
Amazon pages or bypass Amazon access controls.

Configure DEAL_SOURCE_URL in .env when an approved/authorized feed is
available. The feed must return either a JSON list or:
{"deals": [{...}]}

Each deal needs:
product, price, old_price, link, image_url
"""

from dataclasses import dataclass
from pathlib import Path
from typing import List
import hashlib
import json
import os

import httpx


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
            str(price).replace(",", "").replace("₹", "").strip()
        )
        original = float(
            str(old_price).replace(",", "").replace("₹", "").strip()
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
        data = json.loads(path.read_text())
        return set(data) if isinstance(data, list) else set()
    except (json.JSONDecodeError, OSError):
        return set()


def save_seen(seen: set) -> None:
    Path(SEEN_FILE).write_text(
        json.dumps(sorted(seen), indent=2)
    )


def mark_seen(deal: Deal) -> None:
    seen = load_seen()
    seen.add(deal_key(deal))
    save_seen(seen)


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
    """
    Return only unseen deals without saving them yet.

    A deal is marked seen only after Telegram confirms the post succeeded.
    This allows failed posts to be retried on the next scheduler run.
    """
    seen = load_seen()
    fresh = []
    batch_seen = set()

    for deal in deals:
        key = deal_key(deal)

        if key not in seen and key not in batch_seen:
            fresh.append(deal)
            batch_seen.add(key)

    return fresh


def _deal_from_dict(item: dict) -> Deal | None:
    required = (
        "product",
        "price",
        "old_price",
        "link",
        "image_url",
    )

    if (
        not isinstance(item, dict)
        or any(
            not str(item.get(key, "")).strip()
            for key in required
        )
    ):
        return None

    return Deal(
        product=str(item["product"]).strip(),
        price=str(item["price"]).strip(),
        old_price=str(item["old_price"]).strip(),
        link=str(item["link"]).strip(),
        image_url=str(item["image_url"]).strip(),
    )


def fetch_deals() -> List[Deal]:
    """
    Fetch deals from an authorized JSON feed.

    Set DEAL_SOURCE_URL in .env only for a source you are
    authorized to use.

    If it is not configured, automatic posting stays disabled.
    """

    source_url = os.getenv("DEAL_SOURCE_URL", "").strip()

    if not source_url:
        return []

    try:
        response = httpx.get(
            source_url,
            timeout=15.0,
            follow_redirects=True,
        )
        response.raise_for_status()
        payload = response.json()

    except (httpx.HTTPError, ValueError) as exc:
        print(f"Deal source fetch failed: {exc}")
        return []

    items = (
        payload.get("deals", [])
        if isinstance(payload, dict)
        else payload
    )

    if not isinstance(items, list):
        print("Deal source returned an invalid JSON format.")
        return []

    deals = []

    for item in items:
        deal = _deal_from_dict(item)

        if deal:
            deals.append(deal)

    return deals
