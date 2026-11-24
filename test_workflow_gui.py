import json
import tempfile
import unittest
from pathlib import Path

from workflow_gui import execute_workflow


class WorkflowGuiTests(unittest.TestCase):
    def test_default_style_dry_run_does_not_write_output(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            config = root / "workflow.json"
            output = root / "created.txt"
            config.write_text(json.dumps({
                "base_dir": str(root),
                "workflow": [{"action": "write_text", "path": output.name, "text": "synthetic"}],
            }), encoding="utf-8")
            result = execute_workflow(config, dry_run=True)
            self.assertIn('"dry_run": true', result)
            self.assertFalse(output.exists())

    def test_execution_applies_synthetic_write(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            config = root / "workflow.json"
            output = root / "created.txt"
            config.write_text(json.dumps({
                "base_dir": str(root),
                "workflow": [{"action": "write_text", "path": output.name, "text": "synthetic"}],
            }), encoding="utf-8")
            execute_workflow(config, dry_run=False)
            self.assertEqual(output.read_text(encoding="utf-8"), "synthetic")


if __name__ == "__main__":
    unittest.main()
