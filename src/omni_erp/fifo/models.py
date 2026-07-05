"""FIFO engine result models."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from omni_erp.warehouse import StockMovement


@dataclass(frozen=True)
class FifoIssueResult:
    document_no: str
    platform: str
    order_id: str
    internal_sku: str
    inventory_quantity: Decimal
    movements: list[StockMovement]
    cost_of_goods_sold: Decimal
