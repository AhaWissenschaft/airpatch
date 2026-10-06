"""Checks for the isolation test (``make security``).

The test runs a probe program as a candidate through the normal pipeline. The
probe searches everything it can read for marker strings that exist only in
hidden test data, in expected outputs and in the verifier's source, tries to
write outside /tmp and tries to reach the network. It prints ``NO-LEAK`` only
if all of that fails.

A positive control runs the same probe with the hidden data and harness code
deliberately mounted; there it must report leaks. This shows the probe would
notice a broken boundary rather than passing by accident.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


def manifest(roots: list[Path]) -> dict[str, str]:
    """SHA-256 of every regular file below the given roots."""
    digests = {}
    for root in roots:
        for path in sorted(root.rglob("*")):
            if path.is_file() and not path.is_symlink():
                key = f"{root.name}/{path.relative_to(root).as_posix()}"
                digests[key] = hashlib.sha256(path.read_bytes()).hexdigest()
    return digests


def feedback_leaks(feedback_dir: Path, tasks_root: Path, hidden_root: Path, min_len: int = 6) -> dict:
    """Search repair-round feedback for any hidden input or expected output.

    A hidden string counts as leaked only if it is not already public (task
    specification, start code or visible examples), since e.g. "YES" may
    legitimately appear in both.
    """
    files = sorted(feedback_dir.rglob("*.json")) if feedback_dir.is_dir() else []
    leaks = []
    for fb_file in files:
        task_id = fb_file.parent.name
        text = fb_file.read_text(encoding="utf-8")
        public = "\n".join(p.read_text(encoding="utf-8", errors="replace")
                           for p in (tasks_root / task_id).rglob("*") if p.is_file())
        for case in sorted((hidden_root / task_id / "cases").glob("*")):
            for chunk in case.read_text(encoding="utf-8", errors="replace").split("\n"):
                chunk = chunk.strip()
                if len(chunk) >= min_len and chunk in text and chunk not in public:
                    leaks.append(f"{fb_file.parent.name}/{fb_file.name}: {case.name}")
    return {"feedback_files": len(files), "leaks": sorted(set(leaks))}


def check(verdicts_file: Path, before: Path, after: Path, control_output: Path) -> dict:
    verdicts = {(v["task"], v["candidate"]): v
                for v in json.loads(verdicts_file.read_text(encoding="utf-8"))}
    checks = []

    def add(name: str, ok: bool, detail: str = "") -> None:
        checks.append({"check": name, "ok": bool(ok), "detail": detail})

    probe = verdicts.get(("sec-probe", "c0"))
    add("probe ran on every hidden case and found no leak",
        probe is not None and probe["verdict"] == "PASS" and probe["cases_total"] >= 2,
        "" if probe is None else f"{probe['verdict']} {probe['cases_passed']}/{probe['cases_total']}")
    traversal = verdicts.get(("sec-traversal", "c0"))
    add("path traversal in an answer is refused before anything is written",
        traversal is not None and traversal["verdict"] == "POLICY_VIOLATION",
        "" if traversal is None else f"{traversal['verdict']}: {traversal.get('detail')}")
    b = json.loads(before.read_text(encoding="utf-8"))
    a = json.loads(after.read_text(encoding="utf-8"))
    changed = sorted(k for k in set(a) | set(b) if a.get(k) != b.get(k))
    add("tasks, hidden data, mock answers and harness code unchanged by the run",
        not changed and len(b) > 0, ", ".join(changed[:5]))
    control = control_output.read_text(encoding="utf-8", errors="replace").strip()
    found = [m for m in ("EXPECTED", "VERIFIER", "CASE-") if m in control]
    add("positive control: probe detects deliberately exposed hidden data and verifier code",
        control.startswith("LEAK") and len(found) == 3, control[:300])
    return {"ok": all(c["ok"] for c in checks), "checks": checks}


def run(verdicts_file: Path, before: Path, after: Path, control_output: Path, out_file: Path) -> int:
    result = check(verdicts_file, before, after, control_output)
    out_file.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    for c in result["checks"]:
        print(f"[{'PASS' if c['ok'] else 'FAIL'}] {c['check']}" + (f" ({c['detail']})" if c["detail"] else ""))
    print("SECURITY TEST: " + ("PASSED" if result["ok"] else "FAILED"), flush=True)
    return 0 if result["ok"] else 1
