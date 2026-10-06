"""Descriptive numbers for the recorded live runs (not part of the confirmatory analysis).

Usage (from track_2b/): python3 results/describe.py <label>=<run dir> [...] > results/usage.md

Reads only run artefacts (proposals, verdicts). Per model and condition: model calls,
reported tokens (prompt / completion / total), latency per call, verdict classes,
answers identical to the previous answer, and finish reasons. Standard library only.
"""

from __future__ import annotations

import json
import statistics
import sys
from collections import Counter
from pathlib import Path

ORDER = ["C0", "C1", "C2"]


def pct(values: list[int], q: float) -> int:
    values = sorted(values)
    return values[min(len(values) - 1, int(round(q * (len(values) - 1))))]


def describe(label: str, run: Path) -> list[str]:
    props = {}
    for f in sorted((run / "proposals").glob("*/*.json")):
        d = json.loads(f.read_text(encoding="utf-8"))
        if d.get("source", "model") == "model":
            props[(d["task"], d["candidate"])] = d
    verdicts = {(v["task"], v["candidate"]): v
                for v in json.loads((run / "results" / "verdicts.json").read_text(encoding="utf-8"))}
    models = sorted({str(p.get("served_model")) for p in props.values()})
    ledger = json.loads((run / "proposals" / "_budget.json").read_text(encoding="utf-8"))
    out = [f"## {label}", "", f"Run `{run.name}`, served model(s): {', '.join(models)}; "
           f"ledger: {ledger['calls']} calls, {ledger['tokens']} counted tokens, "
           f"{ledger.get('overruns', 0)} overruns.", "",
           "| condition | calls | errors | prompt tok | completion tok | total tok | "
           "latency median / p90 / max (s) | tries > 1 | verdicts | same as previous answer |",
           "|---|---|---|---|---|---|---|---|---|---|"]
    all_lat, all_tok = [], 0
    for cond in ORDER + ["all"]:
        ps = [(k, p) for k, p in props.items() if cond == "all" or p["condition"] == cond]
        if not ps:
            continue
        usage = [p["usage"] for _, p in ps if isinstance(p.get("usage"), dict)]
        lat = [p["latency_ms"] for _, p in ps if isinstance(p.get("latency_ms"), int)]
        errors = sum(bool(p.get("error")) for _, p in ps)
        tries = sum((p.get("tries") or 1) > 1 for _, p in ps)
        verd = Counter(verdicts[k]["verdict"] for k, _ in ps if k in verdicts)
        same = 0
        for (task, cand), p in ps:
            prev = {"r1": "c0", "r2": "r1"}.get(cand)
            if prev and (task, prev) in props and props[(task, prev)].get("text") == p.get("text"):
                same += 1
        n_rep = sum(1 for (_, c), _ in ps if c in ("r1", "r2"))
        lat_s = (f"{statistics.median(lat) / 1000:.1f} / {pct(lat, 0.9) / 1000:.1f} / {max(lat) / 1000:.1f}"
                 if lat else "-")
        out.append(f"| {cond} | {len(ps)} | {errors} | {sum(u['prompt_tokens'] for u in usage)} | "
                   f"{sum(u['completion_tokens'] for u in usage)} | {sum(u['total_tokens'] for u in usage)} | "
                   f"{lat_s} | {tries} | {', '.join(f'{k} {n}' for k, n in sorted(verd.items()))} | "
                   f"{f'{same} / {n_rep}' if n_rep else '-'} |")
        if cond == "all":
            all_lat, all_tok = lat, sum(u["total_tokens"] for u in usage)
    finish = Counter(p.get("finish_reason") for p in props.values())
    cases = Counter()
    for k in props:
        for c in verdicts.get(k, {}).get("cases", []):
            if c["status"] != "PASS":
                cases[c.get("reason") or c["status"]] += 1
    out += ["", f"Finish reasons: {dict(finish)}. Failed hidden cases by reason (all model answers): "
            f"{dict(cases.most_common())}. Tokens per call: {all_tok / max(1, len(props)):.0f}; "
            f"sum of call latencies: {sum(all_lat) / 60000:.1f} min.", ""]
    return out


def main(argv: list[str]) -> int:
    lines = ["# Live runs: calls, tokens, latency, error classes (descriptive)", ""]
    for spec in argv:
        label, _, path = spec.partition("=")
        lines += describe(label, Path(path))
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
