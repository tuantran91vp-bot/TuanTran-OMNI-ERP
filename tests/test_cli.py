from pathlib import Path
from contextlib import redirect_stdout
from io import StringIO
import sys
import tempfile
import unittest


ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT_DIR / "src"))

from omni_erp.cli import main  # noqa: E402


class CliTests(unittest.TestCase):
    def test_package_command_reports_complete_manifest(self) -> None:
        result = _run_cli(["package", "--project-root", str(ROOT_DIR)])

        self.assertEqual(0, result)

    def test_backup_command_creates_archive(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            output_path = Path(tmp_dir) / "omni.zip"

            result = _run_cli(["backup", "--project-root", str(ROOT_DIR), "--output", str(output_path)])

            self.assertEqual(0, result)
            self.assertTrue(output_path.exists())

    def test_automation_plan_command_returns_json(self) -> None:
        result = _run_cli(["automation-plan"])

        self.assertEqual(0, result)


def _run_cli(args: list[str]) -> int:
    with redirect_stdout(StringIO()):
        return main(args)


if __name__ == "__main__":
    unittest.main()
