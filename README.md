# AirPatch - Hack Apertus, Track 2B

Apertus proposes code changes for small, reproducible programming tasks. A
deterministic pipeline that does not depend on the model runs every proposal
in isolated, offline containers against hidden test cases and measures the
result: build, tests passed, run time, reproducible error fingerprints, model
calls and tokens, compared against baselines.

Result (40 new test tasks, one live run per model, analysis plan frozen
before the runs): Apertus v1.5 70B and 8B each solve 2/40 tasks with one
answer (95% CI 1-16%) and 3/40 with any of three; verifier feedback repaired
none; no pre-registered comparison is distinguishable. Details:
[`track_2b/results/comparison.md`](track_2b/results/comparison.md).

Team AhaWissenschaft AirPatch (William Kannenberg) · Hack Apertus Online
Hack, Track 2B (Own Project).

- Technical report (PDF): [`track_2b/AhaWissenschaft_AirPatch_Report.pdf`](track_2b/AhaWissenschaft_AirPatch_Report.pdf)
- Demo video (90 s): [`track_2b/demo/airpatch_demo.mp4`](track_2b/demo/airpatch_demo.mp4) (subtitles: [`airpatch_demo.srt`](track_2b/demo/airpatch_demo.srt))

The project lives in [`track_2b/`](track_2b/):

- [`track_2b/technical_report.md`](track_2b/technical_report.md) - the write-up
- [`track_2b/docs/REPRODUCE.md`](track_2b/docs/REPRODUCE.md) - how to run it (`cd track_2b && make run`)
- [`track_2b/docs/ARCHITECTURE.md`](track_2b/docs/ARCHITECTURE.md) and
  [`track_2b/docs/THREAT_MODEL.md`](track_2b/docs/THREAT_MODEL.md)
- [`track_2b/docs/ANALYSIS_PLAN.md`](track_2b/docs/ANALYSIS_PLAN.md) - the pre-registered analysis plan
- [`track_2b/docs/POST_EVALUATION_AUDIT.md`](track_2b/docs/POST_EVALUATION_AUDIT.md) - what was checked and changed after the evaluation
- [`track_2b/README.md`](track_2b/README.md) - the official challenge description

## Repository history

This public repository is a single snapshot of the final state. Commit
identifiers quoted in the report and the analysis plan (for example the frozen
analysis plan `0515deb` and the frozen evaluation `8bb67bc`) refer to the
project's development history, which is not part of this snapshot. The
recorded model answers (`track_2b/data/cassettes/`) and results
(`track_2b/results/`) are included unchanged, so every reported number can be
re-checked with `make run` (REPLAY) and `make compare`.

## License

All Hack Apertus projects are open-sourced. Please check the Terms & Conditions
(6. What you build is open source): https://hackapertus.ch/terms-and-conditions
- code Apache-2.0, documentation CC-BY-4.0, datasets CDLA-Permissive-2.0.
