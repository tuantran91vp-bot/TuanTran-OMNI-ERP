from pathlib import Path
import sys
import tempfile
import unittest


ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT_DIR / "src"))

from omni_erp.web_state import read_state, write_state  # noqa: E402


class WebStateTests(unittest.TestCase):
    def test_read_missing_state_returns_empty_dict(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            self.assertEqual({}, read_state(tmp_dir))

    def test_write_and_read_state_uses_data_file(self) -> None:
        state = {
            "orders": [{"orderId": "SHP-1001", "revenue": 100000}],
            "inventory": [],
            "automations": [],
        }

        with tempfile.TemporaryDirectory() as tmp_dir:
            state_path = write_state(tmp_dir, state)
            loaded_state = read_state(tmp_dir)

        self.assertEqual(Path(tmp_dir) / "data" / "omni-data.json", state_path)
        self.assertEqual(state, loaded_state)


if __name__ == "__main__":
    unittest.main()
