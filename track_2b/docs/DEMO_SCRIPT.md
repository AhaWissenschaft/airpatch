# Demo script (max. 2 minutes)

Recorded from a REPLAY of the recorded Apertus 70B run
(`data/cassettes/apertus-70b-20261005`, the default cassette), so the video is
reproducible and the screen says REPLAY. Numbers quoted below are the measured
ones (`results/comparison.md`); do not round them up.

Preparation:

```bash
cd track_2b
make clean
make run      # no key set: REPLAY of the 70B answers (about 15 min on 4 vCPUs; warm-up)
```

| time | on screen | voice-over (suggestion) |
|---|---|---|
| 0:00-0:12 | title slide: "AirPatch - check what a sovereign model writes, offline" | "Can a locally run Apertus fix real programs - and can we prove it without trusting the model?" |
| 0:12-0:35 | terminal: `make run` (REPLAY banner), propose, apply, per-case containers (speed up the recording) | "Apertus proposes a change. A separate pipeline runs it in containers with no network, against hidden tests it never sees." |
| 0:35-1:00 | viewer `index.html`, then `results/comparison.md`: tasks solved per condition, per-task matrix | "On 40 new tasks, Apertus 70B and 8B each solve 2 with one answer and 3 with any of three - between 1 and 20 percent with 95% confidence. Simple baselines solve none; the reference solves all." |
| 1:00-1:20 | viewer: task `ahvcheck`, C0 fails 2/12, feedback shows the failing visible example, r1 and r2 fail the same way | "The verifier tells the model which visible example fails and what it printed - no hidden data. Here, as in most cases, the model repeats its answer: repair rounds fixed nothing. We report that as measured." |
| 1:20-1:45 | terminal: `make security` (probe finds nothing; positive control finds every marker) | "We attack our own verifier: the candidate cannot read hidden tests, expected outputs or verifier code. The control shows the probe would notice." |
| 1:45-2:00 | `make bundle`, architecture slide, repo link | "Everything runs air-gapped: two images, standard library only, Apache-2.0." |

Do not show any API key, `.env` file, or shell history.
