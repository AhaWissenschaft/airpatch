Standard input contains time-clock records, one per line:

`<name> <in> <out>`

with both times as `HH:MM` on a 24-hour clock (`00:00` to `23:59`).

- If `<out>` is earlier than `<in>`, the shift went past midnight and ended on
  the next day: `22:00 06:00` is 8 hours.
- If `<out>` equals `<in>`, the record is a mistaken double punch and counts
  as 0 minutes.
- Unpaid breaks are deducted from every shift on its own: a shift of more
  than 6 hours loses 30 minutes, a shift of more than 9 hours loses 45
  minutes instead (not 30 + 45). A shift of exactly 6:00 loses nothing, a
  shift of exactly 9:00 loses 30 minutes.
- Names are case-sensitive (`Zoe` and `zoe` are different people). An
  employee can have any number of records.
- Empty lines are ignored.

Print one line per employee, `<name> <H:MM>`: the total paid time over all
their shifts, with the hours without leading zeros (they may exceed 24) and
the minutes as two digits. Sort the lines by name in plain character order
(upper-case letters before lower-case letters). An employee whose total is 0
is still listed (`Noah 0:00`). Empty input gives no output.
