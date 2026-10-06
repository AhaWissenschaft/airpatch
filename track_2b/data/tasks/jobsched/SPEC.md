A single machine runs jobs one at a time. Each non-empty line of standard
input describes one job: `name arrival duration priority`.

- `name` is a word without spaces; names are unique.
- `arrival` (0 or more), `duration` (at least 1) and `priority` (may be
  negative) are integers. The lines can be in any order.

The machine starts at time 0. Whenever it is free at time `t`, it chooses
among the jobs that have arrived (`arrival <= t`) and have not run yet the one
with the highest priority; ties are broken by earlier arrival, then by smaller
name (plain character order). It runs that job from `t` to `t + duration`
without interruption and is then free again. If no waiting job has arrived
yet, the machine stays idle until the next arrival.

Print one line `name start end` per job, in the order the jobs run. Then print
a final line `idle <total>` with the total time the machine was idle between
time 0 and the end of the last job. Empty input prints only `idle 0`.
