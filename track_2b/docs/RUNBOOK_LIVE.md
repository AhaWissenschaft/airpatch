# Runbook: live Apertus runs

Live runs are the only step that talks to a model. Everything else (`make
validate`, `make regress`, `make security`, `make test`, `make run` without a
key) works offline.

## Rules

- The API key is a temporary secret. Export it in the shell for the duration
  of the run; never put it into a file that is committed. `.env` is ignored by
  git, but a shell export is preferred.
- The key reaches only the `propose` container (as an environment variable).
  It is never written to proposals, logs, reports or cassettes; `make record`
  refuses to save a run if the key string appears anywhere in it.
- Every live run has a hard cap on model calls (`AIRPATCH_MAX_CALLS`) and can
  have a token cap (`AIRPATCH_MAX_TOTAL_TOKENS`; every call first reserves its
  upper bound, so parallel calls cannot together pass it). When a cap is
  reached, no further calls are made; the affected answers are reported as
  `INFRA_ERROR`, never as model failures.
- Public CI never receives a model key.

## 1. Check the setup (no model)

```bash
make doctor
make check          # unit tests, task validation, pipeline regression, isolation test
```

## 2. Configure the endpoint

```bash
export LLM_NAME="<model id from the Hack Apertus API, e.g. Apertus v1.5 70B>"
export LLM_BASE_URL="<endpoint base URL, usually ending in /v1>"
export LLM_API_KEY="<temporary key>"
```

## 3. Pilot (dev split, C0 only, small)

```bash
AIRPATCH_SPLIT=dev AIRPATCH_MAX_CALLS=20 make run
```

Check in the report that answers parse (few `MALFORMED_PROPOSAL`) and that
there is no series of `INFRA_ERROR` (endpoint problems).

## 4. Freeze the pre-registration

Commit `docs/ANALYSIS_PLAN.md` with the final task list **before** the first
test-split run. Its commit hash goes into the report.

## 5. Experiment (test split, all conditions), once per model

Calls per task: 1 (C0) + 3 (C1) + up to 2 (C2). Set the cap to tasks x 6.

```bash
AIRPATCH_SPLIT=test AIRPATCH_ALLOW_EXPERIMENT=yes AIRPATCH_MAX_CALLS=<tasks x 6> \
AIRPATCH_MODEL_JOBS=4 make experiment
```

## 6. Record and compare

```bash
make record RUN=runs/<id>-benchmark NAME=apertus-70b-<date>
make record RUN=runs/<id>-benchmark NAME=apertus-8b-<date>
make compare RUNS="8b=runs/<id>-benchmark 70b=runs/<id>-benchmark"
```

Cassettes in `data/cassettes/` make every reported number reproducible
offline: `AIRPATCH_CASSETTE=apertus-70b-<date> make run` re-checks the recorded
answers and is labelled **REPLAY** everywhere.

## 7. Clean up

```bash
unset LLM_API_KEY
```

Revoke or let the temporary key expire.
