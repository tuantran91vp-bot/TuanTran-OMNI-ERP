"""OMNI ERP command line interface."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

from omni_erp import __version__
from omni_erp.operations import build_default_automation_plan, build_package_manifest, create_backup_archive


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    return args.handler(args)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="omni-erp", description="OMNI ERP operations toolkit")
    parser.add_argument("--version", action="version", version=f"OMNI ERP {__version__}")
    subparsers = parser.add_subparsers(dest="command", required=True)

    check_parser = subparsers.add_parser("check", help="Run unit tests and Python compile checks")
    check_parser.add_argument("--project-root", default=".", help="Project root directory")
    check_parser.set_defaults(handler=_handle_check)

    package_parser = subparsers.add_parser("package", help="Validate package-ready files")
    package_parser.add_argument("--project-root", default=".", help="Project root directory")
    package_parser.set_defaults(handler=_handle_package)

    backup_parser = subparsers.add_parser("backup", help="Create a deployable backup zip")
    backup_parser.add_argument("--project-root", default=".", help="Project root directory")
    backup_parser.add_argument("--output", required=True, help="Output zip path")
    backup_parser.set_defaults(handler=_handle_backup)

    automation_parser = subparsers.add_parser("automation-plan", help="Print default automation plan as JSON")
    automation_parser.set_defaults(handler=_handle_automation_plan)

    return parser


def _handle_check(args: argparse.Namespace) -> int:
    project_root = Path(args.project_root).resolve()
    commands = [
        [sys.executable, "-m", "unittest", "discover", "-s", "tests"],
        [sys.executable, "-m", "compileall", "src", "tests"],
    ]
    for command in commands:
        completed = subprocess.run(command, cwd=project_root, check=False)
        if completed.returncode != 0:
            return completed.returncode
    return 0


def _handle_package(args: argparse.Namespace) -> int:
    manifest = build_package_manifest(project_root=args.project_root, version=__version__)
    payload = {
        "version": manifest.version,
        "is_complete": manifest.is_complete,
        "missing_paths": list(manifest.missing_paths),
        "required_paths": list(manifest.required_paths),
    }
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if manifest.is_complete else 1


def _handle_backup(args: argparse.Namespace) -> int:
    manifest = create_backup_archive(project_root=args.project_root, output_path=args.output)
    payload = {
        "archive_path": str(manifest.archive_path),
        "created_at": manifest.created_at.isoformat(),
        "file_count": manifest.file_count,
    }
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


def _handle_automation_plan(_: argparse.Namespace) -> int:
    tasks = build_default_automation_plan()
    payload = [
        {
            "task_id": task.task_id,
            "name": task.name,
            "schedule": task.schedule,
            "action": task.action,
            "enabled": task.enabled,
        }
        for task in tasks
    ]
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0
