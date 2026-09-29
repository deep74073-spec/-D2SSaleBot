"""
D2S Sale Bot - Deal Source

This module will provide deals to the Telegram bot.
Amazon Creators API can be connected here once API access is approved.
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


def fetch_deals() -> List[Deal]:
    """
    Return available deals.

    Currently returns an empty list because the Amazon
    Creators API is not yet available for this account.
    """
    return []
