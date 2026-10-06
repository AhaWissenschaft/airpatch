# Threat model

Assumption: answers from the model are untrusted. They may be wrong, may try
to game the tests by accident, or may contain harmful code. Judges run
`make run` on their own machines, so the pipeline must be safe to run there.

| Threat | Mitigation | Evidence |
|---|---|---|
| Candidate code reads hidden inputs, expected outputs or verifier code | candidate runs alone in a plain base image; only its own workspace (read-only) and one case input on stdin; expected outputs exist only in the verify container | `make security`: probe finds nothing; positive control with the data deliberately mounted finds every marker |
| Candidate code changes tests, harness or its own code between cases | workspace mounted read-only; tests and harness not mounted; fresh container per case | `make security` (write attempts fail; file hashes unchanged) |
| Answer writes outside the editable files (`../`, absolute paths) | path allow-list in `apply`; only the workspace is writable in that container | `make security` (traversal answer -> `POLICY_VIOLATION`), unit tests |
| Network access / exfiltration | `--network none` for every step except the LIVE propose step (Docker bridge: general egress, but it holds only public task files and harness code, never hidden data) | `make security` probe; config tests |
| Resource exhaustion (endless loop, memory, processes, huge output) | time limit with outer guard, memory limit, process limit, output size cap, 1 CPU | verdict unit tests (`TIMEOUT`, `RESOURCE_LIMIT`) |
| Hidden data leaking through repair-round feedback | feedback carries only counts for hidden cases and details for visible examples | unit test; `leakscan` over every feedback file in `make regress` |
| API key leaking | key only in the environment of the propose container (and, as a guard string, of the `make record` container), always passed by name, never on a command line; never logged or stored; `make record` refuses if the key string appears | sentinel-key test; unit and launcher tests; real-key scan after the live runs: 0 |
| Malicious model output in the report viewer | everything escaped; CSP `default-src 'none'`; no scripts | viewer unit test |
| Privilege escalation via Docker options | no `docker.sock`, no `--privileged`, no host network, `--cap-drop ALL`, `no-new-privileges` | config tests |
| Supply chain | base image pinned by digest; standard library only; no package installs | Dockerfile, `PROVENANCE.md` |
| Overclaiming | pre-registration; claims policy; intervals and paired tests | `ANALYSIS_PLAN.md`, `make compare` |

## Residual risks

- Container isolation depends on the host's Docker and kernel. A kernel or
  runtime vulnerability is outside what this project can control.
- Inside a candidate container the program could interfere with the
  `timeout` process; an outer guard on the host kills the container, and the
  verdict depends on the output comparison in the verifier anyway.
- Timeout and memory kill both exit with 137; they are told apart by run time
  and Docker's `OOMKilled` flag. A program that loops *and* allocates memory
  hits whichever limit comes first, which depends on machine speed; the
  determinism check therefore treats `TIMEOUT` and `RESOURCE_LIMIT` as one
  outcome and reports how often the two differed.
- Run times include container start-up (about 0.1-0.2 s per case). Under
  heavy host load a case can exceed its time limit by start-up delay alone:
  observed once in about 9,900 case executions (an oracle case, 70B run).
- Harness containers run as the invoking user (`--user $(id -u)`); started
  as root they run as root, still without capabilities and read-only.
  Candidate programs always run as uid 65534.
- The hidden cases are public in this repository (it is open source); they
  are hidden from the model during a run, not from the world.
