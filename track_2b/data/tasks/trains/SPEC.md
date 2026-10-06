Plan train journeys. Standard input contains, ignoring empty lines:

1. a first line with the minimum change time `C` in minutes;
2. connection lines `train from to dep arr`: train `train` runs directly from
   station `from` to station `to`, departing at `dep` and arriving at `arr`;
3. query lines `? from to time`.

All connection lines come before the first query line, in no particular order.
Train and station names are words without spaces; a train usually has several
connections. Times are `HH:MM` on a single day (`00:00` to `23:59`) with
`dep < arr`; nothing runs past midnight.

For every query print the earliest time, as `HH:MM`, at which you can be at
station `to` if you are at station `from` at `time`, or `impossible` if you
cannot get there that day. If `from` equals `to`, the answer is `time`.

Rules for using connections:

- At the starting station you may take any connection that departs at or
  after `time`.
- When you arrive at a station with train `T` at time `t`, you may take a
  connection of the same train `T` that departs at or after `t` (staying on
  the train needs no change time), or a connection of any other train that
  departs at or after `t + C`.
- You may wait at a station as long as you like.
