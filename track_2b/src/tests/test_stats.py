"""Statistics and cassette guards."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from airpatch import cassette
from airpatch.stats import mcnemar_exact, paired, wilson


class StatsTests(unittest.TestCase):
    def test_wilson_known_values(self):
        lo, hi = wilson(20, 40)
        self.assertAlmostEqual(lo, 0.3520, places=3)
        self.assertAlmostEqual(hi, 0.6480, places=3)
        self.assertEqual(wilson(0, 0), (0.0, 1.0))
        lo, hi = wilson(0, 10)
        self.assertEqual(lo, 0.0)
        self.assertGreater(hi, 0.25)

    def test_mcnemar_exact(self):
        self.assertEqual(mcnemar_exact(0, 0), 1.0)
        self.assertAlmostEqual(mcnemar_exact(6, 0), 0.03125)
        self.assertAlmostEqual(mcnemar_exact(5, 0), 0.0625)
        self.assertAlmostEqual(mcnemar_exact(3, 3), 1.0)

    def test_paired_counts(self):
        a = {"t1": True, "t2": True, "t3": False, "t4": False}
        b = {"t1": True, "t2": False, "t3": True, "t4": False, "t5": True}
        r = paired(a, b)
        self.assertEqual((r["tasks"], r["both"], r["only_a"], r["only_b"], r["neither"]), (4, 1, 1, 1, 1))


class CassetteTests(unittest.TestCase):
    def _run(self, mode, text="FILE: main.py\n```\nx\n```\n"):
        run = Path(tempfile.mkdtemp())
        (run / "proposals" / "t").mkdir(parents=True)
        (run / "proposals" / "t" / "c0.json").write_text(json.dumps(
            {"task": "t", "candidate": "c0", "condition": "C0", "source": "model", "mode": mode,
             "text": text, "model": "m", "recorded_at": "r1"}))
        (run / "proposals" / "t" / "b2.json").write_text(json.dumps(
            {"task": "t", "candidate": "b2", "source": "baseline", "mode": "BASELINE"}))
        return run

    def test_records_live_answers_only(self):
        out = Path(tempfile.mkdtemp()) / "cas"
        meta = cassette.record(self._run("LIVE"), out)
        self.assertEqual(meta["answers"], 1)
        self.assertTrue((out / "t" / "c0.json").is_file())
        self.assertFalse((out / "t" / "b2.json").exists())

    def test_refuses_mock_answers_and_secrets(self):
        with self.assertRaises(SystemExit):
            cassette.record(self._run("MOCK"), Path(tempfile.mkdtemp()) / "cas")
        with self.assertRaises(SystemExit):
            cassette.record(self._run("LIVE", text="key SECRET-1"), Path(tempfile.mkdtemp()) / "cas",
                            secret="SECRET-1")


if __name__ == "__main__":
    unittest.main()


class CompareInfraTests(unittest.TestCase):
    """INFRA_ERROR is excluded from scoring (analysis plan), never counted as a failure."""

    def _run(self, tmp: Path, name: str, rows: dict) -> Path:
        run = tmp / name
        (run / "results").mkdir(parents=True)
        (run / "proposals").mkdir()
        verdicts = [{"task": t, "candidate": c, "kind": "benchmark", "verdict": v}
                    for (t, c), v in rows.items()]
        (run / "results" / "verdicts.json").write_text(json.dumps(verdicts))
        return run

    def test_infra_error_not_scored(self):
        from airpatch import compare
        with tempfile.TemporaryDirectory() as d:
            run = self._run(Path(d), "a", {
                ("t1", "c0"): "PASS", ("t1", "s1"): "INFRA_ERROR", ("t1", "s2"): "PASS",
                ("t2", "c0"): "INFRA_ERROR", ("t2", "s1"): "FAIL_TESTS", ("t2", "s2"): "FAIL_TESTS",
                ("t3", "c0"): "FAIL_TESTS", ("t3", "r1"): "INFRA_ERROR", ("t3", "s1"): "FAIL_TESTS",
                ("t3", "s2"): "INFRA_ERROR",
                ("t4", "c0"): "FAIL_TESTS", ("t4", "r1"): "PASS", ("t4", "s1"): "FAIL_TESTS",
                ("t4", "s2"): "FAIL_TESTS",
                ("t1", "b1"): "FAIL_TESTS", ("t2", "b1"): "FAIL_TESTS", ("t3", "b1"): "FAIL_TESTS",
                ("t4", "b1"): "INFRA_ERROR"})
            conds = compare.solved_by_condition(run)
            self.assertEqual(conds["C0"], {"t1": True, "t2": None, "t3": False, "t4": False})
            self.assertEqual(conds["C1"], {"t1": True, "t2": False, "t3": None, "t4": False})
            self.assertEqual(conds["C2"], {"t1": True, "t2": None, "t3": None, "t4": True})
            result = compare.compare([("a", run)])
            rows = {r["condition"]: r for r in result["runs"][0]["rows"]}
            self.assertEqual((rows["C0"]["solved"], rows["C0"]["tasks"], rows["C0"]["infra_excluded"]), (1, 3, 1))
            self.assertEqual((rows["C2"]["solved"], rows["C2"]["tasks"], rows["C2"]["infra_excluded"]), (2, 2, 2))
            c0_b1 = next(c for c in result["comparisons"] if c["what"] == "a: C0 vs B1")
            self.assertEqual((c0_b1["tasks"], c0_b1["only_a"]), (2, 1))  # t2 and t4 not scored
            self.assertIn("not scored (INFRA_ERROR)", compare.to_markdown(result))

    def test_across_runs_uses_tasks_scored_in_both(self):
        from airpatch import compare
        with tempfile.TemporaryDirectory() as d:
            a = self._run(Path(d), "a", {("t1", "c0"): "PASS", ("t2", "c0"): "PASS", ("t3", "c0"): "FAIL_TESTS"})
            b = self._run(Path(d), "b", {("t1", "c0"): "INFRA_ERROR", ("t2", "c0"): "FAIL_TESTS",
                                         ("t3", "c0"): "FAIL_TESTS"})
            result = compare.compare([("a", a), ("b", b)])
            c = next(c for c in result["comparisons"] if c["what"] == "C0: a vs b")
            self.assertEqual((c["tasks"], c["only_a"], c["only_b"], c["neither"]), (2, 1, 0, 1))
