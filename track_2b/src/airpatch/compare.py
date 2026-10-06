"""Compare conditions and runs (e.g. Apertus 8B vs 70B) with uncertainty.

Input: one or more finished runs, each given as ``label=<run dir>``.
Output: tasks solved per condition with 95% Wilson intervals, and paired
exact McNemar tests for the pre-registered comparisons:

* within each run:  C0 vs B1 (does the task need a model?), C1 vs C0, C2 vs C0
* across the first two runs: C0 vs C0, C2 vs C2

A task whose answers in a condition hit INFRA_ERROR (endpoint failure, budget
cap) without any pass is not scored in that condition and is counted
separately; paired tests use the tasks scored in both conditions.

Differences are only called "distinguishable" when p < 0.05; with a few dozen
tasks only large effects can reach that, and the report says so.
"""

from __future__ import annotations

import json
from pathlib import Path

from .report import load_proposals
from .stats import paired, wilson


def _outcome(verdicts: list[str | None]) -> bool | None:
    """Solved if any answer passes; not scored (None) if an INFRA_ERROR could have hidden a pass."""
    if "PASS" in verdicts:
        return True
    if "INFRA_ERROR" in verdicts or None in verdicts:
        return None
    return False


def solved_by_condition(run_dir: Path, kind: str = "benchmark") -> dict[str, dict[str, bool | None]]:
    """Per condition and task: True (solved), False, or None (INFRA_ERROR - excluded from scoring)."""
    verdicts = [v for v in json.loads((run_dir / "results" / "verdicts.json").read_text(encoding="utf-8"))
                if v["kind"] == kind]
    by = {(v["task"], v["candidate"]): v["verdict"] for v in verdicts}
    tasks = sorted({v["task"] for v in verdicts})
    out: dict[str, dict[str, bool | None]] = {}
    c0_tasks = [t for t in tasks if (t, "c0") in by]
    if c0_tasks:
        out["C0"] = {t: _outcome([by[(t, "c0")]]) for t in c0_tasks}
    samples = sorted({c for _, c in by if c.startswith("s")})
    if samples:
        out["C1"] = {t: _outcome([by.get((t, s)) for s in samples]) for t in c0_tasks}
    rounds = sorted({c for _, c in by if c.startswith("r")})
    if rounds:
        # Repair rounds exist only after a failed answer, so missing rounds are not gaps.
        out["C2"] = {t: _outcome([by[(t, c)] for c in ["c0"] + rounds if (t, c) in by]) for t in c0_tasks}
    for base in ("b0", "b1", "b2", "b3"):
        if any(c == base for _, c in by):
            out[base.upper()] = {t: _outcome([by.get((t, base))]) for t in tasks}
    return out


def _scored(*conds: dict[str, bool | None]) -> list[dict[str, bool]]:
    """Restrict conditions to the tasks scored (not INFRA_ERROR) in all of them."""
    keep = set.intersection(*(set(c) for c in conds))
    keep = {t for t in keep if all(c[t] is not None for c in conds)}
    return [{t: bool(c[t]) for t in keep} for c in conds]


def mode_of(run_dir: Path) -> str:
    modes = {p["mode"] for p in load_proposals(run_dir).values() if p.get("source", "model") == "model"}
    return ",".join(sorted(modes)) or "NONE"


def compare(runs: list[tuple[str, Path]]) -> dict:
    result = {"runs": [], "comparisons": []}
    solved = {}
    for label, run_dir in runs:
        conds = solved_by_condition(run_dir)
        solved[label] = conds
        rows = []
        for cond, per_task in conds.items():
            scored = [v for v in per_task.values() if v is not None]
            k, n = sum(scored), len(scored)
            lo, hi = wilson(k, n)
            rows.append({"condition": cond, "solved": k, "tasks": n, "ci95": [round(lo, 3), round(hi, 3)],
                         "infra_excluded": len(per_task) - n})
        result["runs"].append({"label": label, "mode": mode_of(run_dir), "rows": rows})
        for a, b in (("C0", "B1"), ("C1", "C0"), ("C2", "C0")):
            if a in conds and b in conds:
                result["comparisons"].append({"what": f"{label}: {a} vs {b}",
                                              **paired(*_scored(conds[a], conds[b]))})
    if len(runs) >= 2:
        (la, _), (lb, _) = runs[0], runs[1]
        for cond in ("C0", "C2"):
            if cond in solved[la] and cond in solved[lb]:
                result["comparisons"].append({"what": f"{cond}: {la} vs {lb}",
                                              **paired(*_scored(solved[la][cond], solved[lb][cond]))})
    return result


def to_markdown(result: dict) -> str:
    lines = ["# Comparison", ""]
    for run in result["runs"]:
        lines += [f"## {run['label']} (mode of model answers: {run['mode']})", "",
                  "| condition | solved | 95% CI | not scored (INFRA_ERROR) |", "|---|---|---|---|"]
        for r in run["rows"]:
            lines.append(f"| {r['condition']} | {r['solved']} / {r['tasks']} | "
                         f"{r['ci95'][0]:.0%} - {r['ci95'][1]:.0%} | {r.get('infra_excluded', 0)} |")
        lines.append("")
    lines += ["## Paired comparisons (exact McNemar)", "",
              "| comparison | tasks | only first | only second | p | reading |", "|---|---|---|---|---|---|"]
    for c in result["comparisons"]:
        reading = "distinguishable" if c["p_value"] < 0.05 else "not distinguishable"
        lines.append(f"| {c['what']} | {c['tasks']} | {c['only_a']} | {c['only_b']} | "
                     f"{c['p_value']:.3f} | {reading} |")
    return "\n".join(lines) + "\n"


def run(specs: list[str], out_dir: Path, root: Path) -> int:
    runs = []
    for spec in specs:
        label, _, path = spec.partition("=")
        if not label or not path:
            raise SystemExit(f"expected label=run_dir, got {spec!r}")
        runs.append((label, root / path))
    result = compare(runs)
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "comparison.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    md = to_markdown(result)
    (out_dir / "comparison.md").write_text(md, encoding="utf-8")
    print(md, flush=True)
    return 0
