# Reproduce

Requirements: Docker Engine (20.10 or newer) and a POSIX shell with `make`.
The pinned base image is pulled once from Docker Hub; if it rate-limits, a
registry mirror (e.g. `mirror.gcr.io`) serves the same digest.
Linux or macOS. Disk: about 200 MB for images. No GPU.

```bash
cd track_2b
make doctor      # checks Docker, shows the isolation settings and the mode make run will use
make run         # end-to-end run; mode printed at the start and the end (REPLAY: about 10-15 min on 4 vCPUs)
```

`make run` chooses its mode automatically:

| situation | mode | meaning |
|---|---|---|
| `LLM_NAME`, `LLM_BASE_URL`, `LLM_API_KEY` set | **LIVE** | new answers from the model (quick task subset; `FULL=1` for all) |
| `AIRPATCH_CASSETTE=<name>` set, or `data/cassettes/DEFAULT` names a cassette (it does: the Apertus 70B answers) | **REPLAY** | recorded answers re-checked; NOT new results |
| neither | **MOCK** | canned stub answers; NOT a model |

Output: `runs/<id>-benchmark/report/` with `index.html` (open in a browser,
works offline), `report.md` and `summary.json`.

## All checks

```bash
make test          # unit, data and configuration tests
make validate      # every task: oracle passes; start code, memoriser, near-misses fail
make regress       # MOCK answers must give recorded verdicts; feedback leak scan
make determinism   # same answers checked twice -> identical results (about 8 min)
make security      # isolation probe + positive control
make check         # test + validate + regress + security
```

## Re-check published results without a model

The recorded live answers are in `data/cassettes/apertus-70b-20261005` and
`data/cassettes/apertus-8b-20261005` (`data/cassettes/DEFAULT` names the 70B one).

```bash
AIRPATCH_CASSETTE=apertus-70b-20261005 make run   # about 15 min on 4 vCPUs
AIRPATCH_CASSETTE=apertus-8b-20261005 make run
make compare RUNS="8b=runs/<8B replay id>-benchmark 70b=runs/<70B replay id>-benchmark"
python3 results/describe.py 8b=runs/<8B replay id>-benchmark 70b=runs/<70B replay id>-benchmark
```

The result should equal `results/comparison.md` (one oracle case of the 70B
live run hit the time limit once under load, see the technical report 5.1;
model answers are not affected). If `LLM_API_KEY` is set in your shell,
`make run` asks the model instead (LIVE) - unset it to replay.

## Air-gapped machine

```bash
make bundle                          # on a connected machine: runs/airpatch-images.tar
docker load -i airpatch-images.tar   # on the offline machine
make run                             # REPLAY/MOCK need no network at all
```

For LIVE runs offline, point `LLM_BASE_URL` at a local OpenAI-compatible
server that serves Apertus on the same isolated network.

## Useful settings

| variable | default | meaning |
|---|---|---|
| `AIRPATCH_SPLIT` | all | `dev` or `test` |
| `AIRPATCH_TASKS` | all | comma-separated task ids |
| `AIRPATCH_SAMPLES` | 3 (0 in LIVE) | C1 answers per task |
| `AIRPATCH_ROUNDS` | 2 (0 in LIVE) | C2 repair rounds |
| `AIRPATCH_MAX_CALLS` | 64 | hard cap on model calls per run |
| `AIRPATCH_MAX_TOTAL_TOKENS` | none | token cap per run; each call first reserves prompt bound + answer limit (see `propose.Budget`) |
| `AIRPATCH_MAX_TOKENS` | 2048 | answer limit per call (`max_tokens`); part of the frozen protocol - not the run's token cap |
| `AIRPATCH_JOBS` | CPUs, at most 4 | test-case containers in parallel |
| `AIRPATCH_MODEL_JOBS` | 2 | model calls in parallel |
| `AIRPATCH_CA_BUNDLE` | none | LIVE only: extra CA file for networks that re-sign TLS |
| `AIRPATCH_RESUME` | none | `make experiment` only: continue an interrupted LIVE run (`<run id>` without `-benchmark`); every answer already on disk is kept and never asked again; exactly the missing (or failed) answers of each step are asked (`make resume-test`) |
