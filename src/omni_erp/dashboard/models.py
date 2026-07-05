"""Dashboard data models."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal


@dataclass(frozen=True)
class DashboardOrderMetric:
    order_date: date
    platform: str
    order_id: str
    internal_sku: str
    gross_revenue: Decimal
    amount_received: Decimal
    cost_of_goods_sold: Decimal
    profit: Decimal


@dataclass(frozen=True)
class InventorySnapshot:
    warehouse_id: str
    internal_sku: str
    quantity_available: Decimal
    inventory_value: Decimal


@dataclass(frozen=True)
class ChartPoint:
    label: str
    revenue: Decimal
    profit: Decimal
    orders: int


@dataclass(frozen=True)
class DashboardSummary:
    total_orders: int
    total_revenue: Decimal
    total_amount_received: Decimal
    total_cost_of_goods_sold: Decimal
    total_profit: Decimal
    total_stock_quantity: Decimal
    total_inventory_value: Decimal
    revenue_by_platform: dict[str, Decimal]
    profit_by_platform: dict[str, Decimal]
    stock_by_warehouse: dict[str, Decimal]
    stock_by_sku: dict[str, Decimal]
    chart_by_date: list[ChartPoint]
