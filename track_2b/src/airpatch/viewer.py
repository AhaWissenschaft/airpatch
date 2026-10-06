"""Static, offline run viewer (``runs/<id>/report/index.html``).

One self-contained HTML file: no scripts, no external fonts or images, a
Content-Security-Policy that forbids loading anything, and every piece of
model output escaped. It opens from disk on an air-gapped machine.
"""

from __future__ import annotations

import html

from .report import BANNERS, CONDITION_LABEL, CONDITION_ORDER

MODE_CLASS = {"LIVE": "live", "REPLAY": "replay", "MOCK": "mock", "NONE": "none"}
VERDICT_CLASS = {"PASS": "ok", "FAIL_TESTS": "bad", "BUILD_ERROR": "bad", "TIMEOUT": "warn",
                 "RESOURCE_LIMIT": "warn", "POLICY_VIOLATION": "bad", "MALFORMED_PROPOSAL": "bad",
                 "INFRA_ERROR": "grey"}

CSS = """
:root { --bg:#ffffff; --fg:#1d232b; --muted:#5d6670; --line:#d9dee3; --card:#f5f7f9;
        --ok:#1f7a3f; --bad:#b3261e; --warn:#8a5a00; --grey:#6b7280;
        --live:#e6f4ea; --replay:#fff4d6; --mock:#eceff3; }
@media (prefers-color-scheme: dark) {
  :root { --bg:#14181d; --fg:#e7ebef; --muted:#9aa4ae; --line:#2c333b; --card:#1b2026;
          --ok:#5cc985; --bad:#ff8a80; --warn:#f2c35b; --grey:#9ca3af;
          --live:#1d3326; --replay:#3a3115; --mock:#262c33; } }
* { box-sizing: border-box; }
body { margin:0; background:var(--bg); color:var(--fg); font:15px/1.5 system-ui, sans-serif; }
main { max-width: 1100px; margin: 0 auto; padding: 24px 16px 64px; }
h1 { font-size: 22px; margin: 0 0 12px; } h2 { font-size: 18px; margin: 28px 0 8px; }
.banner { padding: 14px 16px; border-radius: 8px; border: 1px solid var(--line); font-weight: 600; }
.banner.live { background: var(--live); } .banner.replay { background: var(--replay); }
.banner.mock, .banner.none { background: var(--mock); }
.meta { color: var(--muted); font-size: 13px; margin-top: 8px; }
.scroll { overflow-x: auto; }
table { border-collapse: collapse; width: 100%; margin: 8px 0; font-size: 14px; }
th, td { border-bottom: 1px solid var(--line); padding: 6px 8px; text-align: left; vertical-align: top; }
th { color: var(--muted); font-weight: 600; }
.v { font-weight: 600; white-space: nowrap; } .ok { color: var(--ok); } .bad { color: var(--bad); }
.warn { color: var(--warn); } .grey { color: var(--grey); }
details { background: var(--card); border: 1px solid var(--line); border-radius: 8px; margin: 8px 0; padding: 8px 12px; }
summary { cursor: pointer; font-weight: 600; }
pre { white-space: pre-wrap; word-break: break-word; font-size: 12.5px; background: var(--bg);
      border: 1px solid var(--line); border-radius: 6px; padding: 8px; max-height: 360px; overflow: auto; }
.facts li { margin: 2px 0; }
"""

FACTS = [
    "The model only writes text; it never runs code and never sees hidden test cases.",
    "Each hidden test case runs in its own container: no network, read-only file system, "
    "no capabilities, unprivileged user, CPU/memory/process limits, plain Python image without "
    "harness code.",
    "Only the verifier reads expected outputs. Repair-round feedback contains counts for hidden "
    "cases and details for visible examples only.",
    "Baselines (B0-B3) involve no model and are judged by exactly the same pipeline.",
]


def _e(value) -> str:
    return html.escape(str(value if value is not None else "-"), quote=True)


def _verdict(v: str) -> str:
    return f'<span class="v {VERDICT_CLASS.get(v, "grey")}">{_e(v)}</span>'


def _usage_table(kind: str, verdicts: list[dict], proposals: dict) -> str:
    """Model answers per condition: count, reported tokens and latency (as recorded)."""
    rows = []
    for cond in ("C0", "C1", "C2"):
        ps = [proposals[(v["task"], v["candidate"])] for v in verdicts
              if v["kind"] == kind and proposals.get((v["task"], v["candidate"]), {}).get("condition") == cond]
        if not ps:
            continue
        tokens = [p["usage"]["total_tokens"] for p in ps
                  if isinstance(p.get("usage"), dict) and isinstance(p["usage"].get("total_tokens"), int)]
        lat = sorted(p["latency_ms"] for p in ps if isinstance(p.get("latency_ms"), int))
        median = f"{lat[len(lat) // 2] / 1000:.1f} s" if lat else "-"
        rows.append(f"<tr><td>{_e(cond)} {_e(CONDITION_LABEL.get(cond, ''))}</td><td>{len(ps)}</td>"
                    f"<td>{sum(tokens) if tokens else '-'}</td><td>{median}</td></tr>")
    if not rows:
        return ""
    return ("<h2>Model answers: tokens and latency</h2><div class='scroll'><table><tr><th>condition</th>"
            "<th>answers</th><th>reported tokens</th><th>median latency</th></tr>" + "".join(rows)
            + "</table></div><p class='meta'>As recorded at the time of the live call "
              "(REPLAY shows the recorded values).</p>")


