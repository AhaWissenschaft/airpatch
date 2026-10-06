A post office has `k` counters, numbered 1 to `k`, and one shared waiting
line. Simulate a day.

The first line of standard input is `k` (at least 1). Every following
non-empty line is a customer: `name arrival duration patience`, where `name`
is a word without spaces and the other values are integers (`arrival >= 0`,
`duration >= 1`, `patience >= 0`). Customers may be listed in any order. The
waiting line is ordered by arrival time; customers who arrive at the same time
keep the order in which they are listed in the input.

Customers are handled one after the other in waiting-line order. For each
customer:

- Service could start at the earliest time `s >= arrival` at which at least
  one counter is free. A counter that finishes serving someone at time `t` is
  free again at time `t`.
- If `s - arrival > patience`, the customer gives up and leaves; no counter
  is affected.
- Otherwise the customer is served from time `s` at the free counter with the
  smallest number, which is then busy until `s + duration`.

Print one line per customer in waiting-line order: `name counter start end`
for a served customer, `name left` for one who left. Finish with the line
`served <S> left <L> max wait <W>`, where `W` is the longest waiting time
`start - arrival` among the served customers (0 if nobody was served).
