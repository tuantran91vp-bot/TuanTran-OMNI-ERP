"""Warehouse domain models."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal


def to_decimal(value: Decimal | int | str) -> Decimal:
    """Convert numeric input to Decimal without float rounding surprises."""

    return value if isinstance(value, Decimal) else Decimal(str(value))


@dataclass(frozen=True)
class Product:
    product_id: str
    internal_sku: str
    product_name: str
    unit: str = "piece"
    status: str = "active"


@dataclass(frozen=True)
class Warehouse:
    warehouse_id: str
    warehouse_name: str
    warehouse_type: str = "main"
    status: str = "active"


@dataclass
class InventoryLot:
    lot_id: str
    warehouse_id: str
    internal_sku: str
    received_date: date
    qty_received: Decimal
    qty_available: Decimal
    unit_cost: Decimal
    supplier_id: str | None = None

    def __post_init__(self) -> None:
        self.qty_received = to_decimal(self.qty_received)
        self.qty_available = to_decimal(self.qty_available)
        self.unit_cost = to_decimal(self.unit_cost)

        if self.qty_received < 0:
            raise ValueError("qty_received must be non-negative")
        if self.qty_available < 0:
            raise ValueError("qty_available must be non-negative")
        if self.qty_available > self.qty_received:
            raise ValueError("qty_available cannot exceed qty_received")
        if self.unit_cost < 0:
            raise ValueError("unit_cost must be non-negative")


@dataclass(frozen=True)
class StockMovement:
    movement_id: str
    movement_type: str
    document_no: str
    warehouse_id: str
    internal_sku: str
    quantity: Decimal
    movement_date: date
    lot_id: str | None = None
    unit_cost: Decimal | None = None

    def __post_init__(self) -> None:
        object.__setattr__(self, "quantity", to_decimal(self.quantity))
        if self.unit_cost is not None:
            object.__setattr__(self, "unit_cost", to_decimal(self.unit_cost))

        if self.movement_type not in {"inbound", "outbound", "return", "adjustment"}:
            raise ValueError("movement_type must be inbound, outbound, return, or adjustment")
        if self.quantity <= 0:
            raise ValueError("quantity must be positive")
