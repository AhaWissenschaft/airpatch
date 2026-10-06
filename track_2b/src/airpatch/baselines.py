"""Reference candidates that do not involve a model.

They go through exactly the same apply / execute / verify path as model
answers, so the verifier treats them identically:

* ``b0`` no change          - the start code as given (lower bound).
* ``b2`` oracle             - the task's reference solution (upper bound,
                              and proof that the task is solvable).
* ``b3`` memorise examples  - a program that only replays the visible
                              examples; shows the hidden cases are needed.
* ``nm1``, ``nm2`` ...      - near-miss variants: plausible but wrong
                              solutions that the hidden cases must reject.

``b1`` (a simple mutation search) lives in mutsearch.py because it executes
code and therefore runs in its own container.

This step reads ``data/hidden`` (for the oracle and near-miss variants), so it
runs on the verifier side, without network access.
"""

from __future__ import annotations

import json
from pathlib import Path

from .tasks import list_tasks, read_tree, start_files, visible_examples

SCHEMA = 1


def as_answer(files: dict[str, str]) -> str:
    """Render files in the same FILE-block format the model is asked to use."""
    parts = []
    for path, content in sorted(files.items()):
        parts.extend([f"FILE: {path}", "```", content.rstrip("\n"), "```", ""])
    return "\n".join(parts)


def memoriser(task) -> str:
    table = {inp: out for inp, out in visible_examples(task)}
    return ("import sys\n\n"
            f"ANSWERS = {table!r}\n\n"
            "sys.stdout.write(ANSWERS.get(sys.stdin.read(), ''))\n")


def record(task_id: str, candidate: str, condition: str, text: str | None, note: str = "") -> dict:
    return {"schema": SCHEMA, "task": task_id, "candidate": candidate, "condition": condition,
            "source": "baseline", "mode": "BASELINE", "text": text, "usage": None,
            "latency_ms": None, "model": None, "error": None if text is not None else note,
            "note": note}


def build(task, hidden_root: Path, which: set[str]) -> list[dict]:
    out = []
    if "b0" in which:
        out.append(record(task.id, "b0", "B0", as_answer(start_files(task))))
    if "b2" in which:
        ref = read_tree(hidden_root / task.id / "reference")
        out.append(record(task.id, "b2", "B2", as_answer(ref) if ref else None, "no reference"))
    if "b3" in which and task.entry in task.editable:
        out.append(record(task.id, "b3", "B3", as_answer({task.entry: memoriser(task)})))
    if "nm" in which:
        nm_root = hidden_root / task.id / "near_miss"
        for i, variant in enumerate(sorted(p for p in nm_root.glob("*") if p.is_dir()), 1):
            out.append(record(task.id, f"nm{i}", "NEAR_MISS", as_answer(read_tree(variant)),
                              f"near miss {variant.name}"))
    return out


def run(tasks_root: Path, hidden_root: Path, out_dir: Path, kind: str, which: set[str],
        only: set[str] | None = None) -> int:
    for task in list_tasks(tasks_root, kind):
        if only and task.id not in only:
            continue
        for rec in build(task, hidden_root, which):
            target = out_dir / task.id
            target.mkdir(parents=True, exist_ok=True)
            (target / f"{rec['candidate']}.json").write_text(
                json.dumps(rec, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(f"baselines {task.id}: {sorted(which)}", flush=True)
    return 0
