"""Pipeline regression check (``make regress``), no model involved.

Runs the benchmark tasks with the MOCK stub plus baselines and compares the
outcome with ``data/mock/expectations.json``: the expected verdict of each
canned answer, the oracle passing, and the start code / memoriser failing.
Any difference means the pipeline itself changed behaviour.
"""

from __future__ import annotations

import json
from pathlib import Path


def check(verdicts: list[dict], expectations: dict) -> list[str]:
    by = {(v["task"], v["candidate"]): v["verdict"] for v in verdicts}
    problems = []
    for v in verdicts:  # visible examples feed the repair rounds; they must really run
        bad = [c["case"] for c in v.get("visible", []) if c["status"] == "INFRA_ERROR"]
        if bad:
            problems.append(f"{v['task']}/{v['candidate']}: visible examples not run ({', '.join(bad)})")
    tasks = sorted({v["task"] for v in verdicts})
    for task in tasks:
        want = expectations.get(task) if task != "repair_final" else None
        if want is None:
            problems.append(f"{task}: no expectation in expectations.json")
        elif by.get((task, "c0")) != want:
            problems.append(f"{task}: mock answer verdict {by.get((task, 'c0'))}, expected {want}")
        if by.get((task, "b2")) != "PASS":
            problems.append(f"{task}: oracle {by.get((task, 'b2'))}")
        for cand in ("b0", "b3"):
            if by.get((task, cand)) == "PASS":
                problems.append(f"{task}: {cand} passed")
    for task, want in sorted(expectations.get("repair_final", {}).items()):
        chain = [by[(task, c)] for c in ("c0", "r1", "r2", "r3") if (task, c) in by]
        got = "PASS" if "PASS" in chain else (chain[-1] if chain else None)
        if got != want:
            problems.append(f"{task}: after repair rounds {got} (chain {chain}), expected {want}")
    for task in sorted(set(expectations) - set(tasks) - {"repair_final"}):
        problems.append(f"{task}: expected but not run")
    return problems


def run(verdicts_file: Path, expectations_file: Path) -> int:
    verdicts = json.loads(verdicts_file.read_text(encoding="utf-8"))
    expectations = json.loads(expectations_file.read_text(encoding="utf-8"))
    problems = check(verdicts, expectations)
    for p in problems:
        print("REGRESSION:", p)
    n = len({v["task"] for v in verdicts})
    print(f"REGRESS: {'PASSED' if not problems else 'FAILED'} ({n} tasks, {len(problems)} problems)",
          flush=True)
    return 0 if not problems else 1
