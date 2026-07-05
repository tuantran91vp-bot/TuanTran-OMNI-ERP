"""In-memory warehouse service for SKU and FIFO stock operations."""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from itertools import count

from .models import InventoryLot, Product, StockMovement, Warehouse, to_decimal


class UnknownSkuError(ValueError):
    """Raised when a stock operation references an unknown internal SKU."""


class UnknownWarehouseError(ValueError):
    """Raised when a stock operation references an unknown warehouse."""


class InsufficientStockError(ValueError):
    """Raised when FIFO issue quantity exceeds available stock."""


class WarehouseService:
    """Manage products, warehouses, stock receipts, issues, and balances."""

    def __init__(self) -> None:
        self.products: dict[str, Product] = {}
        self.warehouses: dict[str, Warehouse] = {}
        self.lots: list[InventoryLot] = []
        self.movements: list[StockMovement] = []
        self._movement_sequence = count(1)

    def add_product(self, product: Product) -> None:
        self.products[product.internal_sku] = product

    def add_warehouse(self, warehouse: Warehouse) -> None:
        self.warehouses[warehouse.warehouse_id] = warehouse

    def receive_stock(
        self,
        *,
        lot_id: str,
        warehouse_id: str,
        internal_sku: str,
        quantity: Decimal | int | str,
        unit_cost: Decimal | int | str,
        document_no: str,
        received_date: date,
        supplier_id: str | None = None,
    ) -> InventoryLot:
        self._ensure_known_stock_target(warehouse_id, internal_sku)
        received_qty = to_decimal(quantity)
        lot = InventoryLot(
            lot_id=lot_id,
            warehouse_id=warehouse_id,
            internal_sku=internal_sku,
            received_date=received_date,
            qty_received=received_qty,
            qty_available=received_qty,
            unit_cost=to_decimal(unit_cost),
            supplier_id=supplier_id,
        )
        movement = self._build_movement(
            movement_type="inbound",
            document_no=document_no,
            warehouse_id=warehouse_id,
            internal_sku=internal_sku,
            quantity=received_qty,
            movement_date=received_date,
            lot_id=lot_id,
            unit_cost=lot.unit_cost,
        )

        self.lots.append(lot)
        self.movements.append(movement)
        return lot

    def issue_stock_fifo(
        self,
        *,
        warehouse_id: str,
        internal_sku: str,
        quantity: Decimal | int | str,
        document_no: str,
        issued_date: date,
    ) -> list[StockMovement]:
        self._ensure_known_stock_target(warehouse_id, internal_sku)
        remaining_qty = to_decimal(quantity)
        if remaining_qty <= 0:
            raise ValueError("quantity must be positive")

        available_qty = self.stock_on_hand(warehouse_id=warehouse_id, internal_sku=internal_sku)
        if available_qty < remaining_qty:
            raise InsufficientStockError(
                f"insufficient stock for {internal_sku} in {warehouse_id}: "
                f"need {remaining_qty}, available {available_qty}"
            )

        outbound_movements: list[StockMovement] = []
        for lot in self._fifo_lots(warehouse_id, internal_sku):
            if remaining_qty == 0:
                break

            issue_qty = min(lot.qty_available, remaining_qty)
            lot.qty_available -= issue_qty
            remaining_qty -= issue_qty
            outbound_movements.append(
                self._build_movement(
                    movement_type="outbound",
                    document_no=document_no,
                    warehouse_id=warehouse_id,
                    internal_sku=internal_sku,
                    quantity=issue_qty,
                    movement_date=issued_date,
                    lot_id=lot.lot_id,
                    unit_cost=lot.unit_cost,
                )
            )

        self.movements.extend(outbound_movements)
        return outbound_movements

    def stock_on_hand(self, *, warehouse_id: str | None = None, internal_sku: str | None = None) -> Decimal:
        matching_lots = self.lots
        if warehouse_id is not None:
            matching_lots = [lot for lot in matching_lots if lot.warehouse_id == warehouse_id]
        if internal_sku is not None:
            matching_lots = [lot for lot in matching_lots if lot.internal_sku == internal_sku]
        return sum((lot.qty_available for lot in matching_lots), Decimal("0"))

    def _fifo_lots(self, warehouse_id: str, internal_sku: str) -> list[InventoryLot]:
        return sorted(
            [
                lot
                for lot in self.lots
                if lot.warehouse_id == warehouse_id
                and lot.internal_sku == internal_sku
                and lot.qty_available > 0
            ],
            key=lambda lot: (lot.received_date, lot.lot_id),
        )

    def _ensure_known_stock_target(self, warehouse_id: str, internal_sku: str) -> None:
        if warehouse_id not in self.warehouses:
            raise UnknownWarehouseError(f"unknown warehouse: {warehouse_id}")
        if internal_sku not in self.products:
            raise UnknownSkuError(f"unknown internal SKU: {internal_sku}")

    def _build_movement(
        self,
        *,
        movement_type: str,
        document_no: str,
        warehouse_id: str,
        internal_sku: str,
        quantity: Decimal,
        movement_date: date,
        lot_id: str | None,
        unit_cost: Decimal,
    ) -> StockMovement:
        movement_id = f"MOV-{next(self._movement_sequence):06d}"
        return StockMovement(
            movement_id=movement_id,
            movement_type=movement_type,
            document_no=document_no,
            warehouse_id=warehouse_id,
            internal_sku=internal_sku,
            quantity=quantity,
            movement_date=movement_date,
            lot_id=lot_id,
            unit_cost=unit_cost,
        )
