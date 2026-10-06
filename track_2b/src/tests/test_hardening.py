"""Post-evaluation hardening tests: guards around the frozen evaluation.

They change nothing that is measured; they make sure it stays as recorded.
"""

from __future__ import annotations

import io
import json
import os
import re
import tempfile
import threading
import unittest
import urllib.error
import urllib.request
from http.server import ThreadingHTTPServer
from pathlib import Path

from airpatch import determinism, llm, mockllm, mutsearch, propose, verify
from airpatch.tasks import list_tasks, load_task, visible_case_ids, visible_examples

DATA = Path(os.environ.get("AIRPATCH_DATA", Path(__file__).resolve().parents[2] / "data"))
LAUNCHER = Path(__file__).resolve().parents[2] / "scripts" / "airpatch.sh"


def make_task(tmp: Path, start: str = "print('start')\n", visible: list[tuple[str, str]] = ()):
    root = tmp / "tasks" / "demo"
    (root / "start").mkdir(parents=True)
    (root / "start" / "main.py").write_text(start)
    (root / "SPEC.md").write_text("Spec.\n")
    (root / "task.json").write_text(json.dumps({
        "id": "demo", "kind": "benchmark", "title": "Demo", "entry": "main.py",
        "editable": ["main.py"], "time_limit_s": 5, "mem_limit_mb": 64, "compare": "lines"}))
    if visible:
        (root / "visible").mkdir()
        for i, (inp, out) in enumerate(visible, 1):
            (root / "visible" / f"{i:02d}.in").write_text(inp)
            (root / "visible" / f"{i:02d}.out").write_text(out)
    return load_task(tmp / "tasks", "demo")


class FrozenPromptTests(unittest.TestCase):
    """The recorded answers must still match the prompt the code builds today."""

    def test_cassettes_match_the_current_prompt(self):
        cassettes = [d for d in sorted((DATA / "cassettes").glob("*")) if d.is_dir()]
        self.assertGreaterEqual(len(cassettes), 2)
        tasks = {t.id: t for t in list_tasks(DATA / "tasks")}
        checked = 0
        for cas in cassettes:
            for f in sorted(cas.glob("*/*.json")):
                rec = json.loads(f.read_text(encoding="utf-8"))
                self.assertEqual(rec["mode"], "LIVE", f)
                self.assertEqual(rec.get("served_model"), rec.get("model"), f)
                if rec["condition"] not in ("C0", "C1"):
                    continue  # C2 prompts include feedback; checked by REPLAY end to end
                messages = propose.build_messages(tasks[rec["task"]])
                self.assertEqual(propose.prompt_digest(messages, rec["temperature"]),
                                 rec["prompt_sha256"], f)
                checked += 1
        self.assertGreaterEqual(checked, 320)  # 2 models x 40 tasks x (1 + 3)

    def test_default_cassette_names_an_existing_cassette(self):
        name = (DATA / "cassettes" / "DEFAULT").read_text(encoding="utf-8").strip()
        self.assertRegex(name, r"^[a-z0-9][a-z0-9.-]*$")
        self.assertTrue((DATA / "cassettes" / name / "CASSETTE.json").is_file())


class ReplayGuardTests(unittest.TestCase):
    def _cassette(self, tmp: Path, task, **over) -> Path:
        cas = tmp / "cas" / "demo"
        cas.mkdir(parents=True)
        rec = {"mode": "LIVE", "text": "FILE: main.py\n```\nprint(1)\n```\n", "usage": None,
               "latency_ms": 5, "model": "m", "served_model": "m", "finish_reason": "stop",
               "prompt_sha256": propose.prompt_digest(propose.build_messages(task), 0.0)}
        rec.update(over)
        (cas / "c0.json").write_text(json.dumps(rec))
        return tmp / "cas"

    def _replay(self, task, cas, job=None):
        job = job or ("c0", "C0", propose.build_messages(task), 0.0, {})
        return propose._one(task, job, "REPLAY", propose.Budget(0, None), cas, {})

    def test_matching_prompt_is_replayed(self):
        with tempfile.TemporaryDirectory() as d:
            task = make_task(Path(d))
            rec = self._replay(task, self._cassette(Path(d), task))
            self.assertIsNone(rec["error"])
            self.assertIn("print(1)", rec["text"])

    def test_changed_prompt_is_not_replayed_as_valid(self):
        with tempfile.TemporaryDirectory() as d:
            task = make_task(Path(d))
            rec = self._replay(task, self._cassette(Path(d), task, prompt_sha256="0" * 64))
            self.assertEqual(rec["error"], "recorded prompt differs from current prompt")

    def test_non_live_cassette_is_refused(self):
        with tempfile.TemporaryDirectory() as d:
            task = make_task(Path(d))
            with self.assertRaises(SystemExit):
                self._replay(task, self._cassette(Path(d), task, mode="MOCK"))

    def test_missing_answers(self):
        with tempfile.TemporaryDirectory() as d:
            task = make_task(Path(d))
            cas = Path(d) / "empty"
            cas.mkdir()
            self.assertEqual(self._replay(task, cas)["error"], "no recorded answer for this task")
            job = ("s1", "C1", propose.build_messages(task), 0.7, {"sample": 1})
            self.assertIsNone(self._replay(task, cas, job))  # condition not recorded: skipped


class _Resp(io.BytesIO):
    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False


