"""List which candidate runs on which case.

Runs on the verifier side (it reads the hidden case directory) and writes a
plain tab-separated file for the host launcher:

    task  candidate  case  time_limit_s  mem_limit_mb  entry

Every applied candidate runs on every hidden case. Model candidates also run
on the visible examples (case ids ``vNN``); those results may be shown to the
model in a repair round, hidden results never are. Candidates that already
ran earlier in the same run are skipped.
"""

from __future__ import annotations

import json
from pathlib import Path

from .tasks import (CASE_ID, TASK_ID, VISIBLE_CASE_ID, hidden_cases, list_tasks, safe_relpath,
                    visible_case_ids)

CANDIDATE_ID_CHARS = set("abcdefghijklmnopqrstuvwxyz0123456789-")


def build(tasks_root: Path, hidden_root: Path, records_dir: Path, kind: str,
          exec_dir: Path | None = None) -> list[tuple]:
    rows = []
    for task in list_tasks(tasks_root, kind):
        cases = hidden_cases(hidden_root, task.id)
        visible = visible_case_ids(task)
        for record_file in sorted((records_dir / task.id).glob("*.json")):
            record = json.loads(record_file.read_text(encoding="utf-8"))
            if record.get("status") != "APPLIED":
                continue
            cand = record_file.stem
            if not cand or not set(cand) <= CANDIDATE_ID_CHARS:
                raise ValueError(f"invalid candidate id {cand!r}")
            if exec_dir is not None and (exec_dir / task.id / cand).exists():
                continue
            run_on = cases + (visible if record.get("source", "model") == "model" else [])
            for case_id in run_on:
                rows.append((task.id, cand, case_id, task.time_limit_s, task.mem_limit_mb, task.entry))
    for task_id, cand, case_id, _, _, entry in rows:
        # The launcher interpolates these into paths and container names.
        if not (TASK_ID.fullmatch(task_id) and (CASE_ID.fullmatch(case_id) or VISIBLE_CASE_ID.fullmatch(case_id))
                and safe_relpath(entry) == entry):
            raise ValueError(f"unsafe plan row for {task_id!r}")
    return rows


def run(tasks_root: Path, hidden_root: Path, records_dir: Path, out_file: Path, kind: str,
        exec_dir: Path | None = None) -> int:
    rows = build(tasks_root, hidden_root, records_dir, kind, exec_dir)
    out_file.write_text("".join("\t".join(map(str, r)) + "\n" for r in rows), encoding="utf-8")
    print(f"plan: {len(rows)} executions", flush=True)
    return 0
