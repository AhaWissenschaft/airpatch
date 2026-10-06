#!/bin/sh
# AirPatch host launcher.
#
# Starts one container per step and only moves files between them; every
# decision is made inside a container. What each step can see:
#
#   propose  public tasks (ro)               network: model endpoint (LIVE),
#                                             internal stub network (MOCK), none (REPLAY)
#   baselines public tasks, hidden (ro)      writes reference candidates          no network
#   mutsearch public tasks (ro)              runs start-code variants on visible
#                                             examples only                        no network
#   apply    public tasks, answers (ro)      writes workspaces + apply records    no network
#   plan     public tasks, hidden cases (ro) writes the execution plan            no network
#   execute  ONE candidate workspace (ro)    plain Python image, no harness code,
#                                             stdin = ONE hidden case input        no network
#   verify   tasks, hidden cases, run (ro)   writes verdicts                      no network
#   report   run (ro)                        writes the report                    no network
#
# Hidden data is mounted only into `plan` (to list case ids) and `verify` (the
# only step that reads expected outputs). Candidate programs never share a
# container with harness code, hidden data or another test case.
set -eu

ROOT=$(cd "$(dirname "$0")/.." && pwd)
BASE_IMAGE="python:3.12-slim@sha256:02108f5d322dd89f1c9e552442c25acb0543dfdbc455693a5599624f20d9155d"
HARNESS_IMAGE="airpatch-harness:local"
OUT_LIMIT=${AIRPATCH_OUT_LIMIT:-262144}
ERR_LIMIT=65536
UIDGID="$(id -u):$(id -g)"
# AIRPATCH_RESUME=<run id> continues an interrupted experiment in its own run directory.
RUN_ID=${AIRPATCH__RUN:-${AIRPATCH_RESUME:-"$(date -u +%Y%m%dT%H%M%SZ)-$$"}}
RESUME_ARG=""  # "--resume" when continuing an interrupted run
export AIRPATCH__RUN="$RUN_ID"
SELF="$ROOT/scripts/airpatch.sh"
split_tasks() { # dev|test -> comma-separated task ids of that split
    case "$1" in dev|test) ;; *) printf 'airpatch: split must be dev or test\n' >&2; exit 1 ;; esac
    ids=""
    for f in "$ROOT"/data/tasks/*/task.json; do
        grep -q "\"split\": *\"$1\"" "$f" && ids="${ids:+$ids,}$(basename "$(dirname "$f")")"
    done
    [ -n "$ids" ] || { printf 'airpatch: no tasks in split %s\n' "$1" >&2; exit 1; }
    printf '%s\n' "$ids"
}

ONLY=${AIRPATCH_TASKS:-}
if [ -n "${AIRPATCH_SPLIT:-}" ] && [ -z "$ONLY" ]; then
    ONLY=$(split_tasks "$AIRPATCH_SPLIT")
fi
if [ -z "${AIRPATCH_JOBS:-}" ]; then
    AIRPATCH_JOBS=$(getconf _NPROCESSORS_ONLN 2>/dev/null || echo 2)
    [ "$AIRPATCH_JOBS" -gt 4 ] && AIRPATCH_JOBS=4
fi

# Hardening shared by all harness containers.
H="--rm --read-only --cap-drop ALL --security-opt no-new-privileges --pids-limit 128 \
--memory 512m --user $UIDGID --tmpfs /tmp:rw,size=64m -e TZ=UTC -e PYTHONHASHSEED=0"

log() { printf '%s\n' "airpatch: $*" >&2; }
die() { log "$*"; exit 1; }

# The default cassette is named in data/cassettes/DEFAULT, a plain file (unlike a
# symlink it survives checkouts and archives without symlink support).
if [ -z "${AIRPATCH_CASSETTE:-}" ] && [ -f "$ROOT/data/cassettes/DEFAULT" ]; then
    AIRPATCH_CASSETTE=$(tr -d ' \t\r\n' < "$ROOT/data/cassettes/DEFAULT")
fi
case "${AIRPATCH_CASSETTE:-}" in
    .*|*[!a-z0-9.-]*) die "AIRPATCH_CASSETTE may only contain a-z 0-9 . - (and not start with .)" ;;
esac

check_docker() {
    command -v docker >/dev/null 2>&1 || die "docker is not installed"
    docker info >/dev/null 2>&1 || die "cannot reach the docker daemon (is it running, may you use it?)"
}

build_images() {
    docker image inspect "$BASE_IMAGE" >/dev/null 2>&1 || docker pull -q "$BASE_IMAGE" >/dev/null
    docker build -q --build-arg "BASE_IMAGE=$BASE_IMAGE" -t "$HARNESS_IMAGE" \
        -f "$ROOT/docker/Dockerfile" "$ROOT" >/dev/null
}

harness() {
    # shellcheck disable=SC2086  # $H is a deliberate list of options
    docker run $H "$@"
}

choose_mode() {
    if [ -n "${AIRPATCH_MODE:-}" ]; then
        printf '%s\n' "$AIRPATCH_MODE"
    elif [ -n "${LLM_NAME:-}" ] && [ -n "${LLM_BASE_URL:-}" ] && [ -n "${LLM_API_KEY:-}" ]; then
        printf 'LIVE\n'
    elif [ -n "${AIRPATCH_CASSETTE:-}" ]; then
        [ -d "$ROOT/data/cassettes/$AIRPATCH_CASSETTE" ] || die "no cassette data/cassettes/$AIRPATCH_CASSETTE"
        printf 'REPLAY\n'
    elif [ -d "$ROOT/data/cassettes/default" ]; then
        printf 'REPLAY\n'
    else
        printf 'MOCK\n'
    fi
}

banner() {
    case $1 in
        LIVE) log "MODE: LIVE - asking model '${LLM_NAME}' now; answers are checked offline." ;;
        REPLAY) log "MODE: REPLAY - re-checking RECORDED answers. These are NOT new Apertus results." ;;
        MOCK) log "MODE: MOCK - canned answers from a local test stub. NOT Apertus, NOT a model." ;;
        NONE) log "MODE: NO MODEL - reference candidates only (task validation)." ;;
        *) die "unknown mode '$1' (expected LIVE, REPLAY or MOCK)" ;;
    esac
}

propose_step() { # mode kind run [extra propose args...]
    pmode=$1 pkind=$2 prun=$3
    shift 3
    mkdir -p "$prun/feedback"
    case $pmode in
        LIVE)
            ca=""
            if [ -n "${AIRPATCH_CA_BUNDLE:-}" ]; then
                # Only for networks that re-sign TLS (corporate proxy): trust that CA too.
                [ -f "$AIRPATCH_CA_BUNDLE" ] || die "AIRPATCH_CA_BUNDLE is not a file"
                case "$AIRPATCH_CA_BUNDLE" in *[!A-Za-z0-9_./-]*) die "AIRPATCH_CA_BUNDLE: unsupported characters in path" ;; esac
                ca="-v $AIRPATCH_CA_BUNDLE:/etc/airpatch-ca.pem:ro -e SSL_CERT_FILE=/etc/airpatch-ca.pem"
            fi
            # shellcheck disable=SC2086  # $ca is an optional list of options
            harness --network bridge $ca -e LLM_NAME -e LLM_BASE_URL -e LLM_API_KEY \
                -e "AIRPATCH_RUN_ID=$RUN_ID" -e AIRPATCH_MAX_CALLS -e AIRPATCH_MAX_TOTAL_TOKENS \
                -e AIRPATCH_MAX_TOKENS -e AIRPATCH_MODEL_JOBS \
                -v "$ROOT/data/tasks:/in/tasks:ro" -v "$prun/feedback:/in/feedback:ro" -v "$prun/proposals:/out" \
                "$HARNESS_IMAGE" propose --tasks /in/tasks --out /out --kind "$pkind" --mode LIVE \
                --only "$ONLY" --feedback /in/feedback "$@" ;;
        REPLAY)
            harness --network none \
                -v "$ROOT/data/tasks:/in/tasks:ro" -v "$prun/feedback:/in/feedback:ro" \
                -v "$ROOT/data/cassettes/${AIRPATCH_CASSETTE:-default}:/in/cassette:ro" \
                -v "$prun/proposals:/out" \
                "$HARNESS_IMAGE" propose --tasks /in/tasks --out /out --kind "$pkind" --mode REPLAY \
                --cassette /in/cassette --only "$ONLY" --feedback /in/feedback "$@" ;;
        MOCK)
            net="airpatch-$RUN_ID-$pkind-$$"
            docker network create --internal "$net" >/dev/null
            docker run -d --name "$net-stub" --network "$net" --network-alias llmstub --read-only \
                --cap-drop ALL --security-opt no-new-privileges --pids-limit 64 --memory 128m \
                --user "$UIDGID" -v "$ROOT/data/mock:/in/mock:ro" \
                "$HARNESS_IMAGE" mockllm --dir /in/mock --port 8080 >/dev/null
            status=0
            harness --network "$net" -e LLM_NAME=mock -e LLM_BASE_URL=http://llmstub:8080/v1 \
                -e LLM_API_KEY=not-a-secret -v "$ROOT/data/tasks:/in/tasks:ro" \
                -v "$prun/feedback:/in/feedback:ro" -v "$prun/proposals:/out" \
                "$HARNESS_IMAGE" propose --tasks /in/tasks --out /out --kind "$pkind" --mode MOCK \
                --only "$ONLY" --feedback /in/feedback "$@" || status=$?
            docker rm -f "$net-stub" >/dev/null 2>&1 || true
            docker network rm "$net" >/dev/null 2>&1 || true
            return $status ;;
    esac
}

feedback_step() { # kind run candidate
    harness --network none -v "$ROOT/data/tasks:/in/tasks:ro" -v "$2:/in/run:ro" -v "$2/feedback:/out" \
        "$HARNESS_IMAGE" feedback --tasks /in/tasks --run /in/run --out /out --kind "$1" --candidate "$3"
}

baselines_step() { # kind run which
    harness --network none -v "$ROOT/data/tasks:/in/tasks:ro" -v "$ROOT/data/hidden:/in/hidden:ro" \
        -v "$2/proposals:/out" \
        "$HARNESS_IMAGE" baselines --tasks /in/tasks --hidden /in/hidden --out /out --kind "$1" \
        --which "$3" --only "$ONLY"
}

mutsearch_step() { # kind run
    harness --network none -v "$ROOT/data/tasks:/in/tasks:ro" -v "$2/proposals:/out" \
        "$HARNESS_IMAGE" mutsearch --tasks /in/tasks --out /out --kind "$1" --only "$ONLY"
}

apply_step() { # kind run
    harness --network none -v "$ROOT/data/tasks:/in/tasks:ro" -v "$2/proposals:/in/proposals:ro" \
        -v "$2/ws:/ws" -v "$2/apply:/records" \
        "$HARNESS_IMAGE" apply --tasks /in/tasks --proposals /in/proposals --ws /ws \
        --records /records --kind "$1"
}

plan_step() { # kind run
    harness --network none -v "$ROOT/data/tasks:/in/tasks:ro" -v "$ROOT/data/hidden:/in/hidden:ro" \
        -v "$2/apply:/in/records:ro" -v "$2/exec:/in/exec:ro" -v "$2/plan:/out" \
        "$HARNESS_IMAGE" plan --tasks /in/tasks --hidden /in/hidden --records /in/records \
        --exec /in/exec --out /out/plan.tsv --kind "$1"
}

execute_case() { # run task candidate case limit_s mem_limit_mb entry
    run=$1 task=$2 cand=$3 case_id=$4 limit=$5 mem=$6 entry=$7
    ws="$run/ws/$task/$cand"
    case $case_id in
        v*) input="$ROOT/data/tasks/$task/visible/${case_id#v}.in" ;;  # public example
        *) input="$ROOT/data/hidden/$task/cases/$case_id.in" ;;
    esac
    d="$run/exec/$task/$cand"
    name="airpatch-$RUN_ID-$task-$cand-$case_id"
    mkdir -p "$d"
    # Outer guard in case the in-container timeout is defeated.
    sh -c 'sleep "$1" & s=$!; trap "kill $s 2>/dev/null; exit 0" TERM; wait $s; docker kill "$2" >/dev/null 2>&1' \
        _ "$((limit + 15))" "$name" &
    guard=$!
    { docker run --name "$name" -i --network none --read-only --cap-drop ALL \
        --security-opt no-new-privileges --pids-limit 64 --memory "${mem}m" --memory-swap "${mem}m" \
        --cpus 1 --user 65534:65534 --tmpfs /tmp:rw,size=16m,mode=1777 -w /tmp \
        -e PYTHONHASHSEED=0 -e TZ=UTC -e LC_ALL=C.UTF-8 -v "$ws:/work:ro" \
        "$BASE_IMAGE" timeout -k 1 "$limit" python3 -I -B "/work/$entry" < "$input" \
        | head -c "$((OUT_LIMIT + 1))" > "$d/$case_id.out"; } 2>&1 \
        | head -c "$ERR_LIMIT" > "$d/$case_id.err" || true
    docker wait "$name" >/dev/null 2>&1 || true
    kill "$guard" 2>/dev/null || true
    docker inspect -f '{{.State.ExitCode}} {{.State.OOMKilled}} {{.State.StartedAt}} {{.State.FinishedAt}}' \
        "$name" > "$d/$case_id.state" 2>/dev/null || : > "$d/$case_id.state"
    docker rm -f "$name" >/dev/null 2>&1 || true
}

execute_one() { # run task candidate case limit_s memory_mb entry  (called via xargs)
    [ $# -eq 7 ] || die "bad plan row: $*"
    # The plan comes from the harness; re-check before using values in paths and names.
    case "$2$3$4" in *[!a-z0-9-]*) die "unsafe plan row: $2 $3 $4" ;; esac
    case "$5$6" in *[!0-9]*) die "unsafe limits in plan: $5 $6" ;; esac
    case "$7" in /*|*..*|*[!A-Za-z0-9_./-]*) die "unsafe entry in plan: $7" ;; esac
    execute_case "$@" < /dev/null
}

execute_step() { # run
    total=$(wc -l < "$1/plan/plan.tsv" | tr -d ' ')
    if [ "$total" -gt 0 ]; then
        tr '\t' ' ' < "$1/plan/plan.tsv" | xargs -P "$AIRPATCH_JOBS" -n 6 "$SELF" _exec "$1"
    fi
    log "executed $total hidden cases ($AIRPATCH_JOBS at a time), each in its own container"
}

verify_step() { # kind run
    harness --network none -v "$ROOT/data/tasks:/in/tasks:ro" -v "$ROOT/data/hidden:/in/hidden:ro" \
        -v "$2:/in/run:ro" -v "$2/results:/out" \
        "$HARNESS_IMAGE" verify --tasks /in/tasks --hidden /in/hidden --run /in/run --out /out \
        --kind "$1" --out-limit "$OUT_LIMIT"
}

report_step() { # mode run
    harness --network none -v "$2:/in/run:ro" -v "$2/report:/out" \
        "$HARNESS_IMAGE" report --run /in/run --out /out --mode "$1" --run-id "$RUN_ID"
}

pipeline() { # kind mode candidates... -> prints run directory
    kind=$1 mode=$2
    shift 2
    run="$ROOT/runs/$RUN_ID-$kind"
    mkdir -p "$run/proposals" "$run/ws" "$run/apply" "$run/plan" "$run/exec" "$run/results" "$run/report"
    printf '%s\n' "$mode" > "$run/MODE"
    which=""
    model=no
    for c in "$@"; do
        case $c in
            model) model=yes
                   # On resume, answers already on disk are kept; only missing ones are asked.
                   propose_step "$mode" "$kind" "$run" --samples "$SAMPLES" $RESUME_ARG >&2 ;;
            b1) mutsearch_step "$kind" "$run" >&2 ;;
            b0|b2|b3|nm) which="${which:+$which,}$c" ;;
            *) die "unknown candidate source $c" ;;
        esac
    done
    [ -z "$which" ] || baselines_step "$kind" "$run" "$which" >&2
    set -- "$kind" "$mode"
    apply_step "$1" "$run" >&2
    plan_step "$1" "$run" >&2
    execute_step "$run"
    verify_step "$1" "$run" >&2
    k=1
    while [ "$model" = yes ] && [ "$k" -le "$ROUNDS" ]; do
        prev=c0
        [ "$k" -gt 1 ] && prev="r$((k - 1))"
        feedback_step "$1" "$run" "$prev" >&2
        propose_step "$2" "$1" "$run" --round "$k" $RESUME_ARG >&2
        ls "$run"/proposals/*/"r$k.json" >/dev/null 2>&1 || break
        log "repair round $k"
        apply_step "$1" "$run" >&2
        plan_step "$1" "$run" >&2
        execute_step "$run"
        verify_step "$1" "$run" >&2
        k=$((k + 1))
    done
    report_step "$2" "$run" >&2
    printf '%s\n' "$run"
}

