"""Packaging manifest helpers."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


PACKAGE_REQUIRED_PATHS = (
    "README.md",
    "pyproject.toml",
    "config/settings.example.json",
    "docs/roadmap.md",
    "docs/google-sheet-template.md",
    "templates/google_sheets/products.csv",
    "templates/google_sheets/sku_mapping.csv",
    "templates/google_sheets/warehouses.csv",
    "templates/google_sheets/suppliers.csv",
    "templates/google_sheets/inventory_lots.csv",
    "templates/google_sheets/settings.csv",
    "apps_script/appsscript.json",
    "apps_script/Code.gs",
    "web/index.html",
    "web/styles.css",
    "web/app.js",
    "web/assets/omni-logo.svg",
    "scripts/start-web.ps1",
    "scripts/check.ps1",
)


@dataclass(frozen=True)
class PackageManifest:
    version: str
    required_paths: tuple[str, ...]
    missing_paths: tuple[str, ...]

    @property
    def is_complete(self) -> bool:
        return not self.missing_paths


def build_package_manifest(*, project_root: str | Path, version: str) -> PackageManifest:
    """Validate package-ready assets exist."""

    root = Path(project_root)
    missing_paths = tuple(path for path in PACKAGE_REQUIRED_PATHS if not (root / path).exists())
    return PackageManifest(
        version=version,
        required_paths=PACKAGE_REQUIRED_PATHS,
        missing_paths=missing_paths,
    )
