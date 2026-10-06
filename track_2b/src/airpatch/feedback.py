"""Feedback for a repair round (condition C2), built on the verifier side.

What the model may learn about a failed answer:

* the verdict class and *how many* hidden cases passed, with counts per
  failure reason - never a hidden input, expected output, actual output or
  error message from a hidden case;
* the build error, if its own code did not compile;
* for each *visible* example (already in the prompt): pass or fail, and on
  failure the program's own output and the last lines of its error output.

The feedback files are the only thing passed from the verifier side back to
the proposer, so this module is the whole leak surface; tests check it.
"""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

from .tasks import list_tasks, visible_examples

ALLOWED_KEYS = {"task", "candidate", "verdict", "hidden_passed", "hidden_total", "hidden_failures",
                "build_error", "answer_problem", "visible"}


def build(verdict: dict, apply_record: dict, task) -> dict:
    fb = {"task": verdict["task"], "candidate": verdict["candidate"], "verdict": verdict["verdict"],
          "hidden_passed": verdict["cases_passed"], "hidden_total": verdict["cases_total"],
          "hidden_failures": dict(sorted(Counter(
              c.get("reason") or c["status"] for c in verdict["cases"] if c["status"] != "PASS").items())),
          "build_error": None, "answer_problem": None, "visible": []}
    if verdict["verdict"] == "BUILD_ERROR":
        fb["build_error"] = ((apply_record.get("build") or {}).get("error") or "")[:500]
    if verdict["verdict"] in ("MALFORMED_PROPOSAL", "POLICY_VIOLATION"):
        fb["answer_problem"] = (verdict.get("detail") or "")[:500]
    examples = visible_examples(task)
    for v in verdict.get("visible", []):
        idx = int(v["case"][1:]) - 1
        if not 0 <= idx < len(examples):
            continue
        item = {"example": idx + 1, "status": v["status"]}
        if v["status"] != "PASS":
            item.update(input=examples[idx][0], expected=examples[idx][1],
                        actual=v.get("stdout", ""), stderr_tail=v.get("stderr_tail", ""),
                        reason=v.get("reason") or v["status"])
        fb["visible"].append(item)
    assert set(fb) <= ALLOWED_KEYS
    return fb


def message(fb: dict) -> str:
    """The user message of a repair round."""
    lines = ["Your answer was checked by running the program.",
             f"Result: {fb['verdict']}."]
    if fb["hidden_total"]:
        reasons = ", ".join(f"{k}: {n}" for k, n in fb["hidden_failures"].items())
        lines.append(f"Hidden test cases passed: {fb['hidden_passed']} of {fb['hidden_total']}"
                     + (f" (failures - {reasons})." if reasons else "."))
    if fb["build_error"]:
        lines.append(f"The program does not compile: {fb['build_error']}")
    if fb["answer_problem"]:
        lines.append(f"The answer could not be used: {fb['answer_problem']}")
    for item in fb["visible"]:
        if item["status"] == "PASS":
            lines.append(f"Visible example {item['example']}: passed.")
            continue
        lines += [f"Visible example {item['example']}: failed ({item['reason']}).",
                  "Input:", "```", item["input"].rstrip("\n"), "```",
                  "Expected output:", "```", item["expected"].rstrip("\n"), "```",
                  "Your program printed:", "```", item["actual"].rstrip("\n"), "```"]
        if item["stderr_tail"].strip():
            lines += ["Error output (last lines):", "```", item["stderr_tail"].rstrip("\n"), "```"]
    lines.append("Fix the program. Answer again with the complete content of every file you "
                 "change, in the same FILE format.")
    return "\n".join(lines)


def run(tasks_root: Path, run_dir: Path, out_dir: Path, kind: str, candidate: str) -> int:
    """Write feedback for every task whose `candidate` (c0, r1, ...) did not pass."""
    verdicts = {(v["task"], v["candidate"]): v
                for v in json.loads((run_dir / "results" / "verdicts.json").read_text(encoding="utf-8"))}
    n = 0
    for task in list_tasks(tasks_root, kind):
        v = verdicts.get((task.id, candidate))
        if v is None or v["verdict"] in ("PASS", "INFRA_ERROR"):
            continue
        record = json.loads((run_dir / "apply" / task.id / f"{candidate}.json").read_text(encoding="utf-8"))
        target = out_dir / task.id
        target.mkdir(parents=True, exist_ok=True)
        (target / f"{candidate}.json").write_text(
            json.dumps(build(v, record, task), indent=2, sort_keys=True) + "\n", encoding="utf-8")
        n += 1
    print(f"feedback for {candidate}: {n} tasks need a repair round", flush=True)
    return 0
