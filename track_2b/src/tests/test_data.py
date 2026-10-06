"""Consistency checks over the shipped tasks (no Docker, no model)."""

from __future__ import annotations

import json
import os
import unittest
from pathlib import Path

from airpatch import proposal, propose
from airpatch.tasks import hidden_cases, list_tasks, start_files

DATA = Path(os.environ.get("AIRPATCH_DATA", Path(__file__).resolve().parents[2] / "data"))
MARK = "AIRPATCH" + "-CANARY-"


class TaskDataTests(unittest.TestCase):
    def test_every_task_loads_and_has_hidden_cases(self):
        tasks = list_tasks(DATA / "tasks")
        self.assertGreaterEqual(len(tasks), 4)
        for task in tasks:
            self.assertTrue(hidden_cases(DATA / "hidden", task.id), task.id)
            self.assertIn(task.entry, start_files(task), task.id)

    def test_public_task_files_contain_no_hidden_markers(self):
        for path in (DATA / "tasks").rglob("*"):
            if path.is_file():
                self.assertNotIn(MARK, path.read_text(encoding="utf-8"), str(path))

    def test_prompt_never_contains_hidden_data(self):
        for task in list_tasks(DATA / "tasks"):
            prompt = "\n".join(m["content"] for m in propose.build_messages(task))
            self.assertNotIn(MARK, prompt, task.id)
            for case_id in hidden_cases(DATA / "hidden", task.id):
                expected = (DATA / "hidden" / task.id / "cases" / f"{case_id}.out").read_text()
                # Short or empty expected outputs may coincide with visible examples.
                if len(expected.strip()) >= 12:
                    self.assertNotIn(expected.strip(), prompt, f"{task.id}/{case_id}")

    def test_mock_answers_parse_as_expected(self):
        expectations = json.loads((DATA / "mock" / "expectations.json").read_text())
        expectations.pop("repair_final", None)
        expectations.update({"sec-probe": "PASS", "sec-traversal": "POLICY_VIOLATION"})
        parse_status = {"MALFORMED_PROPOSAL": "MALFORMED_PROPOSAL", "POLICY_VIOLATION": "POLICY_VIOLATION"}
        tasks = {t.id: t for t in list_tasks(DATA / "tasks")
                 if t.kind == "security" or json.loads((t.public_dir / "task.json").read_text()).get("split") == "dev"}
        self.assertEqual(set(expectations), set(tasks), "every dev task needs a mock expectation")
        for task_id, verdict in expectations.items():
            text = (DATA / "mock" / f"{task_id}.md").read_text(encoding="utf-8")
            self.assertEqual(proposal.parse(text, tasks[task_id].editable).status,
                             parse_status.get(verdict, "OK"), task_id)

    def test_quick_subset_names_existing_benchmark_tasks(self):
        quick = [l for l in (DATA / "quick_tasks.txt").read_text().split() if not l.startswith("#")]
        benchmark = {t.id for t in list_tasks(DATA / "tasks", "benchmark")}
        self.assertTrue(quick)
        self.assertLessEqual(set(quick), benchmark)

if __name__ == "__main__":
    unittest.main()
