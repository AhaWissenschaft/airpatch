"""Build each candidate's workspace: start files plus the proposed changes.

Runs in a container without network access. Its only writable mounts are the
workspace directory and the apply-record directory, so even a bug here cannot
write into tasks, hidden cases or harness code.
"""

from __future__ import annotations

import json
import os
from pathlib import Path

from . import proposal
from .tasks import list_tasks, start_files
from .fingerprint import fingerprint


def _write_file(root: Path, rel: str, content: str) -> None:
    target = root / rel
    target.parent.mkdir(parents=True, exist_ok=True)
    root_real = os.path.realpath(root)
    if os.path.commonpath([root_real, os.path.realpath(target.parent)]) != root_real:
        raise ValueError(f"refusing to write outside workspace: {rel}")
    fd = os.open(target, os.O_WRONLY | os.O_CREAT | os.O_TRUNC | os.O_NOFOLLOW, 0o644)
    with os.fdopen(fd, "w", encoding="utf-8") as fh:
        fh.write(content)


def build_check(workspace: Path) -> dict:
    """Compile every Python file without running it."""
    for path in sorted(workspace.rglob("*.py")):
        try:
            compile(path.read_text(encoding="utf-8"), path.relative_to(workspace).as_posix(), "exec")
        except (SyntaxError, ValueError, RecursionError, MemoryError) as exc:
            return {"ok": False, "error": f"{type(exc).__name__}: {exc}",
                    "fingerprint": fingerprint(f"{type(exc).__name__}: {exc}")}
    return {"ok": True, "error": None, "fingerprint": None}


def apply_one(task, proposal_file: Path, workspace: Path) -> dict:
    record = {"task": task.id, "candidate": proposal_file.stem, "status": None, "source": None,
              "changed_paths": [], "violations": [], "error": None, "build": None}
    try:
        data = json.loads(proposal_file.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        record.update(status="INFRA_ERROR", error=f"cannot read proposal: {exc}")
        return record
    record["source"] = data.get("source", "model")
    if data.get("error") or data.get("text") is None:
        record.update(status="NO_RESPONSE", error=data.get("error") or "empty answer")
        return record
    parsed = proposal.parse(data["text"], task.editable)
    if parsed.status != "OK":
        record.update(status=parsed.status, violations=parsed.violations, error=parsed.error)
        return record
    workspace.mkdir(parents=True, exist_ok=False)
    for rel, content in start_files(task).items():
        _write_file(workspace, rel, content)
    for rel, content in parsed.files.items():
        _write_file(workspace, rel, content)
    record["changed_paths"] = sorted(parsed.files)
    record["build"] = build_check(workspace)
    record["status"] = "APPLIED" if record["build"]["ok"] else "BUILD_ERROR"
    return record


def run(tasks_root: Path, proposals_dir: Path, ws_root: Path, records_dir: Path, kind: str) -> int:
    for task in list_tasks(tasks_root, kind):
        for proposal_file in sorted((proposals_dir / task.id).glob("*.json")):
            out = records_dir / task.id
            if (out / f"{proposal_file.stem}.json").exists():
                continue  # applied in an earlier round of this run
            workspace = ws_root / task.id / proposal_file.stem
            record = apply_one(task, proposal_file, workspace)
            out.mkdir(parents=True, exist_ok=True)
            (out / f"{proposal_file.stem}.json").write_text(
                json.dumps(record, indent=2, sort_keys=True) + "\n", encoding="utf-8")
            print(f"apply {task.id}/{proposal_file.stem}: {record['status']}", flush=True)
    return 0
