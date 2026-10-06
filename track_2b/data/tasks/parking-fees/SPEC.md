Compute parking fees. Each non-empty line of standard input is one
stay:

`<plate> <entry date> <entry time> <exit date> <exit time>`

with dates as `YYYY-MM-DD` and times as `HH:MM` (`00:00` to `23:59`). Stays
can last several days and cross month and year ends.

Tariff:

1. The duration is the number of minutes from entry to exit. A record whose
   exit is before its entry is invalid. Exit equal to entry is a valid stay
   of 0 minutes.
2. A stay of at most 30 minutes is free. A longer stay is charged in full,
   including its first 30 minutes.
3. The stay is cut into consecutive blocks of 60 minutes, starting at the
   entry time; a shorter last block counts as a full block. So 31 to 60
   minutes are 1 block, 61 minutes are 2 blocks, and exactly 120 minutes are
   2 blocks.
4. A block costs 2.50 if its start (clock time) is 08:00 or later and before
   20:00, otherwise 1.00. A block starting at 07:59 costs 1.00, one starting
   at 19:59 costs 2.50.
5. The blocks form periods of 24 consecutive blocks counted from the entry
   (blocks 1-24, blocks 25-48, ...; the last period may be shorter). The
   price of a period is the sum of its blocks, but at most 18.00.
6. The fee is the sum of the prices of all periods.

Output, for each record in input order, either `<plate> <duration> <fee>`
with the duration as `H:MM` (hours without leading zeros, minutes as two
digits), or `<plate> invalid`. Then print a line `---` (always, even if no
record was printed). Then, for every plate with at least one valid stay, a
line `<plate> <number of valid stays> <total fee>`, sorted by total fee from
highest to lowest; plates with equal totals are sorted by plate in plain
character order (upper-case letters and digits before lower-case letters).
Plates are case-sensitive. All amounts have exactly two digits after the
point.
