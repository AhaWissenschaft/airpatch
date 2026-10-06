Process meeting-room bookings in input order. Each non-empty line of
standard input is one command:

- `book <id> <room> <date> <start> <end>`: request room `<room>` on `<date>`
  (`YYYY-MM-DD`) from `<start>` to `<end>`. Times are `HH:MM`; a start is
  between `00:00` and `23:59`, an end between `00:00` and `24:00` (`24:00`
  is the end of the day).
- `cancel <id>`: cancel an earlier booking.

No two `book` commands use the same id. Room names are case-sensitive
(`Aare` and `aare` are different rooms).

For `book`, print exactly one line:

- `INVALID <id>` if the end is not after the start. Nothing else happens.
- Otherwise, if the requested time overlaps an *active* booking (accepted
  and not cancelled) of the same room on the same date, print
  `REJECT <id> <other>`, where `<other>` is the id of the overlapping active
  booking with the earliest start time. Two bookings overlap when they share
  at least one minute: a booking that ends at 10:00 and one that starts at
  10:00 do not overlap.
- Otherwise print `ACCEPT <id>`; the booking becomes active.

For `cancel <id>`, print `CANCELLED <id>` if `<id>` is an active booking (it
stops being active, so its time is free again), otherwise `UNKNOWN <id>`
(never booked, rejected, invalid, or already cancelled).

After all commands, print one summary line for every room that still has
at least one active booking, sorted by room name in plain character order
(upper-case letters before lower-case letters):

`<room> <number of active bookings> <total booked time>`

with the total booked time of those bookings as `H:MM` (hours without
leading zeros, minutes as two digits).
