"""Task validation (experiment E0): is every benchmark task fit for measuring?

A task is valid only if
* the oracle (reference solution) passes every hidden case,
* the unchanged start code fails,
* a program that memorises the visible examples fails,
* every near-miss variant fails (at least MIN_NEAR_MISS of them exist),
* it has at least MIN_HIDDEN hidden cases.

The mutation-search baseline is reported as a flag, not a failure: a task it
solves does not need a model, which matters when reading model results.
"""

from __future__ import annotations

import json
from pathlib import Path

from .tasks import hidden_cases, list_tasks

MIN_HIDDEN = 8
MIN_NEAR_MISS = 2


def check(verdicts: list[dict], tasks, hidden_root: Path) -> list[dict]:
    by = {(v["task"], v["candidate"]): v for v in verdicts}
    rows = []
    for task in tasks:
        problems = []
        n_hidden = len(hidden_cases(hidden_root, task.id))
        if n_hidden < MIN_HIDDEN:
            problems.append(f"only {n_hidden} hidden cases (need {MIN_HIDDEN})")

        def verdict(cand):
            v = by.get((task.id, cand))
            return v["verdict"] if v else "MISSING"

        if verdict("b2") != "PASS":
            problems.append(f"oracle does not pass ({verdict('b2')})")
        for cand, label in (("b0", "start code"), ("b3", "memorised examples")):
            if verdict(cand) in ("PASS", "MISSING"):
                problems.append(f"{label}: {verdict(cand)} (must be rejected)")
        near = sorted(c for (t, c) in by if t == task.id and c.startswith("nm"))
        if len(near) < MIN_NEAR_MISS:
            problems.append(f"only {len(near)} near-miss variants (need {MIN_NEAR_MISS})")
        accepted = [c for c in near if verdict(c) == "PASS"]
        if accepted:
            problems.append(f"near-miss accepted: {', '.join(accepted)}")
        rows.append({"task": task.id, "hidden_cases": n_hidden, "oracle": verdict("b2"),
                     "start": verdict("b0"), "memorise": verdict("b3"),
                     "near_miss_rejected": f"{len(near) - len(accepted)}/{len(near)}",
                     "mutation_search": verdict("b1"),
                     "flag": "solvable without a model" if verdict("b1") == "PASS" else "",
                     "valid": not problems, "problems": problems})
    return rows


def run(tasks_root: Path, hidden_root: Path, verdicts_file: Path, out_file: Path, kind: str,
        only: set[str] | None = None) -> int:
    verdicts = json.loads(verdicts_file.read_text(encoding="utf-8"))
    tasks = [t for t in list_tasks(tasks_root, kind) if not only or t.id in only]
    rows = check(verdicts, tasks, hidden_root)
    out_file.write_text(json.dumps(rows, indent=2) + "\n", encoding="utf-8")
    print("| task | hidden | oracle | start | memorise | near-miss rejected | mutation search | valid |")
    print("|---|---|---|---|---|---|---|---|")
    for r in rows:
        print(f"| {r['task']} | {r['hidden_cases']} | {r['oracle']} | {r['start']} | {r['memorise']} | "
              f"{r['near_miss_rejected']} | {r['mutation_search']} {r['flag']} | "
              f"{'yes' if r['valid'] else 'NO: ' + '; '.join(r['problems'])} |")
    n_valid = sum(r["valid"] for r in rows)
    print(f"VALIDATION: {n_valid}/{len(rows)} tasks valid", flush=True)
    return 0 if n_valid == len(rows) else 1
