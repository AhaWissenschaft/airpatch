"""Tests for the call and token caps of the propose step (reservation logic)."""

from __future__ import annotations

import json
import os
import tempfile
import threading
import time
import unittest
from pathlib import Path

from airpatch import llm, propose
from airpatch.propose import Budget, token_bound
from airpatch.tasks import load_task

DATA = Path(os.environ.get("AIRPATCH_DATA", Path(__file__).resolve().parents[2] / "data"))


def usage(total: int) -> dict:
    return {"prompt_tokens": total // 2, "completion_tokens": total - total // 2, "total_tokens": total}


class TokenBoundTests(unittest.TestCase):
    def test_bound_covers_text_bytes_margins_and_answer(self):
        msgs = [{"role": "system", "content": "abc"}, {"role": "user", "content": "äö"}]
        expected = 3 + 4 + 2 * propose.PROMPT_MARGIN_PER_MESSAGE + propose.PROMPT_MARGIN_PER_REQUEST + 100
        self.assertEqual(token_bound(msgs, 100), expected)


class BudgetTests(unittest.TestCase):
    def test_call_cap(self):
        b = Budget(2, None)
        self.assertIsNone(b.take_call(10))
        self.assertIsNone(b.take_call(10))
        self.assertIn("call budget", b.take_call(10))
        self.assertEqual(b.calls, 2)

    def test_open_reservations_block_further_calls(self):
        b = Budget(100, 1000)
        self.assertIsNone(b.take_call(400))
        self.assertIsNone(b.take_call(400))
        self.assertIn("token budget", b.take_call(400))  # 800 reserved + 400 > 1000
        self.assertFalse(b.settle(400, usage(150)))
        self.assertIsNone(b.take_call(400))  # 150 + 400 + 400 <= 1000
        self.assertEqual(b.calls, 3)

    def test_failed_call_releases_its_reservation(self):
        b = Budget(100, 500)
        self.assertIsNone(b.take_call(500))
        b.settle(500, None, failed=True)
        self.assertEqual((b.tokens, b.reserved), (0, 0))
        self.assertIsNone(b.take_call(500))

    def test_missing_usage_counts_the_full_reservation(self):
        b = Budget(100, 1000)
        b.take_call(600)
        b.settle(600, None)
        self.assertEqual(b.tokens, 600)
        self.assertIn("token budget", b.take_call(600))

    def test_overrun_is_counted_and_stops_further_calls(self):
        b = Budget(100, 10_000)
        b.take_call(100)
        self.assertTrue(b.settle(100, usage(130)))
        self.assertEqual((b.tokens, b.overruns), (130, 1))
        self.assertIn("exceeded", b.take_call(100))

    def test_without_token_cap_reported_tokens_are_still_counted(self):
        b = Budget(10, None)
        b.take_call(999_999)
        b.settle(999_999, usage(42))
        self.assertEqual((b.tokens, b.reserved), (42, 0))

    def test_parallel_calls_never_exceed_the_cap(self):
        # Every worker reports exactly its reservation (the worst case). Without
        # reservations, eight workers that all pass the check before anyone
        # settles would overshoot a cap of 1000 by up to 7 x 300.
        cap, bound = 1000, 300
        b = Budget(1000, cap)
        start = threading.Barrier(8)

        def worker():
            start.wait()
            for _ in range(5):
                if b.take_call(bound) is None:
                    time.sleep(0.01)  # the "request" is in flight
                    b.settle(bound, usage(bound))

        threads = [threading.Thread(target=worker) for _ in range(8)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        self.assertLessEqual(b.tokens, cap)
        self.assertEqual(b.tokens, 3 * bound)
        self.assertEqual(b.reserved, 0)


class ProposeBudgetTests(unittest.TestCase):
    """End to end through propose.run with a fake endpoint and 4 workers."""

    def test_run_keeps_token_cap_with_parallel_workers(self):
        data = DATA
        ids = sorted(p.name for p in (data / "tasks").iterdir()
                     if (p / "task.json").is_file()
                     and json.loads((p / "task.json").read_text())["kind"] == "benchmark")[:6]
        calls = []

        def fake_chat(base_url, api_key, model, messages, *, temperature, max_tokens, **kw):
            bound = token_bound(messages, max_tokens)
            calls.append(bound)
            time.sleep(0.02)
            return {"text": "x", "usage": usage(bound), "latency_ms": 1, "tries": 1,
                    "finish_reason": "stop", "served_model": model}

        bounds = []
        for i in ids:
            bounds.append(token_bound(propose.build_messages(load_task(data / "tasks", i)), 2048))
        cap = sum(sorted(bounds)[:2]) + 1  # room for about two answers only
        env = {"LLM_NAME": "fake", "LLM_BASE_URL": "http://fake/v1", "LLM_API_KEY": "k",
               "AIRPATCH_MAX_TOKENS": "2048"}
        original = llm.chat
        llm.chat = fake_chat
        try:
            with tempfile.TemporaryDirectory() as tmp:
                propose.run(data / "tasks", Path(tmp), "benchmark", "LIVE", max_calls=50,
                            max_tokens=cap, workers=4, env=env, only=set(ids))
                ledger = json.loads((Path(tmp) / "_budget.json").read_text())
        finally:
            llm.chat = original
        self.assertLessEqual(ledger["tokens"], cap)
        self.assertEqual(ledger["tokens"], sum(calls))
        self.assertLess(len(calls), len(ids))


if __name__ == "__main__":
    unittest.main()