manifest() { # out-file
    harness --network none -v "$ROOT/data/tasks:/in/tasks:ro" -v "$ROOT/data/hidden:/in/hidden:ro" \
        -v "$ROOT/data/mock:/in/mock:ro" -v "$ROOT/src:/in/src:ro" -v "$ROOT/scripts:/in/scripts:ro" \
        -v "$(dirname "$1"):/out" \
        "$HARNESS_IMAGE" manifest --out "/out/$(basename "$1")" /in/tasks /in/hidden /in/mock /in/src /in/scripts
}

set_conditions() { # mode -> SAMPLES, ROUNDS (C1 answers per task, C2 repair rounds)
    case $1 in
        LIVE) dflt_samples=0 dflt_rounds=0 ;;  # a live run is C0 only unless asked
        *) dflt_samples=3 dflt_rounds=2 ;;
    esac
    SAMPLES=${AIRPATCH_SAMPLES:-$dflt_samples}
    ROUNDS=${AIRPATCH_ROUNDS:-$dflt_rounds}
    case "$SAMPLES$ROUNDS" in *[!0-9]*) die "AIRPATCH_SAMPLES and AIRPATCH_ROUNDS must be integers" ;; esac
}

op_run() {
    check_docker
    build_images
    mode=$(choose_mode)
    set_conditions "$mode"
    log "conditions: C0 + C1 ($SAMPLES answers/task) + C2 ($ROUNDS repair rounds)"
    if [ "$mode" = LIVE ] && [ -z "$ONLY" ] && [ "${FULL:-0}" != 1 ] && [ -f "$ROOT/data/quick_tasks.txt" ]; then
        # A live run asks the model once per task; by default only the quick subset.
        ONLY=$(grep -v '^#' "$ROOT/data/quick_tasks.txt" | tr -s '\n' ',' | sed 's/,$//')
        log "LIVE quick subset ($ONLY); use FULL=1 for all tasks"
    fi
    if [ "$mode" = MOCK ] && [ -z "$ONLY" ]; then
        # The canned stub answers exist for the dev split only.
        ONLY=$(split_tasks dev)
        log "MOCK runs the dev split (the tasks that have canned stub answers)"
    fi
    if [ "$mode" = REPLAY ] && [ -z "$ONLY" ]; then
        # Replay exactly the tasks the cassette has answers for.
        cas="$ROOT/data/cassettes/${AIRPATCH_CASSETTE:-default}"
        ONLY=$(for d in "$cas"/*/; do [ -f "$d/c0.json" ] && basename "$d"; done | tr '\n' ',' | sed 's/,$//')
        [ -n "$ONLY" ] || die "cassette $cas has no answers"
    fi
    banner "$mode"
    run=$(pipeline benchmark "$mode" model b0 b1 b2 b3)
    banner "$mode"
    log "report: ${run#"$ROOT/"}/report/report.md"
}

op_validate() {
    check_docker
    build_images
    SAMPLES=0 ROUNDS=0
    banner NONE
    run=$(pipeline benchmark NONE b0 b1 b2 b3 nm)
    harness --network none -v "$ROOT/data/tasks:/in/tasks:ro" -v "$ROOT/data/hidden:/in/hidden:ro" \
        -v "$run/results:/in/results:ro" -v "$run/report:/out" \
        "$HARNESS_IMAGE" validate --tasks /in/tasks --hidden /in/hidden \
        --verdicts /in/results/verdicts.json --out /out/validation.json --only "$ONLY"
}

op_record() { # RUN=runs/<id>-benchmark NAME=<cassette name>
    [ -n "${RUN:-}" ] && [ -n "${NAME:-}" ] || die "usage: make record RUN=runs/<run> NAME=<name>"
    case "$NAME" in *[!a-z0-9.-]*) die "NAME may only contain a-z 0-9 . -" ;; esac
    check_docker
    build_images
    [ -d "$ROOT/$RUN/proposals" ] || die "no such run: $RUN"
    mkdir -p "$ROOT/data/cassettes"
    [ ! -e "$ROOT/data/cassettes/$NAME" ] || die "cassette $NAME exists; cassettes are never overwritten"
    # The key itself is only used as a guard string; it is never written anywhere.
    # Passed by name, so the value never appears on a command line (process list).
    AIRPATCH_SECRET_GUARD=${LLM_API_KEY:-}
    export AIRPATCH_SECRET_GUARD
    harness --network none -e AIRPATCH_SECRET_GUARD -v "$ROOT/$RUN:/in/run:ro" \
        -v "$ROOT/data/cassettes:/out" \
        "$HARNESS_IMAGE" record --run /in/run --out "/out/$NAME"
    unset AIRPATCH_SECRET_GUARD
    log "recorded cassette data/cassettes/$NAME (replay with AIRPATCH_CASSETTE=$NAME)"
}

op_compare() { # RUNS="label=runs/<id>-benchmark label2=..."
    [ -n "${RUNS:-}" ] || die "usage: make compare RUNS=\"8b=runs/<id>-benchmark 70b=runs/<id>-benchmark\""
    check_docker
    build_images
    out="$ROOT/runs/$RUN_ID-comparison"
    mkdir -p "$out"
    # shellcheck disable=SC2086  # RUNS is a list of label=path words
    harness --network none -v "$ROOT/runs:/in/runs:ro" -v "$out:/out" \
        "$HARNESS_IMAGE" compare --root /in --out /out $RUNS
}

op_experiment() {
    # The full live measurement: all tasks, C0 + C1 + C2. Asks the model many
    # times, so it needs an explicit go-ahead in addition to the LLM_* settings.
    [ "${AIRPATCH_ALLOW_EXPERIMENT:-}" = yes ] || die "set AIRPATCH_ALLOW_EXPERIMENT=yes to start the full live experiment"
    [ "$(choose_mode)" = LIVE ] || die "the experiment needs LLM_NAME, LLM_BASE_URL and LLM_API_KEY"
    : "${AIRPATCH_MAX_CALLS:?set AIRPATCH_MAX_CALLS (hard cap on model calls for this run)}"
    export AIRPATCH_MAX_CALLS
    check_docker
    build_images
    SAMPLES=${AIRPATCH_SAMPLES:-3} ROUNDS=${AIRPATCH_ROUNDS:-2}
    if [ -n "${AIRPATCH_RESUME:-}" ]; then
        # Continue an interrupted run: model answers already received are kept unchanged
        # (and the call/token ledger with them); every derived step is redone from scratch.
        case "$AIRPATCH_RESUME" in *[!A-Za-z0-9-]*) die "AIRPATCH_RESUME: not a run id" ;; esac
        [ "$RUN_ID" = "$AIRPATCH_RESUME" ] || die "AIRPATCH_RESUME and AIRPATCH__RUN differ"
        old="$ROOT/runs/$RUN_ID-benchmark"
        [ -f "$old/proposals/_budget.json" ] || die "no interrupted run $RUN_ID with model answers"
        [ "$(cat "$old/MODE" 2>/dev/null)" = LIVE ] || die "run $RUN_ID is not a LIVE run"
        # Case containers left over from the interrupted run would block their names.
        docker ps -aq --filter "name=^airpatch-$RUN_ID-" | xargs -r docker rm -f >/dev/null 2>&1 || true
        rm -rf "$old/ws" "$old/apply" "$old/plan" "$old/exec" "$old/results" "$old/report" "$old/feedback"
        RESUME_ARG=--resume
        log "resuming run $RUN_ID ($(cat "$old/proposals/_budget.json"))"
    fi
    banner LIVE
    log "experiment: all tasks, C0 + C1 ($SAMPLES) + C2 ($ROUNDS rounds), cap $AIRPATCH_MAX_CALLS calls"
    run=$(pipeline benchmark LIVE model b0 b1 b2 b3)
    log "report: ${run#"$ROOT/"}/report/report.md"
    log "next: make record RUN=${run#"$ROOT/"} NAME=<model>-<date>"
}

op_determinism() {
    # E1: the same answers (MOCK stub, dev split) checked twice must give identical results.
    check_docker
    build_images
    SAMPLES=3 ROUNDS=2
    [ -n "$ONLY" ] || ONLY=$(split_tasks dev)
    base_id=$RUN_ID
    RUN_ID="$base_id-a"
    first=$(pipeline benchmark MOCK model b0 b1 b2 b3)
    RUN_ID="$base_id-b"
    AIRPATCH_JOBS=1 second=$(pipeline benchmark MOCK model b0 b1 b2 b3)
    RUN_ID=$base_id
    harness --network none -v "$first/results:/in/a:ro" -v "$second/results:/in/b:ro" \
        "$HARNESS_IMAGE" determinism /in/a/verdicts.json /in/b/verdicts.json
}

op_dataset() { # [RUN=runs/<id>-benchmark] -> runs/dataset/*.jsonl for the optional HF dataset
    check_docker
    build_images
    out="$ROOT/runs/dataset"
    rm -rf "$out" && mkdir -p "$out"
    if [ -n "${RUN:-}" ]; then
        [ -d "$ROOT/$RUN/results" ] || die "no such run: $RUN"
        harness --network none -v "$ROOT/data/tasks:/in/tasks:ro" -v "$ROOT/data/hidden:/in/hidden:ro" \
            -v "$ROOT/$RUN:/in/run:ro" -v "$out:/out" \
            "$HARNESS_IMAGE" dataset --tasks /in/tasks --hidden /in/hidden --run /in/run --out /out
    else
        harness --network none -v "$ROOT/data/tasks:/in/tasks:ro" -v "$ROOT/data/hidden:/in/hidden:ro" \
            -v "$out:/out" "$HARNESS_IMAGE" dataset --tasks /in/tasks --hidden /in/hidden --out /out
    fi
    log "wrote runs/dataset/ (upload to Hugging Face is a manual step)"
}

op_bundle() {
    # Air-gap transfer: both images in one tar file. On the offline machine:
    #   docker load -i airpatch-images.tar && make run
    check_docker
    build_images
    mkdir -p "$ROOT/runs"
    docker save -o "$ROOT/runs/airpatch-images.tar" "$BASE_IMAGE" "$HARNESS_IMAGE"
    log "wrote runs/airpatch-images.tar ($(du -m "$ROOT/runs/airpatch-images.tar" | cut -f1) MB)"
}

op_regress() {
    # The canned MOCK answers belong to the dev split.
    check_docker
    build_images
    SAMPLES=3 ROUNDS=2
    [ -n "$ONLY" ] || ONLY=$(split_tasks dev)
    banner MOCK
    run=$(pipeline benchmark MOCK model b0 b2 b3)
    harness --network none -v "$run/results:/in/results:ro" -v "$ROOT/data/mock:/in/mock:ro" \
        "$HARNESS_IMAGE" regress --verdicts /in/results/verdicts.json \
        --expectations /in/mock/expectations.json
    harness --network none -v "$run/feedback:/in/feedback:ro" -v "$ROOT/data/tasks:/in/tasks:ro" \
        -v "$ROOT/data/hidden:/in/hidden:ro" \
        "$HARNESS_IMAGE" leakscan --feedback /in/feedback --tasks /in/tasks --hidden /in/hidden
}

op_expected() {
    # Authoring tool: write missing expected outputs by running each task's
    # reference solution (hardened container, no network). REGEN=1 overwrites.
    check_docker
    docker image inspect "$BASE_IMAGE" >/dev/null 2>&1 || docker pull -q "$BASE_IMAGE" >/dev/null
    n=0
    for ref in "$ROOT"/data/hidden/*/reference; do
        [ -d "$ref" ] || continue
        task=$(basename "$(dirname "$ref")")
        entry=$(sed -n 's/.*"entry": *"\([^"]*\)".*/\1/p' "$ROOT/data/tasks/$task/task.json" | head -n 1)
        for input in "$ROOT/data/hidden/$task/cases/"*.in "$ROOT/data/tasks/$task/visible/"*.in; do
            [ -f "$input" ] || continue
            out="${input%.in}.out"
            [ -f "$out" ] && [ "${REGEN:-0}" != 1 ] && continue
            docker run --rm -i --network none --read-only --cap-drop ALL \
                --security-opt no-new-privileges --pids-limit 64 --memory 256m --user 65534:65534 \
                --tmpfs /tmp:rw,size=16m,mode=1777 -w /tmp -e PYTHONHASHSEED=0 -e TZ=UTC \
                -e LC_ALL=C.UTF-8 -v "$ref:/work:ro" "$BASE_IMAGE" timeout -k 1 20 \
                python3 -I -B "/work/$entry" < "$input" > "$out" || die "reference failed: $task $(basename "$input")"
            n=$((n + 1))
        done
    done
    log "wrote $n expected outputs"
}

op_security() {
    check_docker
    build_images
    sec="$ROOT/runs/$RUN_ID-isolation"
    mkdir -p "$sec"
    log "isolation test: candidate probes for hidden data, expected outputs and verifier code"
    SAMPLES=0 ROUNDS=0
    banner MOCK
    manifest "$sec/before.json"
    run=$(pipeline security MOCK model)
    manifest "$sec/after.json"
    # Positive control: the same probe, with hidden data and harness code deliberately mounted.
    docker run --rm -i --network none --read-only --cap-drop ALL --security-opt no-new-privileges \
        --pids-limit 64 --memory 256m --user 65534:65534 --tmpfs /tmp:rw,size=16m,mode=1777 -w /tmp \
        -v "$run/ws/sec-probe/c0:/work:ro" -v "$ROOT/data/hidden:/exposed/hidden:ro" \
        -v "$ROOT/src:/exposed/src:ro" "$BASE_IMAGE" timeout -k 1 60 python3 -I -B /work/main.py \
        < "$ROOT/data/hidden/sec-probe/cases/01.in" > "$sec/control.out" 2>&1 || true
    harness --network none -v "$run/results:/in/results:ro" -v "$sec:/sec" \
        "$HARNESS_IMAGE" security-check --verdicts /in/results/verdicts.json \
        --before /sec/before.json --after /sec/after.json --control /sec/control.out \
        --out /sec/security_report.json
}

op_test() {
    check_docker
    build_images
    harness --network none -e PYTHONPATH=/src -e AIRPATCH_DATA=/data -v "$ROOT/src:/src:ro" \
        -v "$ROOT/data:/data:ro" -v "$ROOT/scripts:/scripts:ro" -w /src --entrypoint python3 "$HARNESS_IMAGE" \
        -m unittest discover -s /src/tests -t /src
}

op_doctor() {
    check_docker
    log "docker server: $(docker version -f '{{.Server.Version}} {{.Server.Os}}/{{.Server.Arch}}')"
    log "base image (pinned): $BASE_IMAGE"
    log "mode that 'make run' would use: $(choose_mode)"
    log "candidate containers: --network none --read-only --cap-drop ALL no-new-privileges, uid 65534,"
    log "  pids 64, memory per task, 1 cpu, /tmp tmpfs 16m, one container per hidden case"
    log "network: only the propose step in LIVE mode can reach LLM_BASE_URL"
}

op_clean() {
    rm -rf "$ROOT/runs"
    if command -v docker >/dev/null 2>&1; then
        docker ps -aq --filter "name=^airpatch-" | xargs -r docker rm -f >/dev/null 2>&1 || true
        docker network ls -q --filter "name=^airpatch-" | xargs -r docker network rm >/dev/null 2>&1 || true
    fi
    log "removed runs/ and leftover airpatch containers and networks"
}

case "${1:-run}" in
    run) op_run ;;
    validate) op_validate ;;
    regress) op_regress ;;
    determinism) op_determinism ;;
    bundle) op_bundle ;;
    dataset) op_dataset ;;
    record) op_record ;;
    compare) op_compare ;;
    experiment) op_experiment ;;
    expected) op_expected ;;
    _exec) shift; execute_one "$@" ;;
    security) op_security ;;
    test) op_test ;;
    doctor) op_doctor ;;
    clean) op_clean ;;
    *) die "usage: $0 run|validate|regress|determinism|security|test|experiment|record|compare|bundle|dataset|expected|doctor|clean" ;;
esac