class LLMRetryTests(unittest.TestCase):
    OK = json.dumps({"model": "m", "choices": [{"message": {"content": "hi"}, "finish_reason": "stop"}],
                     "usage": {"total_tokens": 3}}).encode()

    def _opener(self, script):
        calls = []

        def opener(req, timeout):
            calls.append(req)
            step = script[len(calls) - 1]
            if isinstance(step, int):
                raise urllib.error.HTTPError(req.full_url, step, "x", {}, None)
            return _Resp(step)
        return opener, calls

    def test_retryable_status_is_retried_and_counted(self):
        opener, calls = self._opener([503, 429, self.OK])
        out = llm.chat("https://x/v1", "KEY", "m", [{"role": "user", "content": "q"}],
                       retries=2, retry_wait_s=0, opener=opener)
        self.assertEqual((out["text"], out["tries"], len(calls)), ("hi", 3, 3))

    def test_non_retryable_status_fails_at_once(self):
        opener, calls = self._opener([400, self.OK])
        with self.assertRaises(llm.LLMError) as ctx:
            llm.chat("https://x/v1", "KEY", "m", [], retries=2, retry_wait_s=0, opener=opener)
        self.assertEqual((ctx.exception.status, len(calls)), (400, 1))

    def test_retries_are_bounded(self):
        opener, calls = self._opener([503, 503, 503, self.OK])
        with self.assertRaises(llm.LLMError):
            llm.chat("https://x/v1", "KEY", "m", [], retries=2, retry_wait_s=0, opener=opener)
        self.assertEqual(len(calls), 3)

    def test_http_error_releases_its_connection(self):
        body = io.BytesIO(b"busy")

        def opener(req, timeout):
            raise urllib.error.HTTPError(req.full_url, 503, "x", {}, body)
        with self.assertRaises(llm.LLMError):
            llm.chat("https://x/v1", "KEY", "m", [], retries=0, opener=opener)
        self.assertTrue(body.closed)

    def test_answer_without_content_is_an_error(self):
        opener, _ = self._opener([json.dumps({"choices": []}).encode()])
        with self.assertRaises(llm.LLMError):
            llm.chat("https://x/v1", "KEY", "m", [], retries=0, opener=opener)


class MockStubTests(unittest.TestCase):
    def test_negative_content_length_is_rejected_not_hanging(self):
        server = ThreadingHTTPServer(("127.0.0.1", 0), mockllm.handler_class(Path(tempfile.mkdtemp())))
        threading.Thread(target=server.serve_forever, daemon=True).start()
        try:
            req = urllib.request.Request(f"http://127.0.0.1:{server.server_address[1]}/v1/chat/completions",
                                         data=b"", method="POST", headers={"Content-Length": "-5"})
            with self.assertRaises(urllib.error.HTTPError) as ctx:
                urllib.request.urlopen(req, timeout=5)
            self.assertEqual(ctx.exception.code, 400)
            ctx.exception.close()
        finally:
            server.shutdown()
            server.server_close()


class MutationSearchTests(unittest.TestCase):
    def test_variants_are_deterministic(self):
        src = "x = 1\nif x < 2 and not x == 3:\n    print(x + 1)\n"
        first = [d for d, _ in mutsearch.variants(src)]
        self.assertEqual(first, [d for d, _ in mutsearch.variants(src)])
        self.assertIn("line 2: Lt -> LtE", first)
        self.assertIn("line 3: Add -> Sub", first)

    def test_finds_a_single_edit_fix_using_visible_examples_only(self):
        with tempfile.TemporaryDirectory() as d:
            task = make_task(Path(d), "import sys\nn = int(sys.stdin.read())\nprint(n - 1)\n",
                             visible=[("1\n", "2\n"), ("5\n", "6\n")])
            files, note = mutsearch.search(task)
            self.assertIn("Sub -> Add", note)
            self.assertIn("n + 1", files["main.py"])


class TaskDataConsistencyTests(unittest.TestCase):
    def test_visible_examples_are_numbered_01_to_n(self):
        # feedback.py maps case vNN to the NN-th visible example; gaps would misalign them.
        for task in list_tasks(DATA / "tasks"):
            ids = visible_case_ids(task)
            self.assertEqual(ids, [f"v{i:02d}" for i in range(1, len(ids) + 1)], task.id)
            self.assertEqual(len(ids), len(visible_examples(task)), task.id)


class VerdictVocabularyTests(unittest.TestCase):
    def test_severity_order_uses_known_verdicts(self):
        self.assertTrue(set(verify._SEVERITY) <= set(verify.VERDICTS))


class DeterminismPairingTests(unittest.TestCase):
    def test_differing_candidate_sets_are_reported_and_cases_paired_by_key(self):
        def v(cand, status):
            return {"task": "t", "candidate": cand, "verdict": status,
                    "cases": [{"case": "01", "status": status}]}
        a = [v("b0", "TIMEOUT"), v("c0", "PASS")]
        b = [v("c0", "PASS"), v("b0", "RESOURCE_LIMIT"), v("s1", "PASS")]
        diffs, swaps = determinism.compare(a, b)
        self.assertEqual(diffs, ["only in second run: ('t', 's1')"])
        self.assertEqual(swaps, 1)


class LauncherSecretTests(unittest.TestCase):
    def test_key_value_never_on_a_command_line(self):
        text = LAUNCHER.read_text(encoding="utf-8")
        # Environment values for containers are passed by name (-e NAME), never as -e NAME=$KEY.
        self.assertIsNone(re.search(r"-e\s+\"?[A-Z_]+=\$\{?LLM_API_KEY", text))
        self.assertIn("-e AIRPATCH_SECRET_GUARD ", text)

    def test_cassette_name_is_validated_before_use_in_paths(self):
        text = LAUNCHER.read_text(encoding="utf-8")
        self.assertIn('.*|*[!a-z0-9.-]*) die "AIRPATCH_CASSETTE', text)


if __name__ == "__main__":
    unittest.main()
