"""Automation planning for recurring OMNI ERP jobs."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class AutomationTask:
    task_id: str
    name: str
    schedule: str
    action: str
    enabled: bool = True


def build_default_automation_plan() -> list[AutomationTask]:
    """Return the default operational automation plan."""

    return [
        AutomationTask(
            task_id="sync-marketplace-orders",
            name="Sync marketplace orders",
            schedule="daily 07:00 Asia/Saigon",
            action="Import Shopee, TikTok Shop, and Lazada orders into normalized rows.",
        ),
        AutomationTask(
            task_id="refresh-dashboard",
            name="Refresh dashboard",
            schedule="daily 07:15 Asia/Saigon",
            action="Rebuild KPI, inventory, revenue, and profit summaries.",
        ),
        AutomationTask(
            task_id="create-backup",
            name="Create backup",
            schedule="daily 23:30 Asia/Saigon",
            action="Archive configuration, templates, Apps Script, and docs.",
        ),
    ]
