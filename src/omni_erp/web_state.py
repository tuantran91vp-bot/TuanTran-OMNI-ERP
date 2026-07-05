"""Persistent JSON state for the local web app."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


DEFAULT_STATE_FILE = "data/omni-data.json"


def read_state(project_root: str | Path) -> dict[str, Any]:
    """Read persisted web app state from disk."""

    state_path = _state_path(project_root)
    if not state_path.exists():
        return {}
    return json.loads(state_path.read_text(encoding="utf-8"))


def write_state(project_root: str | Path, state: dict[str, Any]) -> Path:
    """Write web app state to disk."""

    state_path = _state_path(project_root)
    state_path.parent.mkdir(parents=True, exist_ok=True)
    state_path.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")
    return state_path


def _state_path(project_root: str | Path) -> Path:
    return Path(project_root).resolve() / DEFAULT_STATE_FILE
