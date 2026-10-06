"""Save a LIVE run's model answers as a cassette for REPLAY.

Only answers whose mode is LIVE are accepted; anything else (MOCK, REPLAY,
baselines) is refused, so a cassette can never turn a non-model answer into
something that looks like an Apertus result. The API key is never part of a
proposal; as a second guard the copy is refused if a given secret string
appears anywhere in it.
"""

from __future__ import annotations

import json
import shutil
from pathlib import Path


def record(run_dir: Path, out_dir: Path, secret: str | None = None) -> dict:
    if out_dir.exists():
        raise SystemExit(f"{out_dir} already exists; cassettes are never overwritten")
    files = []
    for path in sorted((run_dir / "proposals").glob("*/*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        if data.get("source", "model") != "model":
            continue
        if data.get("mode") != "LIVE":
            raise SystemExit(f"{path}: mode {data.get('mode')}, only LIVE answers can be recorded")
        if secret and secret in path.read_text(encoding="utf-8"):
            raise SystemExit(f"{path}: contains the secret; refusing to record")
        files.append((path, data))
    if not files:
        raise SystemExit("no LIVE model answers in this run")
    for path, _ in files:
        target = out_dir / path.parent.name / path.name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(path, target)
    meta = {"run": run_dir.name, "answers": len(files),
            "models": sorted({str(d.get("model")) for _, d in files}),
            "served_models": sorted({str(d.get("served_model")) for _, d in files if d.get("served_model")}),
            "recorded_at": sorted({str(d.get("recorded_at")) for _, d in files}),
            "conditions": sorted({d["condition"] for _, d in files})}
    (out_dir / "CASSETTE.json").write_text(json.dumps(meta, indent=2) + "\n", encoding="utf-8")
    return meta
