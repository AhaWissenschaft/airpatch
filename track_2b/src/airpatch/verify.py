"""Decide each candidate's verdict from what was observed.

This is the only component that reads expected outputs. It runs in its own
container without network access; candidate programs never run here and
never see this code.

Isolation test marker (searched for by the security probe; must never be
readable from a candidate container): AIRPATCH-CANARY-VERIFIER-7c41
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from .fingerprint import fingerprint, final_line
from .tasks import hidden_cases, list_tasks, outputs_match, visible_case_ids

VISIBLE_KEEP_CHARS = 2000  # visible-example output kept for repair feedback

VERDICTS = ("PASS", "FAIL_TESTS", "BUILD_ERROR", "TIMEOUT", "RESOURCE_LIMIT",
            "POLICY_VIOLATION", "MALFORMED_PROPOSAL", "INFRA_ERROR")
# When cases fail in different ways, the candidate gets the most severe one.
_SEVERITY = ("INFRA_ERROR", "TIMEOUT", "RESOURCE_LIMIT", "FAIL_TESTS")


def parse_docker_time(value: str) -> int | None:
    """Docker RFC 3339 timestamp (nanosecond precision) to integer nanoseconds."""
    if not value or value.startswith("0001-"):
        return None
    value = value.rstrip("Z")
    whole, _, frac = value.partition(".")
    try:
        base = datetime.strptime(whole, "%Y-%m-%dT%H:%M:%S").replace(tzinfo=timezone.utc)
    except ValueError:
        return None
    frac = (frac + "000000000")[:9]
    return int(base.timestamp()) * 1_000_000_000 + int(frac or 0)


def read_state(path: Path) -> dict | None:
    """Parse the launcher's record: '<exit> <oom> <started> <finished>'."""
    try:
        fields = path.read_text(encoding="utf-8").split()
    except OSError:
        return None
    if len(fields) != 4:
        return None
    try:
        exit_code = int(fields[0])
    except ValueError:
        return None
    started, finished = parse_docker_time(fields[2]), parse_docker_time(fields[3])
    duration_ms = None
    if started is not None and finished is not None and finished >= started:
        duration_ms = (finished - started) // 1_000_000
    return {"exit": exit_code, "oom": fields[1] == "true", "duration_ms": duration_ms}


def judge_case(task, case_id: str, hidden_root: Path, exec_dir: Path, out_limit: int) -> dict:
    result = {"case": case_id, "status": None, "exit": None, "duration_ms": None,
              "stderr_fingerprint": None, "stderr_last_line": ""}
    state = read_state(exec_dir / f"{case_id}.state")
    out_path = exec_dir / f"{case_id}.out"
    if state is None or not out_path.is_file():
        result["status"] = "INFRA_ERROR"
        return result
    result.update(exit=state["exit"], duration_ms=state["duration_ms"])
    err = (exec_dir / f"{case_id}.err").read_text(encoding="utf-8", errors="replace") \
        if (exec_dir / f"{case_id}.err").is_file() else ""
    result["stderr_fingerprint"] = fingerprint(err)
    result["stderr_last_line"] = final_line(err)
    limit_ms = task.time_limit_s * 1000
    if out_path.stat().st_size > out_limit:
        result["status"] = "RESOURCE_LIMIT"
        result["reason"] = "output limit"
    elif state["oom"]:
        result["status"] = "RESOURCE_LIMIT"
        result["reason"] = "memory limit"
    elif state["exit"] == 124 or (state["exit"] == 137 and (state["duration_ms"] or 0) >= limit_ms):
        result["status"] = "TIMEOUT"
    elif state["exit"] == 137:
        result["status"] = "RESOURCE_LIMIT"
        result["reason"] = "killed"
    elif state["exit"] != 0:
        result["status"] = "FAIL_TESTS"
        result["reason"] = "non-zero exit"
    else:
        if case_id.startswith("v"):
            expected_path = task.public_dir / "visible" / f"{case_id[1:]}.out"
        else:
            expected_path = hidden_root / task.id / "cases" / f"{case_id}.out"
        expected = expected_path.read_text(encoding="utf-8")
        actual = out_path.read_text(encoding="utf-8", errors="replace")
        if outputs_match(expected, actual, task.compare):
            result["status"] = "PASS"
        else:
            result["status"] = "FAIL_TESTS"
            result["reason"] = "wrong output"
    if case_id.startswith("v"):
        # Visible examples are public; their output may be shown in a repair round.
        result["stdout"] = out_path.read_text(encoding="utf-8", errors="replace")[:VISIBLE_KEEP_CHARS]
        result["stderr_tail"] = "\n".join(err.splitlines()[-15:])[:VISIBLE_KEEP_CHARS]
    return result


def judge_candidate(task, candidate: str, run_dir: Path, hidden_root: Path, out_limit: int) -> dict:
    record = json.loads((run_dir / "apply" / task.id / f"{candidate}.json").read_text(encoding="utf-8"))
    verdict = {"task": task.id, "kind": task.kind, "candidate": candidate,
               "source": record.get("source", "model"),
               "apply_status": record["status"], "verdict": None, "cases": [], "visible": [],
               "cases_passed": 0, "cases_total": 0, "detail": record.get("error")}
    status = record["status"]
    if status in ("POLICY_VIOLATION", "MALFORMED_PROPOSAL", "BUILD_ERROR"):
        verdict["verdict"] = status
        verdict["detail"] = "; ".join(record.get("violations") or []) or record.get("error") \
            or (record.get("build") or {}).get("error")
        return verdict
    if status != "APPLIED":
        verdict["verdict"] = "INFRA_ERROR"
        return verdict
    exec_dir = run_dir / "exec" / task.id / candidate
    cases = [judge_case(task, c, hidden_root, exec_dir, out_limit)
             for c in hidden_cases(hidden_root, task.id)]
    verdict["cases"] = cases
    if verdict["source"] == "model":
        verdict["visible"] = [judge_case(task, c, hidden_root, exec_dir, out_limit)
                              for c in visible_case_ids(task)]
    verdict["cases_total"] = len(cases)
    verdict["cases_passed"] = sum(c["status"] == "PASS" for c in cases)
    statuses = {c["status"] for c in cases}
    if statuses == {"PASS"}:
        verdict["verdict"] = "PASS"
    else:
        verdict["verdict"] = next(s for s in _SEVERITY if s in statuses)
    return verdict


def run(tasks_root: Path, hidden_root: Path, run_dir: Path, out_dir: Path, kind: str,
        out_limit: int) -> int:
    verdicts = []
    for task in list_tasks(tasks_root, kind):
        for record_file in sorted((run_dir / "apply" / task.id).glob("*.json")):
            v = judge_candidate(task, record_file.stem, run_dir, hidden_root, out_limit)
            verdicts.append(v)
            print(f"verify {task.id}/{v['candidate']}: {v['verdict']} "
                  f"({v['cases_passed']}/{v['cases_total']} cases)", flush=True)
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "verdicts.json").write_text(json.dumps(verdicts, indent=2, sort_keys=True) + "\n",
                                           encoding="utf-8")
    return 0
