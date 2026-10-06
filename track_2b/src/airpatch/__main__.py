"""Command line entry point: ``python3 -m airpatch <step> ...``.

Each step is run by the host launcher in its own container with only the
mounts it needs (see scripts/airpatch.sh).
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

from . import (apply, baselines, cassette, compare, dataset, determinism, feedback, mockllm, mutsearch,
               plan, propose, regress, report, security, validate, verify)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="airpatch")
    sub = ap.add_subparsers(dest="step", required=True)

    p = sub.add_parser("propose")
    p.add_argument("--tasks", type=Path, required=True)
    p.add_argument("--out", type=Path, required=True)
    p.add_argument("--kind", required=True)
    p.add_argument("--mode", required=True, choices=propose.MODES)
    p.add_argument("--cassette", type=Path)
    p.add_argument("--max-calls", type=int, default=int(os.environ.get("AIRPATCH_MAX_CALLS", "64")))
    p.add_argument("--max-tokens", type=int, default=int(os.environ.get("AIRPATCH_MAX_TOTAL_TOKENS", "0")) or None)
    p.add_argument("--samples", type=int, default=0)
    p.add_argument("--round", type=int, default=0)
    p.add_argument("--feedback", type=Path)
    p.add_argument("--workers", type=int, default=int(os.environ.get("AIRPATCH_MODEL_JOBS", "2")))
    p.add_argument("--only", default="")
    p.add_argument("--resume", action="store_true",
                   help="keep answers already in --out; ask only missing or failed ones")

    p = sub.add_parser("feedback")
    p.add_argument("--tasks", type=Path, required=True)
    p.add_argument("--run", type=Path, required=True)
    p.add_argument("--out", type=Path, required=True)
    p.add_argument("--kind", required=True)
    p.add_argument("--candidate", required=True)

    p = sub.add_parser("baselines")
    p.add_argument("--tasks", type=Path, required=True)
    p.add_argument("--hidden", type=Path, required=True)
    p.add_argument("--out", type=Path, required=True)
    p.add_argument("--kind", required=True)
    p.add_argument("--which", default="b0,b2,b3")
    p.add_argument("--only", default="")

    p = sub.add_parser("mutsearch")
    p.add_argument("--tasks", type=Path, required=True)
    p.add_argument("--out", type=Path, required=True)
    p.add_argument("--kind", required=True)
    p.add_argument("--only", default="")

    p = sub.add_parser("validate")
    p.add_argument("--tasks", type=Path, required=True)
    p.add_argument("--hidden", type=Path, required=True)
    p.add_argument("--verdicts", type=Path, required=True)
    p.add_argument("--out", type=Path, required=True)
    p.add_argument("--kind", default="benchmark")
    p.add_argument("--only", default="")

    p = sub.add_parser("regress")
    p.add_argument("--verdicts", type=Path, required=True)
    p.add_argument("--expectations", type=Path, required=True)

    p = sub.add_parser("apply")
    p.add_argument("--tasks", type=Path, required=True)
    p.add_argument("--proposals", type=Path, required=True)
    p.add_argument("--ws", type=Path, required=True)
    p.add_argument("--records", type=Path, required=True)
    p.add_argument("--kind", required=True)

    p = sub.add_parser("plan")
    p.add_argument("--tasks", type=Path, required=True)
    p.add_argument("--hidden", type=Path, required=True)
    p.add_argument("--records", type=Path, required=True)
    p.add_argument("--out", type=Path, required=True)
    p.add_argument("--kind", required=True)
    p.add_argument("--exec", type=Path)

    p = sub.add_parser("verify")
    p.add_argument("--tasks", type=Path, required=True)
    p.add_argument("--hidden", type=Path, required=True)
    p.add_argument("--run", type=Path, required=True)
    p.add_argument("--out", type=Path, required=True)
    p.add_argument("--kind", required=True)
    p.add_argument("--out-limit", type=int, required=True)

    p = sub.add_parser("report")
    p.add_argument("--run", type=Path, required=True)
    p.add_argument("--out", type=Path, required=True)
    p.add_argument("--mode", required=True, choices=propose.MODES + ("NONE",))
    p.add_argument("--run-id", required=True)

    p = sub.add_parser("mockllm")
    p.add_argument("--dir", type=Path, required=True)
    p.add_argument("--port", type=int, default=8080)

    p = sub.add_parser("manifest")
    p.add_argument("--out", type=Path, required=True)
    p.add_argument("roots", type=Path, nargs="+")

    p = sub.add_parser("compare")
    p.add_argument("--root", type=Path, required=True)
    p.add_argument("--out", type=Path, required=True)
    p.add_argument("runs", nargs="+")

    p = sub.add_parser("record")
    p.add_argument("--run", type=Path, required=True)
    p.add_argument("--out", type=Path, required=True)

    p = sub.add_parser("determinism")
    p.add_argument("first", type=Path)
    p.add_argument("second", type=Path)

    p = sub.add_parser("dataset")
    p.add_argument("--tasks", type=Path, required=True)
    p.add_argument("--hidden", type=Path, required=True)
    p.add_argument("--run", type=Path)
    p.add_argument("--out", type=Path, required=True)

    p = sub.add_parser("leakscan")
    p.add_argument("--feedback", type=Path, required=True)
    p.add_argument("--tasks", type=Path, required=True)
    p.add_argument("--hidden", type=Path, required=True)

    p = sub.add_parser("security-check")
    p.add_argument("--verdicts", type=Path, required=True)
    p.add_argument("--before", type=Path, required=True)
    p.add_argument("--after", type=Path, required=True)
    p.add_argument("--control", type=Path, required=True)
    p.add_argument("--out", type=Path, required=True)

    a = ap.parse_args(argv)
    only = {x for x in getattr(a, "only", "").split(",") if x} or None
    if a.step == "propose":
        return propose.run(a.tasks, a.out, a.kind, a.mode, cassette_dir=a.cassette,
                           max_calls=a.max_calls, max_tokens=a.max_tokens, samples=a.samples,
                           round_no=a.round, feedback_dir=a.feedback, workers=a.workers, only=only,
                           resume=a.resume)
    if a.step == "feedback":
        return feedback.run(a.tasks, a.run, a.out, a.kind, a.candidate)
    if a.step == "baselines":
        return baselines.run(a.tasks, a.hidden, a.out, a.kind, set(a.which.split(",")), only)
    if a.step == "mutsearch":
        return mutsearch.run(a.tasks, a.out, a.kind, only)
    if a.step == "validate":
        return validate.run(a.tasks, a.hidden, a.verdicts, a.out, a.kind, only)
    if a.step == "regress":
        return regress.run(a.verdicts, a.expectations)
    if a.step == "apply":
        return apply.run(a.tasks, a.proposals, a.ws, a.records, a.kind)
    if a.step == "plan":
        return plan.run(a.tasks, a.hidden, a.records, a.out, a.kind, a.exec)
    if a.step == "verify":
        return verify.run(a.tasks, a.hidden, a.run, a.out, a.kind, a.out_limit)
    if a.step == "report":
        return report.run(a.run, a.out, a.mode, a.run_id)
    if a.step == "mockllm":
        mockllm.serve(a.dir, a.port)
        return 0
    if a.step == "manifest":
        a.out.write_text(json.dumps(security.manifest(a.roots), indent=1, sort_keys=True) + "\n")
        return 0
    if a.step == "compare":
        return compare.run(a.runs, a.out, a.root)
    if a.step == "record":
        meta = cassette.record(a.run, a.out, os.environ.get("AIRPATCH_SECRET_GUARD") or None)
        print(json.dumps(meta, indent=2))
        return 0
    if a.step == "determinism":
        return determinism.run(a.first, a.second)
    if a.step == "dataset":
        print(json.dumps(dataset.export(a.tasks, a.hidden, a.run, a.out)))
        return 0
    if a.step == "leakscan":
        result = security.feedback_leaks(a.feedback, a.tasks, a.hidden)
        print(f"FEEDBACK LEAK SCAN: {result['feedback_files']} feedback files, "
              f"{len(result['leaks'])} hidden strings found", *result["leaks"], sep="\n")
        return 0 if not result["leaks"] else 1
    if a.step == "security-check":
        return security.run(a.verdicts, a.before, a.after, a.control, a.out)
    return 2


if __name__ == "__main__":
    sys.exit(main())
