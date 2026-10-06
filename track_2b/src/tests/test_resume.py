"""Resume of an interrupted propose step (post-evaluation hardening).

Before the fix, the launcher treated a whole step as done as soon as any one task had its
answer on disk (``ls proposals/*/c0.json``), so tasks without an answer were silently
dropped. Now ``propose.run(..., resume=True)`` keeps every answer already on disk and asks
exactly the missing ones. Calls are counted at the HTTP stub, not inferred.
"""

from __future__ import annotations

import json
import tempfile
import threading
import unittest
from http.server import ThreadingHTTPServer
from pathlib import Path

from airpatch import mockllm, propose

N = 4
TASKS = [f"t{i}" for i in range(1, N + 1)]


class _Stub:
    """Local mock endpoint that counts POST requests."""

    def __init__(self, mock_dir: Path):
        base = mockllm.handler_class(mock_dir)
        stub = self
        self.calls = 0
        self.lock = threading.Lock()

        class Counting(base):
            def do_POST(self):
                with stub.lock:
                    stub.calls += 1
                super().do_POST()

        self.server = ThreadingHTTPServer(("127.0.0.1", 0), Counting)
        threading.Thread(target=self.server.serve_forever, daemon=True).start()
        self.url = f"http://127.0.0.1:{self.server.server_address[1]}/v1"

    def close(self):
        self.server.shutdown()
        self.server.server_close()


class ResumeTests(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.tasks = self.tmp / "tasks"
        mock = self.tmp / "mock"
        mock.mkdir()
        for t in TASKS:
            root = self.tasks / t
            (root / "start").mkdir(parents=True)
            (root / "start" / "main.py").write_text("print(0)\n")
            (root / "SPEC.md").write_text("Print 1.\n")
            (root / "task.json").write_text(json.dumps({
                "id": t, "kind": "benchmark", "title": t, "entry": "main.py", "editable": ["main.py"],
                "time_limit_s": 5, "mem_limit_mb": 64, "compare": "lines"}))
            (mock / f"{t}.md").write_text("FILE: main.py\n```\nprint(1)\n```\n")
            (mock / f"{t}.r1.md").write_text("FILE: main.py\n```\nprint(11)\n```\n")
        self.out = self.tmp / "proposals"
        self.out.mkdir()
        self.stub = _Stub(mock)
        self.env = {"LLM_BASE_URL": self.stub.url, "LLM_API_KEY": "not-a-secret", "LLM_NAME": "mock"}

    def tearDown(self):
        self.stub.close()

    # helpers
    def propose(self, *, resume=True, samples=0, round_no=0, feedback=None):
        before = self.stub.calls
        propose.run(self.tasks, self.out, "benchmark", "MOCK", max_calls=100, samples=samples,
                    round_no=round_no, feedback_dir=feedback, workers=4, env=self.env, resume=resume)
        return self.stub.calls - before

    def plant(self, task, cand, **over):
        rec = {"task": task, "candidate": cand, "condition": "C0", "source": "model", "mode": "LIVE",
               "text": "FILE: main.py\n```\nprint('kept')\n```\n", "error": None}
        rec.update(over)
        (self.out / task).mkdir(exist_ok=True)
        (self.out / task / f"{cand}.json").write_text(json.dumps(rec))

    def snapshot(self):
        return {p.relative_to(self.out).as_posix(): p.read_bytes()
                for p in sorted(self.out.glob("*/*.json"))}

    def answers(self, cand):
        return sorted(p.parent.name for p in self.out.glob(f"*/{cand}.json"))

    # A-D: k of N answers already present
    def _k_present(self, k):
        for t in TASKS[:k]:
            self.plant(t, "c0")
        kept = self.snapshot()
        calls = self.propose()
        self.assertEqual(calls, N - k)
        self.assertEqual(self.answers("c0"), TASKS)
        for path, data in kept.items():  # existing answers byte-identical, never asked again
            self.assertEqual((self.out / path).read_bytes(), data, path)

    def test_a_none_present_all_asked(self):
        self._k_present(0)

    def test_b_one_present_rest_asked(self):
        self._k_present(1)

    def test_c_all_but_one_present_exactly_one_asked(self):
        self._k_present(N - 1)

    def test_d_all_present_no_call(self):
        self._k_present(N)

    # E: partial step with samples -> complete set, nothing duplicated
    def test_e_partial_step_with_samples_completes_without_duplicates(self):
        for t in TASKS:
            self.plant(t, "c0")
        for t in TASKS[:2]:
            self.plant(t, "s1", condition="C1")
        calls = self.propose(samples=2)
        self.assertEqual(calls, 2 + N)  # s1 for t3, t4 and s2 for all
        for t in TASKS:
            self.assertEqual(sorted(p.name for p in (self.out / t).glob("*.json")),
                             ["c0.json", "s1.json", "s2.json"])
        recs = [json.loads(p.read_text()) for p in self.out.glob("*/*.json")]
        self.assertEqual(len({(r["task"], r["candidate"]) for r in recs}), len(recs))

    # F: resuming a complete run again is idempotent
    def test_f_repeated_resume_is_idempotent(self):
        self.plant(TASKS[0], "c0")
        self.propose(samples=1)
        done = self.snapshot()
        self.assertEqual(self.propose(samples=1), 0)
        self.assertEqual(self.propose(samples=1), 0)
        self.assertEqual(self.snapshot(), done)

    # repair rounds use the same path
    def test_repair_round_asks_only_missing_tasks(self):
        fb = self.tmp / "feedback"
        for t in TASKS:
            self.plant(t, "c0")
        for t in TASKS[:3]:  # three tasks failed and got feedback
            (fb / t).mkdir(parents=True)
            (fb / t / "c0.json").write_text(json.dumps({
                "task": t, "candidate": "c0", "verdict": "FAIL_TESTS", "hidden_passed": 0,
                "hidden_total": 1, "hidden_failures": {"wrong output": 1}, "build_error": None,
                "answer_problem": None, "visible": []}))
        self.plant(TASKS[0], "r1", condition="C2")
        self.assertEqual(self.propose(round_no=1, feedback=fb), 2)
        self.assertEqual(self.answers("r1"), TASKS[:3])  # t4 passed: no repair round

    def test_failed_answer_is_asked_again(self):
        self.plant(TASKS[0], "c0", text=None, error="call budget of 1 reached")
        for t in TASKS[1:]:
            self.plant(t, "c0")
        self.assertEqual(self.propose(), 1)
        rec = json.loads((self.out / TASKS[0] / "c0.json").read_text())
        self.assertIsNone(rec["error"])

    def test_without_resume_behaviour_is_unchanged(self):
        for t in TASKS:
            self.plant(t, "c0")
        self.assertEqual(self.propose(resume=False), N)  # a normal step asks every task

    def test_has_answer(self):
        self.plant("t1", "c0")
        self.plant("t2", "c0", error="model call failed: HTTP 503", text=None)
        (self.out / "t3").mkdir()
        (self.out / "t3" / "c0.json").write_text("{broken")
        self.assertTrue(propose.has_answer(self.out / "t1" / "c0.json"))
        self.assertFalse(propose.has_answer(self.out / "t2" / "c0.json"))
        self.assertFalse(propose.has_answer(self.out / "t3" / "c0.json"))
        self.assertFalse(propose.has_answer(self.out / "t4" / "c0.json"))


if __name__ == "__main__":
    unittest.main()
