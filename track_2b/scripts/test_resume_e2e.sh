#!/bin/sh
# End-to-end regression test for AIRPATCH_RESUME with a partial C0 step.
# Usage: scripts/test_resume_e2e.sh <airpatch checkout>    (needs Docker; make resume-test)
#
# No model can be reached: the endpoint is a dummy (127.0.0.1:9), the real key is removed
# from the environment, and the call cap equals the calls already in the ledger, so any
# new call is refused by the budget before the network is touched.
#
# Setup: a LIVE run of 3 tasks in which only `brackets` has its C0 answer (as after an
# interruption). Expected after resuming:
#   - every task has exactly one c0 record (missing ones were attempted, here refused by the cap),
#   - the existing answer is byte-identical (never asked again),
#   - the launcher did not report the step as complete while tasks were missing.
set -u
SRC=$(cd "$1" && pwd); W=$(mktemp -d); trap 'rm -rf "$W"' EXIT
git clone -q "$SRC" "$W/a" && cd "$W/a/track_2b" || exit 2
ID=20990101T000000Z-partial; R=runs/$ID-benchmark
mkdir -p "$R/proposals/brackets"; echo LIVE > "$R/MODE"
echo '{"calls": 1, "tokens": 500, "overruns": 0}' > "$R/proposals/_budget.json"
python3 - "$R/proposals/brackets/c0.json" <<'PY'
import json, sys
json.dump({"schema": 1, "task": "brackets", "candidate": "c0", "condition": "C0", "source": "model",
           "mode": "LIVE", "temperature": 0.0, "prompt_sha256": "recorded",
           "text": "FILE: main.py\n```\nprint(1)\n```\n", "usage": {"total_tokens": 500},
           "latency_ms": 1, "model": "dummy", "served_model": "dummy", "error": None,
           "recorded_at": "partial"}, open(sys.argv[1], "w"), indent=2, sort_keys=True)
PY
before=$(sha256sum "$R/proposals/brackets/c0.json" | cut -d' ' -f1)
env -u LLM_API_KEY -u LLM_NAME -u LLM_BASE_URL LLM_API_KEY=dummy-not-a-key LLM_NAME=dummy \
  LLM_BASE_URL=http://127.0.0.1:9/v1 AIRPATCH_RESUME=$ID AIRPATCH_TASKS=brackets,csvsum,roman \
  AIRPATCH_SAMPLES=0 AIRPATCH_ROUNDS=0 AIRPATCH_ALLOW_EXPERIMENT=yes AIRPATCH_MAX_CALLS=1 \
  make experiment > "$W/log" 2>&1
rc=$?
fail=""
for t in brackets csvsum roman; do
    [ "$(find "$R/proposals/$t" -name 'c0*.json' 2>/dev/null | wc -l)" -eq 1 ] || fail="$fail $t:no-single-c0"
done
[ "$(sha256sum "$R/proposals/brackets/c0.json" | cut -d' ' -f1)" = "$before" ] || fail="$fail brackets:changed"
for t in csvsum roman; do
    [ -f "$R/proposals/$t/c0.json" ] && ! grep -q '"call budget of 1 reached"' "$R/proposals/$t/c0.json" \
        && fail="$fail $t:not-refused-by-cap"
done
grep -q "keeping the recorded C0/C1 answers" "$W/log" && fail="$fail launcher-claimed-complete"
if [ -z "$fail" ]; then echo "PASS (rc=$rc): missing tasks attempted, existing answer unchanged"; exit 0; fi
echo "FAIL (rc=$rc):$fail"; grep -E "resum|answers|LIVE\]" "$W/log" | head -8; exit 1
