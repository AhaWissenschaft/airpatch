# Architecture

AirPatch lets Apertus propose code changes and checks them without the model:
a deterministic pipeline runs every proposed program in isolated containers
against hidden test cases and measures the result.

## Components and data flow

```
 make run (host: POSIX shell + docker CLI; moves files, decides nothing)
   |
   |  public task: SPEC.md, start/, visible/            hidden: cases/, reference/, near_miss/
   v                                                      (never mounted into propose or candidates)
 +-----------+   answers    +---------+  workspaces  +------+  plan  +-----------------------------+
 | propose   | -----------> | apply   | -----------> | plan | -----> | execute: ONE container per  |
 | (model)   |              | (paths  |              |      |        | case, plain Python image,   |
 | LIVE/     |              |  allow- |              |      |        | no network, read-only, no   |
 | REPLAY/   |              |  list)  |              |      |        | capabilities, uid 65534,    |
 | MOCK      |              +---------+              +------+        | stdin = this case's input   |
 +-----------+                                                       +-----------------------------+
   ^      ^                                                                       | stdout, stderr,
   |      | feedback (counts for hidden cases, details for visible examples)      | exit code, time
   |      |                                                                       v
   |   +----------+          +-------------------------------------------------------------+
   |   | feedback | <------- | verify: the ONLY step that reads expected outputs; verdicts |
   |   +----------+          +-------------------------------------------------------------+
   |                                                         |
   | LLM_BASE_URL (LIVE only)                                v
   +-- Apertus endpoint                      report: report.md, summary.json, index.html (viewer)
```

| Step | Sees | Writes | Network |
|---|---|---|---|
| propose | public task files, earlier answers, feedback | answers (`proposals/`) | LIVE: model endpoint; MOCK: internal stub network; REPLAY: none |
| baselines | public task files, reference and near-miss solutions | reference candidates | none |
| mutsearch | public task files | baseline B1 | none |
| apply | public task files, answers | workspaces (one per candidate) | none |
| plan | public task files, hidden case ids | execution plan | none |
| execute | one workspace (read-only), one case input on stdin | stdout, stderr, exit code, timing | none |
| verify | everything above, expected outputs | verdicts | none |
| feedback | verdicts, visible examples | repair-round feedback | none |
| report | run directory | Markdown, JSON, HTML | none |

Every step except `execute` runs in the harness image (`docker/Dockerfile`):
the pinned Python base image plus the `airpatch` package, read-only, no
capabilities, non-root. `execute` runs the plain base image, so candidate
programs never share a file system with harness code.

## Candidates and conditions

| candidate | condition | source |
|---|---|---|
| `c0` | C0: one answer, temperature 0 | model |
| `s1..s3` | C1: independent answers, temperature 0.7 | model |
| `r1, r2` | C2: repair rounds after feedback | model |
| `b0` | no change | baseline |
| `b1` | first-order mutation search on visible examples | baseline |
| `b2` | reference solution | baseline |
| `b3` | memorise the visible examples | baseline |
| `nm1, nm2` | near-miss variants (task validation only) | baseline |

All candidates go through the same apply / execute / verify path.

## Verdicts

`PASS` (every hidden case correct), `FAIL_TESTS`, `BUILD_ERROR`, `TIMEOUT`,
`RESOURCE_LIMIT` (memory, output size, killed), `POLICY_VIOLATION` (answer
tries to write outside the editable files), `MALFORMED_PROPOSAL` (no usable
file block), `INFRA_ERROR` (endpoint failure, budget cap; not scored).

## Modes

- **LIVE**: new answers from the endpoint in `LLM_BASE_URL`.
- **REPLAY**: recorded LIVE answers (`data/cassettes/<name>`) re-checked now;
  labelled "NOT new Apertus results" in log, report and viewer.
- **MOCK**: canned answers from a local stub, for tests and demos; labelled
  "NOT Apertus".

## Target architecture

**Air-gapped** (option b of the challenge). At run time the verification
pipeline needs no network at all; the only network use is the propose step
talking to the model endpoint, which can be a local OpenAI-compatible server
(for example vLLM or llama.cpp serving Apertus weights) on the same isolated
network. Build time needs the pinned base image once; `make bundle` exports
both images for transfer to an offline machine (`docker load`).

Runtime dependencies: Docker Engine, a POSIX shell, and the model endpoint.
No Python packages beyond the standard library.
