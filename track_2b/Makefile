.PHONY: run validate regress determinism security test check experiment record compare bundle dataset expected doctor clean resume-test

# Optional local settings (never committed): LLM_NAME, LLM_BASE_URL, LLM_API_KEY.
-include .env
export LLM_NAME LLM_BASE_URL LLM_API_KEY

# Runs the benchmark tasks end to end in Docker.
# LIVE if LLM_NAME, LLM_BASE_URL and LLM_API_KEY are set, otherwise REPLAY of
# recorded answers if present, otherwise MOCK. The mode is printed and written
# into every result.
run:
	@./scripts/airpatch.sh run

# Task validation (no model): oracle must pass; start code, memorised examples
# and near-miss variants must fail. Also reports the mutation-search baseline.
validate:
	@./scripts/airpatch.sh validate

# Pipeline regression: MOCK answers and baselines must give the recorded verdicts.
regress:
	@./scripts/airpatch.sh regress

# Determinism: the same answers checked twice (second time sequentially) must agree.
determinism:
	@./scripts/airpatch.sh determinism

# Isolation test: a candidate tries to read hidden cases, expected outputs and
# verifier code, and to write or reach the network. Must fail; checked with a
# positive control.
security:
	@./scripts/airpatch.sh security

# Unit and integration tests of the harness (inside Docker, no network).
test:
	@./scripts/airpatch.sh test

check: test validate regress security

# Resume regression test: an interrupted LIVE run with a partial C0 step must ask exactly the
# missing answers and keep the others (no model is reachable: dummy endpoint, exhausted cap).
resume-test:
	@./scripts/test_resume_e2e.sh ..

# Full live measurement (all tasks, C0 + C1 + C2). Needs LLM_* settings,
# AIRPATCH_ALLOW_EXPERIMENT=yes and a hard cap AIRPATCH_MAX_CALLS.
experiment:
	@./scripts/airpatch.sh experiment

# Save a LIVE run's answers for REPLAY: make record RUN=runs/<id>-benchmark NAME=<name>
record:
	@./scripts/airpatch.sh record

# Compare runs with 95% intervals and paired tests: make compare RUNS="a=runs/<id> b=runs/<id>"
compare:
	@./scripts/airpatch.sh compare

# Air-gap transfer: save both images to runs/airpatch-images.tar (docker load on the target).
bundle:
	@./scripts/airpatch.sh bundle

# Optional HF dataset files: make dataset [RUN=runs/<id>-benchmark] -> runs/dataset/
dataset:
	@./scripts/airpatch.sh dataset

# Authoring tool: write missing expected outputs from the reference solutions.
expected:
	@./scripts/airpatch.sh expected

doctor:
	@./scripts/airpatch.sh doctor

clean:
	@./scripts/airpatch.sh clean
