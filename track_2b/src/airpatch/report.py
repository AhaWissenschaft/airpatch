"""Summarise a run as JSON and Markdown, with the run mode stated up front.

Model answers and baseline candidates are reported side by side but never
mixed: the mode banner describes the model answers only.
"""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

BANNERS = {
    "LIVE": "LIVE MODE - new answers from model {model}, checked offline by the verifier.",
    "REPLAY": "REPLAY MODE - recorded answers (model {model}, recorded {recorded}) re-checked now. "
              "These are NOT new Apertus results.",
    "MOCK": "MOCK MODE - canned answers from a local test stub. NOT Apertus and NOT a model result.",
    "NONE": "NO MODEL - reference candidates only (task validation). No model was asked.",
}
CONDITION_ORDER = ["C0", "C1", "C2", "B0", "B1", "B2", "B3", "NEAR_MISS"]
CONDITION_LABEL = {"C0": "model, 1 try", "C1": "model, best of 3", "C2": "model + repair rounds",
                   "B0": "no change", "B1": "mutation search", "B2": "oracle",
                   "B3": "memorise examples", "NEAR_MISS": "near-miss variants"}


def load_proposals(run_dir: Path) -> dict:
    found = {}
    for path in sorted((run_dir / "proposals").glob("*/*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        found[(data["task"], data["candidate"])] = data
    return found


def _condition(v: dict, proposals: dict) -> str:
    return proposals.get((v["task"], v["candidate"]), {}).get("condition", "?")


def task_level(verdicts: list[dict], kind: str) -> dict:
    """Per-task outcome of each condition: C0, C1 (pass@k) and C2 (final after repairs)."""
    by = {(v["task"], v["candidate"]): v["verdict"] for v in verdicts if v["kind"] == kind}
    tasks = sorted({t for t, _ in by})
    out = {"tasks": len(tasks), "C0": sum(by.get((t, "c0")) == "PASS" for t in tasks)}
    samples = sorted({c for _, c in by if c.startswith("s")})
    if samples:
        out["C1_pass_at_k"] = sum(any(by.get((t, s)) == "PASS" for s in samples) for t in tasks)
        out["C1_k"] = len(samples)
    rounds = sorted({c for _, c in by if c.startswith("r")})
    if rounds:
        out["C2_final"] = sum(any(by.get((t, c)) == "PASS" for c in ["c0"] + rounds) for t in tasks)
        out["C2_rounds"] = len(rounds)
        out["C2_repaired"] = out["C2_final"] - out["C0"]
    for base in ("b0", "b1", "b2", "b3"):
        if any(c == base for _, c in by):
            out[base.upper()] = sum(by.get((t, base)) == "PASS" for t in tasks)
    return out


def summarise(verdicts: list[dict], proposals: dict, mode: str) -> dict:
    model_props = [p for p in proposals.values() if p.get("source", "model") == "model"]
    summary = {"mode": mode,
               "models": sorted({str(p["model"]) for p in model_props if p.get("model")}),
               "recorded_at": sorted({str(p["recorded_at"]) for p in model_props if p.get("recorded_at")}),
               "per_kind": {}}
    for kind in sorted({v["kind"] for v in verdicts}):
        per_cond = {}
        for cond in CONDITION_ORDER + ["?"]:
            rows = [v for v in verdicts if v["kind"] == kind and _condition(v, proposals) == cond]
            if not rows:
                continue
            counts = Counter(v["verdict"] for v in rows)
            usage = [proposals[(v["task"], v["candidate"])].get("usage") or {} for v in rows
                     if (v["task"], v["candidate"]) in proposals]
            tokens = [u["total_tokens"] for u in usage if isinstance(u.get("total_tokens"), int)]
            per_cond[cond] = {"candidates": len(rows),
                              "scored": sum(v["verdict"] != "INFRA_ERROR" for v in rows),
                              "passed": counts.get("PASS", 0),
                              "verdicts": dict(sorted(counts.items())),
                              "total_tokens": sum(tokens) if tokens else None,
                              "tokens_reported_for": len(tokens)}
        summary["per_kind"][kind] = per_cond
    summary["task_level"] = {kind: task_level(verdicts, kind) for kind in summary["per_kind"]}
    return summary


def to_markdown(summary: dict, verdicts: list[dict], proposals: dict, run_id: str) -> str:
    mode = summary["mode"]
    banner = BANNERS[mode].format(model=", ".join(summary["models"]) or "-",
                                  recorded=", ".join(summary["recorded_at"]) or "-")
    lines = [f"# AirPatch run {run_id}", "", f"> **{banner}**", ""]
    for kind, per_cond in summary["per_kind"].items():
        tl = summary["task_level"][kind]
        lines += [f"## {kind}: tasks solved (of {tl['tasks']})", "", "| condition | tasks solved |", "|---|---|"]
        labels = [("C0", "C0 model, 1 try"), ("C1_pass_at_k", f"C1 model, any of {tl.get('C1_k')} tries"),
                  ("C2_final", f"C2 model + up to {tl.get('C2_rounds')} repair rounds"),
                  ("B0", "B0 no change"), ("B1", "B1 mutation search"), ("B2", "B2 oracle"),
                  ("B3", "B3 memorise examples")]
        for key, label in labels:
            if key in tl:
                lines.append(f"| {label} | {tl[key]} / {tl['tasks']} |")
        lines += ["", "| condition | passed / scored candidates | verdicts |", "|---|---|---|"]
        for cond, s in per_cond.items():
            verdict_txt = ", ".join(f"{k} {n}" for k, n in s["verdicts"].items())
            lines.append(f"| {cond} {CONDITION_LABEL.get(cond, '')} | {s['passed']} / {s['scored']} "
                         f"| {verdict_txt} |")
        conds = [c for c in per_cond]
        tasks = sorted({v["task"] for v in verdicts if v["kind"] == kind})
        lines += ["", "| task | " + " | ".join(conds) + " |", "|---|" + "---|" * len(conds)]
        for task in tasks:
            cells = []
            for cond in conds:
                vs = [v for v in verdicts if v["task"] == task and _condition(v, proposals) == cond]
                cells.append(" ".join(f"{v['verdict']} {v['cases_passed']}/{v['cases_total']}"
                                      for v in sorted(vs, key=lambda x: x["candidate"])) or "-")
            lines.append(f"| {task} | " + " | ".join(cells) + " |")
        lines.append("")
    lines.append(f"Mode of the model answers in this run: **{mode}**. Baseline rows (B0-B3, near-miss) "
                 "involve no model.")
    return "\n".join(lines) + "\n"


def run(run_dir: Path, out_dir: Path, mode: str, run_id: str) -> int:
    verdicts = json.loads((run_dir / "results" / "verdicts.json").read_text(encoding="utf-8"))
    proposals = load_proposals(run_dir)
    model_modes = {p["mode"] for p in proposals.values() if p.get("source", "model") == "model"}
    if model_modes - {mode} or (mode == "NONE" and model_modes):
        raise SystemExit(f"model answer modes {sorted(model_modes)} do not match run mode {mode}")
    summary = summarise(verdicts, proposals, mode)
    summary["run_id"] = run_id
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n",
                                          encoding="utf-8")
    md = to_markdown(summary, verdicts, proposals, run_id)
    (out_dir / "report.md").write_text(md, encoding="utf-8")
    from .viewer import render  # local import: viewer imports this module
    (out_dir / "index.html").write_text(render(summary, verdicts, proposals, run_id), encoding="utf-8")
    print(md, flush=True)
    return 0
