"""Unit tests for parsing, path safety, applying, judging and reporting."""

from __future__ import annotations

import json
import os
import tempfile
import threading
import unittest
from http.server import ThreadingHTTPServer
from pathlib import Path

from airpatch import apply, llm, mockllm, proposal, report, verify
from airpatch.fingerprint import fingerprint
from airpatch.tasks import Task, load_task, outputs_match, safe_relpath

DATA = Path(os.environ.get("AIRPATCH_DATA", Path(__file__).resolve().parents[2] / "data"))


def make_task(tmp: Path, task_id: str = "demo", editable=("main.py",), limit: int = 5) -> Task:
    root = tmp / "tasks" / task_id
    (root / "start").mkdir(parents=True)
    (root / "start" / "main.py").write_text("print('start')\n")
    (root / "SPEC.md").write_text("Print hello.\n")
    (root / "task.json").write_text(json.dumps({
        "id": task_id, "kind": "benchmark", "title": "Demo", "entry": "main.py",
        "editable": list(editable), "time_limit_s": limit, "mem_limit_mb": 64, "compare": "lines"}))
    return load_task(tmp / "tasks", task_id)


class SafePathTests(unittest.TestCase):
    def test_accepts_plain_relative_paths(self):
        self.assertEqual(safe_relpath("main.py"), "main.py")
        self.assertEqual(safe_relpath("pkg/util.py"), "pkg/util.py")
        self.assertEqual(safe_relpath("pkg//util.py"), "pkg/util.py")

    def test_rejects_escapes(self):
        for bad in ("", "/etc/passwd", "../x", "a/../../x", "a\\b", "a\x00b", ".hidden", "a/.git/x", "."):
            self.assertIsNone(safe_relpath(bad), bad)


class ParseTests(unittest.TestCase):
    def test_file_block(self):
        text = "Sure.\n\nFILE: main.py\n```python\nprint(1)\n```\nDone."
        parsed = proposal.parse(text, ("main.py",))
        self.assertEqual(parsed.status, "OK")
        self.assertEqual(parsed.files, {"main.py": "print(1)\n"})

    def test_single_fence_for_single_file(self):
        parsed = proposal.parse("```python\nprint(2)\n```", ("main.py",))
        self.assertEqual(parsed.files, {"main.py": "print(2)\n"})

    def test_no_block_is_malformed(self):
        self.assertEqual(proposal.parse("I cannot help.", ("main.py",)).status, "MALFORMED_PROPOSAL")

    def test_traversal_and_absolute_paths_are_violations(self):
        text = ("FILE: ../../hidden/x.out\n```\nx\n```\n"
                "FILE: /etc/passwd\n```\nroot\n```\n"
                "FILE: main.py\n```\nok\n```\n")
        parsed = proposal.parse(text, ("main.py",))
        self.assertEqual(parsed.status, "POLICY_VIOLATION")
        self.assertEqual(len(parsed.violations), 2)

    def test_non_editable_file_is_violation(self):
        parsed = proposal.parse("FILE: other.py\n```\nx\n```\n", ("main.py",))
        self.assertEqual(parsed.status, "POLICY_VIOLATION")

    def test_duplicate_block_is_malformed(self):
        text = "FILE: main.py\n```\na\n```\nFILE: main.py\n```\nb\n```\n"
        self.assertEqual(proposal.parse(text, ("main.py",)).status, "MALFORMED_PROPOSAL")


