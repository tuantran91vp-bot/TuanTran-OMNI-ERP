from pathlib import Path
import sys
import unittest


ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT_DIR / "src"))

from omni_erp.foundation import REQUIRED_SHEETS, validate_template_directory

TEMPLATE_DIR = ROOT_DIR / "templates" / "google_sheets"


class FoundationTemplateTests(unittest.TestCase):
    def test_all_required_google_sheet_templates_exist(self) -> None:
        for file_name in REQUIRED_SHEETS:
            with self.subTest(file_name=file_name):
                self.assertTrue((TEMPLATE_DIR / file_name).exists())

    def test_google_sheet_templates_match_expected_headers(self) -> None:
        errors = validate_template_directory(TEMPLATE_DIR)
        self.assertEqual([], errors)


if __name__ == "__main__":
    unittest.main()
