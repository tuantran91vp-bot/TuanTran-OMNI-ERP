from pathlib import Path
import sys
import tempfile
import unittest
from zipfile import ZipFile


ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT_DIR / "src"))

from omni_erp.operations import (  # noqa: E402
    build_default_automation_plan,
    build_package_manifest,
    create_backup_archive,
)


class OperationsTests(unittest.TestCase):
    def test_default_automation_plan_contains_core_jobs(self) -> None:
        tasks = build_default_automation_plan()

        self.assertEqual(
            ["sync-marketplace-orders", "refresh-dashboard", "create-backup"],
            [task.task_id for task in tasks],
        )
        self.assertTrue(all(task.enabled for task in tasks))
        self.assertTrue(all("Asia/Saigon" in task.schedule for task in tasks))

    def test_package_manifest_is_complete_for_current_project(self) -> None:
        manifest = build_package_manifest(project_root=ROOT_DIR, version="0.1.0")

        self.assertEqual("0.1.0", manifest.version)
        self.assertTrue(manifest.is_complete)
        self.assertEqual((), manifest.missing_paths)

    def test_backup_archive_contains_operational_assets(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            archive_path = Path(tmp_dir) / "omni-backup.zip"
            manifest = create_backup_archive(project_root=ROOT_DIR, output_path=archive_path)

            with ZipFile(archive_path, "r") as archive:
                names = set(archive.namelist())

        self.assertGreater(manifest.file_count, 0)
        self.assertIn("README.md", names)
        self.assertIn("apps_script/Code.gs", names)
        self.assertIn("config/settings.example.json", names)
        self.assertIn("templates/google_sheets/products.csv", names)

    def test_apps_script_manifest_and_code_exist(self) -> None:
        manifest_path = ROOT_DIR / "apps_script" / "appsscript.json"
        code_path = ROOT_DIR / "apps_script" / "Code.gs"

        self.assertTrue(manifest_path.exists())
        self.assertTrue(code_path.exists())
        self.assertIn("OMNI ERP", code_path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
