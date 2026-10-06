# Pre-registered analysis plan (FROZEN 2026-10-05)

Status: **FROZEN on 2026-10-05**, before the first live run on the test
split. The commit that sets this status is the frozen-analysis commit quoted
in the technical report. Any later change is added as a dated change note
below, never by editing the frozen text.

## Question

Can Apertus (v1.5, 8B and 70B) turn a natural-language specification plus a
faulty program into a correct program, judged only by hidden test cases in an
offline, isolated verifier - and how much does verifier feedback help?

## Tasks

- Newly written black-box tasks (program reads standard input, writes
  standard output), Python. No task is taken from a public benchmark or from
  any other project.
- **dev split**: tasks used to build and debug the pipeline and prompts
  (listed in `data/tasks/*/task.json` with `"split": "dev"`). Not used for
  headline results.
- **test split**: 40 tasks (`"split": "test"`), added after the pipeline and
  prompt were built (commit `a93f08a`). No model has seen them before this
  freeze (the live smoke test used dev tasks only; MOCK answers exist only for
  dev tasks). Their list is fixed below.
- Every task passes `make validate` before any model sees it: the reference
  solution passes all hidden cases; the start code, a program that memorises
  the visible examples, and two near-miss variants are all rejected; at least
  8 hidden cases.

## Conditions

| id | description |
|---|---|
| C0 | one answer, temperature 0 |
| C1 | 3 independent answers, temperature 0.7; reported as "solved by any of 3" |
| C2 | C0 followed by up to 2 repair rounds; the model sees only the verdict class, how many hidden cases passed (with counts per failure reason), its own build error, and pass/fail plus its own output for the *visible* examples |
| B0 | start code unchanged |
| B1 | first-order mutation search on the start code, using the visible examples only |
| B2 | reference solution (validity check) |
| B3 | program that memorises the visible examples |

Models: Apertus v1.5 8B and Apertus v1.5 70B, through the endpoint provided
for the hackathon. The prompt is the one in `src/airpatch/propose.py` at the
frozen commit; maximum answer length 2048 tokens.

## Outcome and metrics

- Primary outcome per task and condition: **solved** = every hidden case
  passes (verdict `PASS`).
- Secondary: verdict classes, hidden cases passed, model calls, reported
  tokens, model latency, run time per case.
- `INFRA_ERROR` (endpoint failure, budget cap) is excluded from scoring and
  reported separately with its cause.

## Hypotheses

- **H1** (validity): B2 solves every task; B0 and B3 solve none.
- **H2** (determinism): re-checking the same answers gives identical verdicts.
- **H3** (isolation): `make security` passes; no repair-round feedback contains
  hidden data (`leakscan`).
- **H4** (need for a model, exploratory): Apertus 70B C0 solves more test
  tasks than B1.
- **H5** (feedback, exploratory): C2 solves at least as many tasks as C0.
- **H6** (size, exploratory): 70B solves at least as many tasks as 8B (C0).

## Analysis

- Tasks solved per condition with 95% Wilson intervals.
- Paired comparisons with the exact McNemar test (two-sided): 70B C0 vs B1;
  C1 vs C0; C2 vs C0 (each model); 8B vs 70B for C0 and C2.
- A difference is called "distinguishable" only at p < 0.05. With a few dozen
  tasks only large effects can be detected; smaller ones are reported as "not
  distinguishable", not as "no effect".
- No other comparisons are presented as confirmatory.

## Exclusions

- Before the first test-split run: tasks failing `make validate` are fixed or
  removed.
- After it: no task is removed. A task found to be faulty is marked as such
  and results are shown with and without it.

## Claims policy

The report claims only what the numbers above support. It makes no claim
about real-world repositories, about Apertus in general, or about costs
beyond the measured calls, tokens and times.

## Frozen settings (2026-10-05)

- Endpoint: CSCS inference API (`https://api.inference.cscs.ch/v1`), model ids
  `swiss-ai/Apertus-v1.5-70B` and `swiss-ai/Apertus-v1.5-8B` (`served_model`
  in each answer is recorded and checked).
- Per model one run: `AIRPATCH_SPLIT=test AIRPATCH_ALLOW_EXPERIMENT=yes
  AIRPATCH_MAX_CALLS=240 AIRPATCH_MAX_TOTAL_TOKENS=3000000
  AIRPATCH_MODEL_JOBS=4 make experiment` (C0 + C1 with 3 answers + C2 with up
  to 2 rounds; 40 x 6 = 240 calls at most; answer limit 2048 tokens). 70B
  first, then 8B with identical settings. Each run is recorded with
  `make record` and is never repeated to obtain a different result.
