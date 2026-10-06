"""Task definitions and safe file access.

A task has two parts:

* ``data/tasks/<id>/``  - public: ``task.json``, ``SPEC.md``, ``start/`` (the
  program to change) and ``visible/`` (example inputs and outputs).
  This is everything the model is allowed to see.
* ``data/hidden/<id>/`` - private to the verifier: ``cases/NN.in`` and
  ``cases/NN.out`` (hidden test cases) and ``reference/`` (a known good
  solution, used only to validate the task itself).
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path, PurePosixPath

TASK_ID = re.compile(r"[a-z0-9][a-z0-9-]{0,47}")
CASE_ID = re.compile(r"[0-9]{2,3}")
VISIBLE_CASE_ID = re.compile(r"v[0-9]{2,3}")  # visible example NN runs as case vNN
KINDS = ("benchmark", "security")
COMPARE_MODES = ("exact", "lines")

MAX_FILE_BYTES = 64 * 1024


class TaskError(ValueError):
    """A task definition on disk is invalid."""


@dataclass(frozen=True)
class Task:
    id: str
    kind: str
    title: str
    entry: str
    editable: tuple[str, ...]
    time_limit_s: int
    mem_limit_mb: int
    compare: str
    public_dir: Path


def safe_relpath(path: str) -> str | None:
    """Return ``path`` as a normalised relative POSIX path.

    Returns None for anything that could point outside its root directory:
    absolute paths, ``..``, backslashes, NUL bytes, hidden (dot) components.
    """
    if not path or "\\" in path or "\x00" in path:
        return None
    pure = PurePosixPath(path)
    if pure.is_absolute() or not pure.parts:
        return None
    for part in pure.parts:
        if part in ("..", ".") or part.startswith("."):
            return None
    return str(pure)


def _int_field(raw: dict, name: str, lo: int, hi: int) -> int:
    value = raw.get(name)
    if not isinstance(value, int) or isinstance(value, bool) or not lo <= value <= hi:
        raise TaskError(f"{name} must be an integer in [{lo}, {hi}]")
    return value


def load_task(tasks_root: Path, task_id: str) -> Task:
    if not TASK_ID.fullmatch(task_id):
        raise TaskError(f"invalid task id {task_id!r}")
    public_dir = tasks_root / task_id
    try:
        raw = json.loads((public_dir / "task.json").read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise TaskError(f"{task_id}: cannot read task.json: {exc}") from exc
    if raw.get("id") != task_id:
        raise TaskError(f"{task_id}: id in task.json does not match directory")
    kind = raw.get("kind")
    if kind not in KINDS:
        raise TaskError(f"{task_id}: kind must be one of {KINDS}")
    entry = safe_relpath(raw.get("entry", ""))
    if entry is None:
        raise TaskError(f"{task_id}: invalid entry")
    editable_raw = raw.get("editable")
    if not isinstance(editable_raw, list) or not editable_raw:
        raise TaskError(f"{task_id}: editable must be a non-empty list")
    editable = []
    for item in editable_raw:
        rel = safe_relpath(item) if isinstance(item, str) else None
        if rel is None:
            raise TaskError(f"{task_id}: invalid editable path {item!r}")
        editable.append(rel)
    compare = raw.get("compare", "lines")
    if compare not in COMPARE_MODES:
        raise TaskError(f"{task_id}: compare must be one of {COMPARE_MODES}")
    return Task(
        id=task_id,
        kind=kind,
        title=str(raw.get("title", task_id)),
        entry=entry,
        editable=tuple(editable),
        time_limit_s=_int_field(raw, "time_limit_s", 1, 120),
        mem_limit_mb=_int_field(raw, "mem_limit_mb", 32, 1024),
        compare=compare,
        public_dir=public_dir,
    )


def list_tasks(tasks_root: Path, kind: str | None = None) -> list[Task]:
    tasks = []
    for child in sorted(tasks_root.iterdir()):
        if child.is_dir() and TASK_ID.fullmatch(child.name):
            task = load_task(tasks_root, child.name)
            if kind is None or task.kind == kind:
                tasks.append(task)
    return tasks


def read_tree(root: Path) -> dict[str, str]:
    """Read all regular files below ``root`` as UTF-8 text, keyed by relative path.

    Symlinks and special files are refused, so a task directory can never
    pull in files from elsewhere.
    """
    files: dict[str, str] = {}
    if not root.is_dir():
        return files
    for path in sorted(root.rglob("*")):
        if path.is_symlink():
            raise TaskError(f"symlink not allowed: {path}")
        if path.is_dir():
            continue
        if not path.is_file():
            raise TaskError(f"special file not allowed: {path}")
        rel = safe_relpath(path.relative_to(root).as_posix())
        if rel is None:
            raise TaskError(f"unsafe file name: {path}")
        if path.stat().st_size > MAX_FILE_BYTES:
            raise TaskError(f"file too large: {path}")
        files[rel] = path.read_text(encoding="utf-8")
    return files


def start_files(task: Task) -> dict[str, str]:
    return read_tree(task.public_dir / "start")


def visible_examples(task: Task) -> list[tuple[str, str]]:
    examples = []
    vis = task.public_dir / "visible"
    if vis.is_dir():
        for inp in sorted(vis.glob("*.in")):
            out = inp.with_suffix(".out")
            examples.append((inp.read_text(encoding="utf-8"), out.read_text(encoding="utf-8")))
    return examples


def visible_case_ids(task: Task) -> list[str]:
    """Case ids for running a candidate on the visible examples (vNN for visible/NN.in)."""
    ids = []
    for inp in sorted((task.public_dir / "visible").glob("*.in")):
        if CASE_ID.fullmatch(inp.stem) and inp.with_suffix(".out").is_file():
            ids.append("v" + inp.stem)
    return ids


def hidden_cases(hidden_root: Path, task_id: str) -> list[str]:
    """Case ids of a task's hidden test cases (each needs both .in and .out)."""
    cases_dir = hidden_root / task_id / "cases"
    ids = []
    for inp in sorted(cases_dir.glob("*.in")):
        case_id = inp.stem
        if not CASE_ID.fullmatch(case_id):
            raise TaskError(f"{task_id}: invalid case id {case_id!r}")
        if not inp.with_suffix(".out").is_file():
            raise TaskError(f"{task_id}: case {case_id} has no .out file")
        ids.append(case_id)
    if not ids:
        raise TaskError(f"{task_id}: no hidden cases")
    return ids


def normalise_output(text: str, mode: str) -> str:
    if mode == "exact":
        return text
    lines = [line.rstrip() for line in text.replace("\r\n", "\n").split("\n")]
    while lines and lines[-1] == "":
        lines.pop()
    return "\n".join(lines)


def outputs_match(expected: str, actual: str, mode: str) -> bool:
    return normalise_output(expected, mode) == normalise_output(actual, mode)
