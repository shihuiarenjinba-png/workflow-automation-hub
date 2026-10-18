import tempfile
import unittest
from pathlib import Path

from workflow_rules import RuleError, evaluate_rules
from workflow_hub import Runner


class RuleTests(unittest.TestCase):
    def test_trigger_skips_without_actions(self):
        with tempfile.TemporaryDirectory() as name:
            base = Path(name)
            cfg = {"base_dir": str(base), "trigger": {"type": "file_exists",
                   "path": "missing.csv"}, "workflow": [
                   {"action": "write_text", "path": "output.txt", "text": "NO"}]}
            Runner(cfg).run()
            self.assertFalse((base / "output.txt").exists())

    def test_trigger_and_text_condition(self):
        with tempfile.TemporaryDirectory() as name:
            base = Path(name)
            (base / "data.txt").write_text("approved", encoding="utf-8")
            cfg = {"trigger": {"type": "file_exists", "path": "data.txt"},
                   "conditions": [{"type": "text_contains", "path": "data.txt", "text": "approved"}]}
            self.assertEqual(evaluate_rules(cfg, base), (True, "eligible"))
            cfg["conditions"][0]["text"] = "declined"
            self.assertEqual(evaluate_rules(cfg, base), (False, "condition_1_not_met"))

    def test_invalid_later_condition_not_hidden_by_missing_trigger(self):
        with tempfile.TemporaryDirectory() as name:
            cfg = {"trigger": {"type": "file_exists", "path": "missing"},
                   "conditions": [{"type": "text_contains", "path": "x", "text": ""}]}
            with self.assertRaises(RuleError):
                evaluate_rules(cfg, Path(name))

    def test_reject_escape(self):
        with tempfile.TemporaryDirectory() as name:
            with self.assertRaises(RuleError):
                evaluate_rules({"trigger": {"type": "file_exists", "path": "../outside"}}, Path(name))
            with self.assertRaises(RuleError):
                evaluate_rules({"conditions": [{"type": "text_contains", "path": "x", "text": ""}]}, Path(name))


if __name__ == "__main__":
    unittest.main()