class ApplyTests(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.task = make_task(self.tmp)

    def _proposal(self, text, error=None) -> Path:
        path = self.tmp / "c0.json"
        path.write_text(json.dumps({"text": text, "error": error}))
        return path

    def test_applied_and_built(self):
        rec = apply.apply_one(self.task, self._proposal("FILE: main.py\n```\nprint('hi')\n```\n"),
                              self.tmp / "ws")
        self.assertEqual(rec["status"], "APPLIED")
        self.assertEqual((self.tmp / "ws" / "main.py").read_text(), "print('hi')\n")

    def test_violation_writes_nothing(self):
        rec = apply.apply_one(self.task, self._proposal("FILE: ../evil.py\n```\nx\n```\n"),
                              self.tmp / "ws")
        self.assertEqual(rec["status"], "POLICY_VIOLATION")
        self.assertFalse((self.tmp / "ws").exists())
        self.assertFalse((self.tmp / "evil.py").exists())

    def test_syntax_error_is_build_error(self):
        rec = apply.apply_one(self.task, self._proposal("FILE: main.py\n```\ndef (:\n```\n"),
                              self.tmp / "ws")
        self.assertEqual(rec["status"], "BUILD_ERROR")
        self.assertTrue(rec["build"]["fingerprint"])

    def test_model_error_is_no_answer(self):
        rec = apply.apply_one(self.task, self._proposal(None, error="model call failed: HTTP 503"),
                              self.tmp / "ws")
        self.assertEqual(rec["status"], "NO_RESPONSE")


class JudgeTests(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.task = make_task(self.tmp, limit=2)
        self.hidden = self.tmp / "hidden"
        (self.hidden / "demo" / "cases").mkdir(parents=True)
        (self.hidden / "demo" / "cases" / "01.in").write_text("")
        (self.hidden / "demo" / "cases" / "01.out").write_text("hello\n")
        self.exec = self.tmp / "exec"
        self.exec.mkdir()

    def _case(self, exit_code=0, oom="false", out="hello\n", start="2026-10-04T10:00:00.000000000Z",
              end="2026-10-04T10:00:00.250000000Z", state=True):
        if state:
            (self.exec / "01.state").write_text(f"{exit_code} {oom} {start} {end}\n")
        (self.exec / "01.out").write_text(out)
        (self.exec / "01.err").write_text("")
        return verify.judge_case(self.task, "01", self.hidden, self.exec, out_limit=100)

    def test_pass(self):
        res = self._case()
        self.assertEqual(res["status"], "PASS")
        self.assertEqual(res["duration_ms"], 250)

    def test_trailing_whitespace_is_ignored_in_lines_mode(self):
        self.assertEqual(self._case(out="hello   \n\n")["status"], "PASS")

    def test_wrong_output(self):
        self.assertEqual(self._case(out="bye\n")["status"], "FAIL_TESTS")

    def test_crash(self):
        self.assertEqual(self._case(exit_code=1)["status"], "FAIL_TESTS")

    def test_timeout_codes(self):
        self.assertEqual(self._case(exit_code=124)["status"], "TIMEOUT")
        self.assertEqual(self._case(exit_code=137, end="2026-10-04T10:00:03.1Z")["status"], "TIMEOUT")

    def test_resource_limits(self):
        self.assertEqual(self._case(exit_code=137)["status"], "RESOURCE_LIMIT")
        self.assertEqual(self._case(oom="true", exit_code=137)["status"], "RESOURCE_LIMIT")
        self.assertEqual(self._case(out="x" * 101)["status"], "RESOURCE_LIMIT")

    def test_missing_state_is_infra_error(self):
        self.assertEqual(self._case(state=False)["status"], "INFRA_ERROR")

    def test_docker_time(self):
        self.assertIsNone(verify.parse_docker_time("0001-01-01T00:00:00Z"))
        a = verify.parse_docker_time("2026-10-04T10:00:00.5Z")
        b = verify.parse_docker_time("2026-10-04T10:00:01.000000001Z")
        self.assertEqual(b - a, 500_000_001)


class LLMClientTests(unittest.TestCase):
    def test_chat_url(self):
        self.assertEqual(llm.chat_url("https://x.ch/v1"), "https://x.ch/v1/chat/completions")
        self.assertEqual(llm.chat_url("https://x.ch/v1/"), "https://x.ch/v1/chat/completions")
        self.assertEqual(llm.chat_url("https://x.ch"), "https://x.ch/v1/chat/completions")
        self.assertEqual(llm.chat_url("https://x.ch/v1/chat/completions"),
                         "https://x.ch/v1/chat/completions")
        with self.assertRaises(llm.LLMError):
            llm.chat_url("ftp://x.ch")

    def test_round_trip_with_stub_and_key_not_leaked(self):
        mock_dir = Path(tempfile.mkdtemp())
        (mock_dir / "demo.md").write_text("FILE: main.py\n```\nprint(1)\n```\n")
        server = ThreadingHTTPServer(("127.0.0.1", 0), mockllm.handler_class(mock_dir))
        threading.Thread(target=server.serve_forever, daemon=True).start()
        try:
            base = f"http://127.0.0.1:{server.server_address[1]}/v1"
            out = llm.chat(base, "SENTINEL-KEY-123", "mock",
                           [{"role": "user", "content": "Task-ID: demo\nfix it"}])
            self.assertIn("print(1)", out["text"])
            self.assertNotIn("SENTINEL", json.dumps(out))
            with self.assertRaises(llm.LLMError) as ctx:
                llm.chat(base, "SENTINEL-KEY-123", "fail-503",
                         [{"role": "user", "content": "x"}], retries=0)
            self.assertEqual(ctx.exception.status, 503)
            self.assertTrue(ctx.exception.retryable)
            self.assertNotIn("SENTINEL", str(ctx.exception))
        finally:
            server.shutdown()
            server.server_close()


class ReportTests(unittest.TestCase):
    def test_banners_mark_non_live_modes(self):
        self.assertIn("NOT new Apertus results", report.BANNERS["REPLAY"])
        self.assertIn("NOT Apertus", report.BANNERS["MOCK"])

    def test_mode_mismatch_is_refused(self):
        tmp = Path(tempfile.mkdtemp())
        (tmp / "results").mkdir()
        (tmp / "results" / "verdicts.json").write_text("[]")
        (tmp / "proposals" / "t").mkdir(parents=True)
        (tmp / "proposals" / "t" / "c0.json").write_text(json.dumps(
            {"task": "t", "candidate": "c0", "mode": "MOCK"}))
        with self.assertRaises(SystemExit):
            report.run(tmp, tmp / "out", "LIVE", "r1")


class ViewerTests(unittest.TestCase):
    def test_model_output_is_escaped_and_nothing_is_loaded(self):
        from airpatch import viewer
        evil = "<script>alert(1)</script><img src=x onerror=y>"
        verdicts = [{"task": "t", "candidate": "c0", "kind": "benchmark", "source": "model",
                     "verdict": "FAIL_TESTS", "cases_passed": 0, "cases_total": 1, "detail": evil,
                     "cases": [{"case": "01", "status": "FAIL_TESTS"}], "visible": []}]
        proposals = {("t", "c0"): {"task": "t", "candidate": "c0", "condition": "C0", "source": "model",
                                   "mode": "MOCK", "text": evil}}
        summary = report.summarise(verdicts, proposals, "MOCK")
        page = viewer.render(summary, verdicts, proposals, "r1")
        self.assertNotIn("<script>", page)
        self.assertNotIn("<img", page)
        self.assertIn("&lt;script&gt;", page)
        self.assertIn("default-src 'none'", page)
        self.assertIn("NOT Apertus", page)

    def test_usage_table_shows_tokens_and_latency(self):
        from airpatch import viewer
        verdicts = [{"task": "t", "candidate": c, "kind": "benchmark", "source": "model", "verdict": "PASS",
                     "cases_passed": 1, "cases_total": 1, "cases": [], "visible": []} for c in ("c0", "s1")]
        proposals = {("t", "c0"): {"condition": "C0", "usage": {"total_tokens": 120}, "latency_ms": 2500},
                     ("t", "s1"): {"condition": "C1", "usage": None, "latency_ms": None}}
        html_ = viewer._usage_table("benchmark", verdicts, proposals)
        self.assertIn("<td>120</td><td>2.5 s</td>", html_)
        self.assertIn("<td>1</td><td>-</td><td>-</td>", html_)


class DeterminismTests(unittest.TestCase):
    def _v(self, status, exit_code, verdict, extra=None):
        case = {"case": "01", "status": status, "exit": exit_code, "duration_ms": 5}
        case.update(extra or {})
        return [{"task": "t", "candidate": "c0", "verdict": verdict, "cases": [case], "visible": []}]

    def test_time_vs_memory_limit_counts_as_same_outcome_and_is_reported(self):
        from airpatch import determinism
        diffs, swaps = determinism.compare(self._v("TIMEOUT", 124, "TIMEOUT"),
                                           self._v("RESOURCE_LIMIT", 137, "RESOURCE_LIMIT",
                                                   {"reason": "memory limit"}))
        self.assertEqual(diffs, [])
        self.assertEqual(swaps, 1)

    def test_other_differences_are_reported(self):
        from airpatch import determinism
        diffs, _ = determinism.compare(self._v("PASS", 0, "PASS"), self._v("FAIL_TESTS", 0, "FAIL_TESTS"))
        self.assertEqual(len(diffs), 1)
        diffs, _ = determinism.compare(self._v("TIMEOUT", 124, "TIMEOUT"), self._v("FAIL_TESTS", 1, "FAIL_TESTS"))
        self.assertEqual(len(diffs), 1)


class MiscTests(unittest.TestCase):
    def test_fingerprint_ignores_addresses(self):
        a = fingerprint('File "/work/main.py", line 3\nTypeError: <obj at 0x7f00aa>')
        b = fingerprint('File "/work/main.py", line 3\nTypeError: <obj at 0x5512bb>')
        self.assertEqual(a, b)
        self.assertIsNone(fingerprint("  \n"))

    def test_outputs_match_modes(self):
        self.assertTrue(outputs_match("a\nb\n", "a \nb", "lines"))
        self.assertFalse(outputs_match("a\nb\n", "a \nb", "exact"))


if __name__ == "__main__":
    unittest.main()


class RegressCheckTests(unittest.TestCase):
    def test_visible_example_not_run_is_a_problem(self):
        from airpatch import regress
        base = {"task": "t", "candidate": "c0", "verdict": "PASS", "cases": [], "visible": [
            {"case": "v01", "status": "PASS"}, {"case": "v02", "status": "INFRA_ERROR"}]}
        rows = [base, {"task": "t", "candidate": "b2", "verdict": "PASS"}]
        problems = regress.check(rows, {"t": "PASS"})
        self.assertEqual(problems, ["t/c0: visible examples not run (v02)"])
        base["visible"][1]["status"] = "FAIL_TESTS"
        self.assertEqual(regress.check(rows, {"t": "PASS"}), [])
