"""Backup archive creation."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile


DEFAULT_BACKUP_PATHS = (
    "config",
    "docs",
    "templates",
    "apps_script",
    "README.md",
    "pyproject.toml",
)


@dataclass(frozen=True)
class BackupManifest:
    archive_path: Path
    file_count: int
    created_at: datetime


def create_backup_archive(
    *,
    project_root: str | Path,
    output_path: str | Path,
    include_paths: tuple[str, ...] = DEFAULT_BACKUP_PATHS,
) -> BackupManifest:
    """Create a zip backup for deployable project assets."""

    root = Path(project_root)
    archive_path = Path(output_path)
    archive_path.parent.mkdir(parents=True, exist_ok=True)
    file_count = 0

    with ZipFile(archive_path, "w", compression=ZIP_DEFLATED) as archive:
        for include_path in include_paths:
            source = root / include_path
            if not source.exists():
                continue
            if source.is_file():
                archive.write(source, source.relative_to(root).as_posix())
                file_count += 1
                continue

            for file_path in sorted(path for path in source.rglob("*") if path.is_file()):
                archive.write(file_path, file_path.relative_to(root).as_posix())
                file_count += 1

    return BackupManifest(
        archive_path=archive_path,
        file_count=file_count,
        created_at=datetime.now(timezone.utc),
    )