- Headline numbers and all tests come from `make compare
  RUNS="8b=<8B run> 70b=<70B run>"` at the frozen code.
- Confirmatory comparisons (exact McNemar, two-sided, no multiplicity
  correction, each read on its own at p < 0.05): 70B C0 vs B1; C1 vs C0 and
  C2 vs C0 for each model; 8B vs 70B for C0 and for C2 (seven tests).
  `make compare` also prints 8B C0 vs B1; it is descriptive only.
- INFRA_ERROR: a task whose answers in a condition hit INFRA_ERROR without
  any pass is not scored in that condition; paired tests use the tasks scored
  in both conditions; the number of unscored tasks is reported.
- Also reported, descriptive only: verdict classes, calls, reported tokens,
  latency per call, per-model and per-condition totals.
- Test tasks (40): age-groups, ahvcheck, allocate, anagram-groups, basecvt,
  calc, common-slots, csv-fields, deccalc, dedupe-ci, factorize, fracexpr,
  friendgroups, gcdlcm, headline-case, ini-query, invoice-vat, jobsched,
  late-fees, league, lrucache, mail-merge, maze, md-outline, numwords,
  parking-fees, postoffice, rappen, room-booking, shift-hours, stats,
  swiss-dates, table-align, template-vars, text-stats, toposort, trains,
  undoredo, vacation-days, weekly-overtime.
- Content identity at freeze (git tree hashes): `data/tasks`
  `39ad762b7d576c37d72871546f9a0840a189a2e9`, `data/hidden`
  `20f292b65617a0071e74cb5c841e99384d8d8733`; prompt file
  `src/airpatch/propose.py` blob `a373789b721a0c59ce6275a3d117aae668d1a709`;
  feedback file `src/airpatch/feedback.py` blob
  `56f77bcf825e3b274826a8d742586910eaa7a349`.

## Before the freeze (2026-10-05)

- Live smoke test, Apertus v1.5 70B, 3 dev tasks (brackets, csvsum, roman),
  C0 + 1 C1 answer + 1 repair round, 8 calls: authentication, model id,
  answer format, parser (8 of 8 answers parsed and applied), verifier, usage
  and latency recording all worked; no rate limit; the key appeared in no
  file. It showed one pipeline fault, fixed before this freeze (commit
  `a7bab1e`): visible examples were started with a wrong input path, so
  repair feedback showed INFRA_ERROR instead of the program's own output on
  the visible examples. Scored verdicts were not affected.
- `make compare` counted INFRA_ERROR as "not solved"; changed to the
  exclusion rule stated above (commit `a156a94`).
- `make validate` passed on all tasks at the frozen code.

## Change notes

- **2026-10-05, deviation (infrastructure, no change to the analysis).** The
  70B run `20261005T075518Z-19745` was interrupted by a restart of the cloud
  container after all 160 C0/C1 answers had been received and saved (0 call
  errors, ledger 160 calls / 183,750 tokens), while the hidden cases were
  being executed. Asking the model again would have drawn a second sample, so
  the launcher got `AIRPATCH_RESUME=<run id>` (commit after the freeze): the
  received answers and the call/token ledger are kept unchanged, every derived
  step (apply, execute, verify, feedback) is redone from scratch, and the
  repair rounds are then asked as planned under the same caps. Prompt, tasks,
  hidden cases, conditions, metrics and analysis are unchanged.
- **2026-10-06, post-evaluation hardening (no change to the analysis or the
  recorded results).** An independent audit found that `AIRPATCH_RESUME`
  treated a step as complete if any one task had its answer on disk, so tasks
  without an answer could be dropped after an interruption inside the step.
  Checked from the recorded artefacts: the 70B resume found all 160 C0/C1
  answers present (written at 07:58:54, interruption at 08:03:31), 8B was
  never resumed; both runs have every expected answer (40 x c0/s1/s2/s3,
  38 x r1, 38 x r2) and 0 INFRA_ERROR. The resume now keeps every answer on
  disk and asks exactly the missing ones. This changes `src/airpatch/propose.py`
  outside prompt construction (blob no longer `a373789`); the recorded prompt
  hashes of all 320 C0/C1 answers still match the current code (unit test).
