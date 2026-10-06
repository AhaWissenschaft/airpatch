"""Baseline B1: first-order mutation search, no model involved.

For each task it tries single small edits to the start code (flip a
comparison, swap + and -, change an integer constant by one, swap and/or,
drop a ``not``) and keeps the first variant that reproduces every *visible*
example. That variant is then judged on the hidden cases like any other
candidate. It answers the question "does this task need a model at all?".

The search executes the variants, so it runs in its own container: no
network, no hidden data mounted, every variant in a subprocess with CPU,
memory and time limits.
"""

from __future__ import annotations

import ast
import json
import resource
import subprocess
import sys
import tempfile
from pathlib import Path

from .baselines import as_answer, record
from .tasks import list_tasks, outputs_match, start_files, visible_examples

MAX_VARIANTS = 400
RUN_TIMEOUT_S = 2

_COMPARE = {ast.Lt: (ast.LtE, ast.Gt), ast.LtE: (ast.Lt, ast.GtE), ast.Gt: (ast.GtE, ast.Lt),
            ast.GtE: (ast.Gt, ast.LtE), ast.Eq: (ast.NotEq,), ast.NotEq: (ast.Eq,),
            ast.In: (ast.NotIn,), ast.NotIn: (ast.In,), ast.Is: (ast.IsNot,), ast.IsNot: (ast.Is,)}
_BINOP = {ast.Add: (ast.Sub,), ast.Sub: (ast.Add,), ast.Mult: (ast.Add, ast.FloorDiv),
          ast.FloorDiv: (ast.Div, ast.Mult), ast.Div: (ast.FloorDiv,), ast.Mod: (ast.FloorDiv,)}
_BOOLOP = {ast.And: (ast.Or,), ast.Or: (ast.And,)}


class _Mutator(ast.NodeTransformer):
    """Counts mutation sites in a fixed traversal order; optionally applies one."""

    def __init__(self, target: tuple[int, int] | None = None):
        self.target = target
        self.sites: list[tuple[int, int, str]] = []  # (site, alternatives, description)
        self.applied: str | None = None

    def _site(self, n_alt: int, desc: str) -> int | None:
        site = len(self.sites)
        self.sites.append((site, n_alt, desc))
        if self.target and self.target[0] == site:
            return self.target[1]
        return None

    def visit_Compare(self, node):
        self.generic_visit(node)
        for i, op in enumerate(node.ops):
            alts = _COMPARE.get(type(op), ())
            if alts:
                pick = self._site(len(alts), f"line {node.lineno}: {type(op).__name__}")
                if pick is not None:
                    node.ops[i] = alts[pick]()
                    self.applied = f"line {node.lineno}: {type(op).__name__} -> {alts[pick].__name__}"
        return node

    def _binop(self, node):
        alts = _BINOP.get(type(node.op), ())
        if alts:
            pick = self._site(len(alts), f"line {node.lineno}: {type(node.op).__name__}")
            if pick is not None:
                self.applied = f"line {node.lineno}: {type(node.op).__name__} -> {alts[pick].__name__}"
                node.op = alts[pick]()
        return node

    def visit_BinOp(self, node):
        self.generic_visit(node)
        return self._binop(node)

    def visit_AugAssign(self, node):
        self.generic_visit(node)
        return self._binop(node)

    def visit_BoolOp(self, node):
        self.generic_visit(node)
        alts = _BOOLOP[type(node.op)]
        pick = self._site(1, f"line {node.lineno}: {type(node.op).__name__}")
        if pick is not None:
            self.applied = f"line {node.lineno}: {type(node.op).__name__} -> {alts[0].__name__}"
            node.op = alts[0]()
        return node

    def visit_UnaryOp(self, node):
        self.generic_visit(node)
        if isinstance(node.op, ast.Not):
            pick = self._site(1, f"line {node.lineno}: not")
            if pick is not None:
                self.applied = f"line {node.lineno}: drop not"
                return node.operand
        return node

    def visit_Constant(self, node):
        if isinstance(node.value, int) and not isinstance(node.value, bool):
            pick = self._site(2, f"line {node.lineno}: {node.value}")
            if pick is not None:
                new = node.value + (1 if pick == 0 else -1)
                self.applied = f"line {node.lineno}: {node.value} -> {new}"
                return ast.copy_location(ast.Constant(new), node)
        return node


def variants(source: str):
    """Yield (description, source) for every single-edit variant, in a fixed order."""
    counter = _Mutator()
    counter.visit(ast.parse(source))
    for site, n_alt, _ in counter.sites:
        for alt in range(n_alt):
            mutator = _Mutator((site, alt))
            tree = mutator.visit(ast.parse(source))
            ast.fix_missing_locations(tree)
            if mutator.applied:
                yield mutator.applied, ast.unparse(tree) + "\n"


def _limits():
    resource.setrlimit(resource.RLIMIT_CPU, (RUN_TIMEOUT_S, RUN_TIMEOUT_S))
    resource.setrlimit(resource.RLIMIT_AS, (256 << 20, 256 << 20))


def passes_visible(files: dict[str, str], task, examples) -> bool:
    with tempfile.TemporaryDirectory() as tmp:
        for rel, content in files.items():
            target = Path(tmp, rel)
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(content, encoding="utf-8")
        for inp, expected in examples:
            try:
                proc = subprocess.run([sys.executable, "-I", "-B", str(Path(tmp, task.entry))],
                                      input=inp, capture_output=True, text=True,
                                      timeout=RUN_TIMEOUT_S, preexec_fn=_limits, cwd=tmp)
            except subprocess.TimeoutExpired:
                return False
            if proc.returncode != 0 or not outputs_match(expected, proc.stdout, task.compare):
                return False
    return True


def search(task) -> tuple[dict[str, str], str]:
    files = start_files(task)
    examples = visible_examples(task)
    if not examples or task.entry not in task.editable:
        return files, "not applicable (no visible examples or entry not editable)"
    if passes_visible(files, task, examples):
        return files, "start code already matches the visible examples"
    tried = 0
    for desc, mutant in variants(files[task.entry]):
        tried += 1
        if tried > MAX_VARIANTS:
            break
        candidate = dict(files, **{task.entry: mutant})
        if passes_visible(candidate, task, examples):
            return candidate, f"variant {tried}: {desc}"
    return files, f"no single-edit variant matches the visible examples ({tried - 1 if tried > MAX_VARIANTS else tried} tried)"


def run(tasks_root: Path, out_dir: Path, kind: str, only: set[str] | None = None) -> int:
    for task in list_tasks(tasks_root, kind):
        if only and task.id not in only:
            continue
        files, note = search(task)
        rec = record(task.id, "b1", "B1", as_answer(files), note)
        target = out_dir / task.id
        target.mkdir(parents=True, exist_ok=True)
        (target / "b1.json").write_text(json.dumps(rec, indent=2, sort_keys=True) + "\n",
                                        encoding="utf-8")
        print(f"mutation search {task.id}: {note}", flush=True)
    return 0
