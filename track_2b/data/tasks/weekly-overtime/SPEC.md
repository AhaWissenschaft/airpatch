Summarise a timesheet per employee and ISO calendar week. Each non-empty
line of standard input is either

- a shift: `<name> <date> <start> <end>`, with the date as `YYYY-MM-DD` and
  the times as `HH:MM` (`00:00` to `23:59`), or
- a weekly target: `target <name> <H:MM>`, the time the employee should work
  per week (for example `38:30`). Without a target line the target is
  `40:00`. If there are several target lines for the same employee, the last
  one in the input counts. The target applies to all weeks, including those
  of shifts listed before the target line. (No employee is called `target`.)

Shifts:

- If `<end>` is earlier than `<start>`, the shift ends on the next day
  (`22:00 06:00` is 8 hours). `<end>` is never equal to `<start>`.
- A shift belongs entirely to the week of its start date, even when it ends
  after midnight in the next week.
- Weeks are ISO weeks: they run from Monday to Sunday, and week 1 of a year
  is the week that contains the first Thursday of that year. A week belongs
  to the year of its Thursday: 2024-12-30 is in week 1 of 2025, and
  2027-01-01 is in week 53 of 2026.

For every employee who has at least one shift (sorted by name in plain
character order, upper-case before lower-case), print one line for each
week in which they have at least one shift, weeks in chronological order:

`<name> <YYYY>-W<ww> <worked> <difference>`

where `<YYYY>` is the ISO week's year, `<ww>` the two-digit week number,
`<worked>` the total time of the employee's shifts in that week, and
`<difference>` is worked time minus target with a sign, `+H:MM` or `-H:MM`
(`+0:00` when they are equal). After the week lines of an employee print

`<name> overtime <H:MM>`

the sum of the positive differences of that employee only (weeks below
target do not reduce it). All durations are `H:MM`: hours without leading
zeros, minutes as two digits. Employees with a target line but no shift are
not printed.
