# Post-evaluation audit

Scope: the AirPatch code after the scientific evaluation was frozen. The audit changed nothing that is
measured. The recorded Apertus 8B and 70B answers, the tasks, the hidden cases, the analysis and the
reported results are the ones produced at evaluation time.

Commit identifiers below refer to the project's development history. The public repository is a single
snapshot of the final state (see the README).

| | |
|---|---|
| Frozen analysis plan | `0515deb` |
| Frozen evaluation (code, data, recorded answers, results) | `8bb67bc` |
| Final state (this snapshot) | after post-evaluation hardening |
| Files unchanged since the frozen evaluation | parser (`proposal.py`), `verify.py`, `feedback.py`, `tasks.py`, `apply.py`, `plan.py`, `mutsearch.py`, `compare.py`, `stats.py`, `report.py`, `fingerprint.py`, `docker/`, `data/tasks`, `data/hidden`, both recorded cassettes, `results/` |
| Prompt construction | unchanged; a unit test checks that the recorded prompt hashes of all 320 C0/C1 answers match the current code |

## Method

Manual review of all 24 modules, the launcher, the Dockerfile, CI and the documentation, plus static tools
(ruff, pyflakes, bandit, pyright, shellcheck), and an independent automated review of the same code. Every
finding is classified:

- **A** - not measurement-relevant; may be fixed
- **B** - potentially measurement-relevant; documented, fixed only where it cannot change recorded results
- **C** - frozen scientific logic; not changed

## Findings fixed after the evaluation (class A unless stated)

| ID | Area | Finding | Fix |
|---|---|---|---|
| R1 (B) | Resume | Resuming an interrupted live run treated a whole step as complete as soon as any one task had its answer on disk, so unfinished tasks could be dropped silently (exit 0, smaller denominator in `make compare`). Reproduced with an end-to-end test before the fix | `propose.run(resume=True)`: every valid answer on disk is kept and never asked again; exactly the missing or failed answers are asked. Tests `test_resume.py` (0/N, 1/N, N-1/N, N/N present, partial step with samples, repeated resume, repair round, failed answer, unchanged default) and `make resume-test` |
| A1 | Secrets | `make record` passed the key guard as a value on the Docker command line (visible in the local process list while it ran; never written to files) | passed by name |
| A2 | Packaging | default cassette was a symlink, which some checkouts turn into a file, making `make run` silently fall back to MOCK | plain file `data/cassettes/DEFAULT` |
| A3 | Security | `AIRPATCH_CASSETTE` was used in a mount path without validation | name validated |
| A4 | Resume | containers left over from an interrupted run could block reuse of their names | removed before resuming |
| A5 | Dead code | unused constant and helper functions | removed |
| A6 | Determinism check | case pairing by position for the "different limit first" count | paired by key |
| A7 | Test stub | negative `Content-Length` read to EOF | rejected with 400 |
| A8 | Tests | missing tests for REPLAY guards, API client retries, mutation search, visible-example numbering, launcher secret handling, recorded prompts | 29 tests added (89 in total) |
| A9 | Resources | unclosed sockets: test servers not closed; the API client did not release the connection of an HTTP error | closed; test |
| A10 | Docs | ambiguous `AIRPATCH_MAX_TOKENS` (per-answer limit, not the run cap), threat model details | REPRODUCE, THREAT_MODEL |
| A11 | CI | `actions/checkout` not pinned | pinned to a commit SHA |

**Were the frozen runs affected by R1?** No. Checked from the recorded cassettes and result files: both
models have 40/40 tasks with C0 and three C1 answers (120), r1 for all 38 tasks that needed a repair and r2
for all 38 that still failed, 0 `INFRA_ERROR`, call ledger = number of answers (236), token ledger = sum of
reported usage. The 70B run was resumed once: all 160 C0/C1 answers had been written (07:58:54 UTC) before
the interruption (08:03:31 UTC). The 8B run was never resumed.

## Documented, not changed (B)

| ID | Finding | In the recorded runs |
|---|---|---|
| B1 | Answers and the call ledger are written after all calls of a step; an interruption during the calls loses answers already paid for and the ledger undercounts | did not occur |
| B2 | HTTP retries of one call: a request processed by the server but answered too late may cost tokens that are not counted; latency covers the last attempt only | 0 of 480 calls needed a retry |
| B3 | Time limits are measured including container start-up; under heavy host load a case can exceed its limit by start-up delay alone | once in about 9,900 case executions (a reference-solution case, `league`, 70B run); passes in every replay; no model answer affected |
| B4 | Replaying repair rounds needs the earlier round's verdicts to recur exactly (the feedback is part of the prompt hash); otherwise the replayed answer becomes a visible `INFRA_ERROR` | 0 occurrences in 6 full replays |
| B5 | The per-run report counts `INFRA_ERROR` as not solved; `make compare` (the confirmatory analysis) excludes it | 0 `INFRA_ERROR` |
| B6 | Resume keeps answers on disk without checking model id or prompt hash; resuming with changed settings would mix answers | the 70B resume used the same model (served model id recorded in all answers) and the same prompts |
| B7 | `make compare` scores the tasks that have a C0 answer and does not check them against the expected task list | all 40 expected tasks present in every condition |
| B8 | Harness containers run as the invoking user (root if started as root), still without capabilities and read-only; candidate programs always run as uid 65534 | - |
| B9 | The LIVE propose container has general network egress (it holds only public task files and harness code) | - |

## Frozen scientific logic (C), not changed

Prompt and answer format; parser rules; output comparison and verdict classes; time, memory and output
limits; repair feedback content; baselines; statistics (exclusion of `INFRA_ERROR`, Wilson intervals,
exact McNemar, the seven pre-registered comparisons); tasks, hidden cases, recorded answers, results.

## Verification of the final state (fresh clone, no model key in the environment)

| Check | Result |
|---|---|
| `make test` | 89/89 |
| `make resume-test` | pass (fails on the state before the fix) |
| `make validate` | 51/51 tasks valid |
| `make regress` | passed; feedback leak scan 0 |
| `make security` | passed |
| `make determinism` | 98 candidates, 841 case results, 0 differences |
| REPLAY 8B | 396/396 candidates identical to the recorded results (verdict, cases passed, status of every case) |
| REPLAY 70B | 396/396 identical except the reference-solution case of B3; all 236 model answers identical |
| `make compare` | every model row and all seven tests identical to `results/comparison.md` |
| secret scan | no key or key pattern in any file |

No material discrepancy affecting the reported frozen evaluation was found in the reviewed areas.
