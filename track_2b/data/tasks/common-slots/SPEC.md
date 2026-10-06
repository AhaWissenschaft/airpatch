Find meeting slots that suit two people, `A` and `B`. The lines of
standard input may come in any order; empty lines are ignored.

- `days <first> <last>`: the dates to search, both included (`YYYY-MM-DD`).
  Exactly one such line.
- `hours <start> <end>`: the working hours, the same on every day. Exactly
  one such line.
- `duration <minutes>`: the minimum length of a slot, a positive integer.
  Exactly one such line.
- `buffer <minutes>`: optional, at most one such line, default 0. Every
  busy time is extended by this many minutes before its start and after its
  end (travel time). The working hours are not extended, and an extended
  busy time only affects its own date (it never reaches into the day before
  or after).
- `busy <who> <date> <start> <end>`: `<who>` (`A` or `B`) is busy on `<date>`
  from `<start>` to `<end>`. Busy times may overlap each other, may lie
  partly or completely outside the working hours, and may be on dates
  outside the search range (those are ignored).

All times are `HH:MM` with the start before the end; an end may be `24:00`
(the end of the day). A busy time never crosses midnight.

For every date from first to last that is a Monday to Friday (Saturdays and
Sundays are skipped and print nothing), the free slots are the maximal time
ranges within the working hours where neither A nor B is busy (after
applying the buffer). A busy time from 10:00 to 11:00 blocks exactly that
range: a slot may end at 10:00 or start at 11:00. Keep only the slots that
are at least `duration` minutes long (a slot of exactly `duration` minutes
is kept).

Output one line per searched weekday, in date order: the date followed by
each kept slot as ` HH:MM-HH:MM` (two-digit hours and minutes, `24:00` for
the end of the day), in time order, or the date followed by ` none` if no
slot is kept on that day.