def render(summary: dict, verdicts: list[dict], proposals: dict, run_id: str) -> str:
    mode = summary["mode"]
    banner = BANNERS[mode].format(model=", ".join(summary["models"]) or "-",
                                  recorded=", ".join(summary["recorded_at"]) or "-")
    out = ["<!doctype html><html lang='en'><head><meta charset='utf-8'>",
           "<meta name='viewport' content='width=device-width, initial-scale=1'>",
           "<meta http-equiv='Content-Security-Policy' content=\"default-src 'none'; style-src 'unsafe-inline'\">",
           f"<title>AirPatch run {_e(run_id)}</title><style>{CSS}</style></head><body><main>",
           f"<h1>AirPatch run {_e(run_id)}</h1>",
           f"<div class='banner {MODE_CLASS.get(mode, 'none')}'>{_e(banner)}</div>",
           f"<div class='meta'>Models: {_e(', '.join(summary['models']) or '-')} &middot; "
           f"mode of model answers: {_e(mode)}</div>"]
    for kind, tl in summary["task_level"].items():
        out.append(f"<h2>{_e(kind)}: tasks solved</h2><div class='scroll'><table>"
                   "<tr><th>condition</th><th>tasks solved</th></tr>")
        rows = [("C0", "C0 model, 1 try"), ("C1_pass_at_k", f"C1 model, any of {tl.get('C1_k')} tries"),
                ("C2_final", f"C2 model + up to {tl.get('C2_rounds')} repair rounds"),
                ("B0", "B0 no change"), ("B1", "B1 mutation search"), ("B2", "B2 oracle"),
                ("B3", "B3 memorise examples")]
        for key, label in rows:
            if key in tl:
                out.append(f"<tr><td>{_e(label)}</td><td>{tl[key]} / {tl['tasks']}</td></tr>")
        out.append("</table></div>")
        out.append(_usage_table(kind, verdicts, proposals))
        kind_verdicts = [v for v in verdicts if v["kind"] == kind]
        conds = [c for c in CONDITION_ORDER
                 if any(proposals.get((v["task"], v["candidate"]), {}).get("condition") == c
                        for v in kind_verdicts)]
        out.append("<h2>Per task</h2><div class='scroll'><table><tr><th>task</th>"
                   + "".join(f"<th>{_e(c)}<br><small>{_e(CONDITION_LABEL.get(c, ''))}</small></th>" for c in conds)
                   + "</tr>")
        tasks = sorted({v["task"] for v in kind_verdicts})
        for task in tasks:
            cells = []
            for cond in conds:
                vs = sorted((v for v in kind_verdicts if v["task"] == task
                             and proposals.get((task, v["candidate"]), {}).get("condition") == cond),
                            key=lambda x: x["candidate"])
                c0_passed = any(v["task"] == task and v["candidate"] == "c0" and v["verdict"] == "PASS"
                                for v in kind_verdicts)
                empty = "<td class='grey'>not needed (C0 passed)</td>" if cond == "C2" and c0_passed else "<td>-</td>"
                cells.append("<td>" + "<br>".join(
                    f"{_verdict(v['verdict'])} {v['cases_passed']}/{v['cases_total']}" for v in vs) + "</td>"
                    if vs else empty)
            out.append(f"<tr><td>{_e(task)}</td>{''.join(cells)}</tr>")
        out.append("</table></div><h2>Model answers</h2>")
        for task in tasks:
            model_vs = [v for v in kind_verdicts if v["task"] == task and v.get("source", "model") == "model"]
            if not model_vs:
                continue
            out.append(f"<details><summary>{_e(task)}</summary>")
            for v in sorted(model_vs, key=lambda x: x["candidate"]):
                p = proposals.get((task, v["candidate"]), {})
                usage = (p.get("usage") or {}).get("total_tokens", "-")
                out.append(f"<p>{_e(v['candidate'])} ({_e(p.get('condition'))}): {_verdict(v['verdict'])} "
                           f"&middot; hidden cases {v['cases_passed']}/{v['cases_total']} &middot; "
                           f"latency {_e(p.get('latency_ms'))} ms &middot; tokens {_e(usage)}</p>")
                if v.get("detail"):
                    out.append(f"<p class='meta'>{_e(v['detail'])}</p>")
                if v.get("cases"):
                    out.append("<p class='meta'>hidden cases: " + " ".join(
                        f"{_e(c['case'])}:{_verdict(c['status'])}" for c in v["cases"]) + "</p>")
                out.append(f"<pre>{_e(p.get('text') or p.get('error') or '')}</pre>")
            out.append("</details>")
    out.append("<h2>How these results were produced</h2><ul class='facts'>"
               + "".join(f"<li>{_e(f)}</li>" for f in FACTS) + "</ul>")
    out.append(f"<p class='meta'>Mode of the model answers in this run: <b>{_e(mode)}</b>.</p>")
    out.append("</main></body></html>")
    return "\n".join(out) + "\n"
