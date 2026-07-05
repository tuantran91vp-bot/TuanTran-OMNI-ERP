"""Report data models."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal


@dataclass(frozen=True)
class ReportFilters:
    start_date: date | None = None
    end_date: date | None = None
    platform: str | None = None


@dataclass(frozen=True)
class ReportRow:
    order_date: date
    platform: str
    order_id: str
    internal_sku: str
    gross_revenue: Decimal
    amount_received: Decimal
    cost_of_goods_sold: Decimal
    profit: Decimal


@dataclass(frozen=True)
class Report:
    title: str
    filters: ReportFilters
    rows: list[ReportRow]
    total_orders: int
    total_revenue: Decimal
    total_amount_received: Decimal
    total_cost_of_goods_sold: Decimal
    total_profit: Decimal
