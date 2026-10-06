"""The repair-round feedback must never carry hidden test data."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from airpatch import feedback, security
from airpatch.tasks import load_task

SECRET = "HIDDEN-SECRET-4711"


class FeedbackTests(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        root = self.tmp / "tasks" / "demo"
        (root / "start").mkdir(parents=True)
        (root / "visible").mkdir()
        (root / "start" / "main.py").write_text("print(input())\n")
        (root / "SPEC.md").write_text("Echo the input.\n")
        (root / "visible" / "01.in").write_text("hello\n")
        (root / "visible" / "01.out").write_text("hello\n")
        (root / "task.json").write_text(json.dumps({
            "id": "demo", "kind": "benchmark", "entry": "main.py", "editable": ["main.py"],
            "time_limit_s": 5, "mem_limit_mb": 64}))
        self.task = load_task(self.tmp / "tasks", "demo")
        cases = self.tmp / "hidden" / "demo" / "cases"
        cases.mkdir(parents=True)
        (cases / "01.in").write_text(SECRET + "-input\n")
        (cases / "01.out").write_text(SECRET + "-expected\n")

    def verdict(self):
        return {"task": "demo", "candidate": "c0", "verdict": "FAIL_TESTS", "cases_passed": 0,
                "cases_total": 1, "detail": None,
                # A hidden case whose error output echoes the hidden input.
                "cases": [{"case": "01", "status": "FAIL_TESTS", "reason": "wrong output",
                           "stderr_last_line": SECRET + "-input", "stderr_fingerprint": "x"}],
                "visible": [{"case": "v01", "status": "FAIL_TESTS", "reason": "wrong output",
                             "stdout": "HELLO\n", "stderr_tail": ""}]}

    def test_feedback_has_counts_and_visible_details_only(self):
        fb = feedback.build(self.verdict(), {"status": "APPLIED"}, self.task)
        text = json.dumps(fb) + feedback.message(fb)
        self.assertNotIn(SECRET, text)
        self.assertEqual(fb["hidden_passed"], 0)
        self.assertEqual(fb["hidden_failures"], {"wrong output": 1})
        self.assertIn("HELLO", feedback.message(fb))  # visible output is allowed

    def test_leak_scan_finds_planted_hidden_string(self):
        fb_dir = self.tmp / "feedback" / "demo"
        fb_dir.mkdir(parents=True)
        (fb_dir / "c0.json").write_text(json.dumps({"note": SECRET + "-expected"}))
        result = security.feedback_leaks(self.tmp / "feedback", self.tmp / "tasks", self.tmp / "hidden")
        self.assertEqual(len(result["leaks"]), 1)
        (fb_dir / "c0.json").write_text(json.dumps(
            feedback.build(self.verdict(), {"status": "APPLIED"}, self.task)))
        self.assertEqual(security.feedback_leaks(self.tmp / "feedback", self.tmp / "tasks",
                                                 self.tmp / "hidden")["leaks"], [])


if __name__ == "__main__":
    unittest.main()
