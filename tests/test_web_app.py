from pathlib import Path
import unittest


ROOT_DIR = Path(__file__).resolve().parents[1]
WEB_DIR = ROOT_DIR / "web"


class WebAppTests(unittest.TestCase):
    def test_web_app_files_exist(self) -> None:
        for path in [
            WEB_DIR / "index.html",
            WEB_DIR / "styles.css",
            WEB_DIR / "app.js",
            WEB_DIR / "assets" / "omni-logo.svg",
        ]:
            with self.subTest(path=path):
                self.assertTrue(path.exists())

    def test_web_app_contains_core_views(self) -> None:
        html = (WEB_DIR / "index.html").read_text(encoding="utf-8")

        for view_id in ["dashboard", "inventory", "orders", "reports", "operations"]:
            with self.subTest(view_id=view_id):
                self.assertIn(f'id="{view_id}"', html)

    def test_web_app_supports_local_storage_and_exports(self) -> None:
        javascript = (WEB_DIR / "app.js").read_text(encoding="utf-8")

        self.assertIn("localStorage", javascript)
        self.assertIn("downloadCsv", javascript)
        self.assertIn("downloadJson", javascript)
        self.assertIn("/api/import/orders", javascript)
        self.assertIn("X-Filename", javascript)
        self.assertIn("/api/state", javascript)
        self.assertIn("parseXlsx", javascript)
        self.assertIn("DecompressionStream", javascript)


if __name__ == "__main__":
    unittest.main()
