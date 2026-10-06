Count the vacation days people have used. Each non-empty line of
standard input is one of:

- `holiday <date>`: a public holiday.
- `allowance <name> <days>`: the person's vacation allowance, a non-negative
  integer. If there are several allowance lines for the same person, the last
  one in the input counts. A person without an allowance line has allowance 0.
- `leave <name> <from> <to>`: a leave request for every day from `<from>` to
  `<to>`, both included. A request whose `<from>` is after its `<to>` is
  ignored (but the person still counts as appearing in the input).

All dates are `YYYY-MM-DD`. The lines may come in any order; every holiday
applies to every request, no matter where in the input it appears.

A day of leave uses one vacation day if it is a Monday to Friday and not a
public holiday; Saturdays, Sundays and public holidays use nothing. The
requests of one person may overlap: each day is counted at most once per
person.

For every person named in an `allowance` or `leave` line, sorted by name in
plain character order (upper-case letters before lower-case letters), print
one line:

- `<name> used <u> left <l>` if `u` is at most the allowance, where `l` is
  the allowance minus `u` (so `left 0` when they are equal), or
- `<name> used <u> over <o>` if `u` is more than the allowance, where `o` is
  `u` minus the allowance.
