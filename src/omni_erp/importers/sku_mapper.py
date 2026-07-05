"""SKU mapping helpers."""

from __future__ import annotations

from decimal import Decimal

from .models import SkuMapping


class UnmappedSkuError(ValueError):
    """Raised when an import row cannot be linked to an internal SKU."""


class SkuMapper:
    """Resolve platform SKU values to internal warehouse SKU values."""

    def __init__(self, mappings: list[SkuMapping]) -> None:
        self._mappings: dict[tuple[str, str], SkuMapping] = {
            (mapping.platform.casefold(), mapping.platform_sku.casefold()): mapping
            for mapping in mappings
            if mapping.status == "active"
        }

    def resolve(self, platform: str, platform_sku: str) -> SkuMapping:
        key = (platform.casefold(), platform_sku.casefold())
        try:
            return self._mappings[key]
        except KeyError as exc:
            raise UnmappedSkuError(f"unmapped SKU for {platform}: {platform_sku}") from exc

    def inventory_quantity(self, platform: str, platform_sku: str, sold_quantity: Decimal) -> Decimal:
        mapping = self.resolve(platform, platform_sku)
        return sold_quantity * mapping.conversion_qty
