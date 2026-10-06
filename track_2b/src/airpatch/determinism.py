"""Experiment E1: does checking the same answers twice give the same result?

Compares two runs' verdicts field by field, ignoring only measured times.

One outcome is hardware-dependent by nature: a runaway program that both
loops and allocates memory hits whichever limit it reaches first, so it can
end as TIMEOUT on one machine and RESOURCE_LIMIT (memory) on another. Both
are reported as they happened; for this comparison they count as the same
outcome ("a limit was exceeded"), and the number of such cases is printed.
"""

from __future__ import annotations

import json
from pathlib import Path

IGNORED = {"duration_ms"}
LIMITS = {"TIMEOUT", "RESOURCE_LIMIT"}


def _strip(value):
    if isinstance(value, dict):
        out = {k: _strip(v) for k, v in value.items() if k not in IGNORED}
        if out.get("status") in LIMITS:
            out["status"] = "LIMIT"
            out.pop("exit", None)
            out.pop("reason", None)
        if out.get("verdict") in LIMITS:
            out["verdict"] = "LIMIT"
        return out
    if isinstance(value, list):
        return [_strip(v) for v in value]
    return value


def compare(a: list[dict], b: list[dict]) -> tuple[list[str], int]:
    ka = {(v["task"], v["candidate"]): _strip(v) for v in a}
    kb = {(v["task"], v["candidate"]): _strip(v) for v in b}
    diffs = [f"only in first run: {k}" for k in sorted(set(ka) - set(kb))]
    diffs += [f"only in second run: {k}" for k in sorted(set(kb) - set(ka))]
    for key in sorted(set(ka) & set(kb)):
        if ka[key] != kb[key]:
            diffs.append(f"{key[0]}/{key[1]}: {ka[key]['verdict']} vs {kb[key]['verdict']} (details differ)")
    # Pair candidates by key (not by position), so differing candidate sets cannot misalign.
    by_b = {(v["task"], v["candidate"]): v for v in b}
    swaps = sum(1 for va in a if (va["task"], va["candidate"]) in by_b
                for ca, cb in zip(va["cases"], by_b[(va["task"], va["candidate"])]["cases"])
                if ca["status"] in LIMITS and ca["status"] != cb["status"])
    return diffs, swaps


def run(first: Path, second: Path) -> int:
    a = json.loads(first.read_text(encoding="utf-8"))
    b = json.loads(second.read_text(encoding="utf-8"))
    diffs, limit_swaps = compare(a, b)
    cases = sum(len(v["cases"]) + len(v.get("visible", [])) for v in a)
    for d in diffs:
        print("DIFFERENT:", d)
    print(f"DETERMINISM: {'PASSED' if not diffs else 'FAILED'} - {len(a)} candidates, {cases} case results "
          f"compared, {len(diffs)} differences; {limit_swaps} case(s) hit a different resource limit "
          f"first (TIMEOUT vs memory), counted as the same outcome", flush=True)
    return 0 if not diffs else 1
