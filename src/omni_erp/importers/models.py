"""Normalized marketplace import models."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal


@dataclass(frozen=True)
class SkuMapping:
    platform: str
    platform_sku: str
    internal_sku: str
    conversion_qty: Decimal = Decimal("1")
    status: str = "active"


@dataclass(frozen=True)
class NormalizedOrderLine:
    platform: str
    order_id: str
    order_date: date
    platform_sku: str
    internal_sku: str
    quantity: Decimal
    inventory_quantity: Decimal
    gross_amount: Decimal
    discount_amount: Decimal
    shipping_fee: Decimal
    buyer_paid_amount: Decimal
    currency: str
    raw_status: str
