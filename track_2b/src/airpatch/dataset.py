"""Export the optional Hack Apertus dataset (three JSON Lines files).

* ``evaluation.jsonl`` - one record per hidden test case (task, input, expected output)
* ``responses.jsonl``  - one record per model answer of a run, with its verdict
* ``metadata.jsonl``   - one record per task: title, tier, split, sizes, licence

Only answers from LIVE runs (or REPLAYs of them) are exported as model
responses; MOCK answers are refused, so the dataset can never contain a stub
answer presented as an Apertus response.
"""

from __future__ import annotations

import json
from pathlib import Path

from .report import load_proposals
from .tasks import hidden_cases, list_tasks, visible_examples

LICENCE = "CDLA-Permissive-2.0"


def export(tasks_root: Path, hidden_root: Path, run_dir: Path | None, out_dir: Path) -> dict:
    out_dir.mkdir(parents=True, exist_ok=True)
    tasks = list_tasks(tasks_root, "benchmark")
    n_eval = 0
    with open(out_dir / "evaluation.jsonl", "w", encoding="utf-8") as ev, \
            open(out_dir / "metadata.jsonl", "w", encoding="utf-8") as meta:
        for task in tasks:
            raw = json.loads((task.public_dir / "task.json").read_text(encoding="utf-8"))
            cases = hidden_cases(hidden_root, task.id)
            for case_id in cases:
                d = hidden_root / task.id / "cases"
                ev.write(json.dumps({"task_id": task.id, "case_id": case_id,
                                     "input": (d / f"{case_id}.in").read_text(encoding="utf-8"),
                                     "expected_output": (d / f"{case_id}.out").read_text(encoding="utf-8")}) + "\n")
                n_eval += 1
            meta.write(json.dumps({"task_id": task.id, "title": task.title, "tier": raw.get("tier"),
                                   "split": raw.get("split"), "hidden_cases": len(cases),
                                   "visible_examples": len(visible_examples(task)),
                                   "specification": (task.public_dir / "SPEC.md").read_text(encoding="utf-8"),
                                   "licence": LICENCE,
                                   "source": "written for this project; not taken from any benchmark"}) + "\n")
    n_resp = 0
    if run_dir is not None:
        verdicts = {(v["task"], v["candidate"]): v
                    for v in json.loads((run_dir / "results" / "verdicts.json").read_text(encoding="utf-8"))}
        with open(out_dir / "responses.jsonl", "w", encoding="utf-8") as resp:
            for (task_id, cand), p in sorted(load_proposals(run_dir).items()):
                if p.get("source", "model") != "model":
                    continue
                if p["mode"] not in ("LIVE", "REPLAY"):
                    raise SystemExit(f"{task_id}/{cand}: mode {p['mode']} answers are not model responses")
                v = verdicts.get((task_id, cand), {})
                resp.write(json.dumps({"task_id": task_id, "candidate": cand, "condition": p.get("condition"),
                                       "model": p.get("model"), "temperature": p.get("temperature"),
                                       "response": p.get("text"), "verdict": v.get("verdict"),
                                       "hidden_cases_passed": v.get("cases_passed"),
                                       "hidden_cases_total": v.get("cases_total"),
                                       "usage": p.get("usage"), "latency_ms": p.get("latency_ms"),
                                       "licence": LICENCE}) + "\n")
                n_resp += 1
    return {"tasks": len(tasks), "evaluation_records": n_eval, "responses": n_resp}
