Compute library late fees. The first line of standard input is
`asof <date>`, the day of the report. Every following non-empty line is a
loan:

`<member> <type> <due date> <returned>`

where `<type>` is `book`, `dvd` or `magazine`, all dates are `YYYY-MM-DD`,
and `<returned>` is the return date, or `-` if the item has not come back
yet.

For each loan:

1. The library is closed on Sundays: if the due date is a Sunday, the item
   is due on the following Monday instead. (Other days are never moved.)
2. The number of days late is the number of days from the (possibly moved)
   due date to the return date, or to the `asof` date for an item that has
   not been returned. Zero or a negative number means not late.
3. Grace period: an item that is at most 3 days late costs nothing. An item
   that is more than 3 days late is charged for every late day (the grace
   days are not deducted: 4 days late means 4 charged days).
4. Daily rate: `book` 0.50, `dvd` 1.00, `magazine` 0.20.
5. The fee of a single loan is at most 10.00 (the limit applies to each loan
   on its own, not to a member's total).

Output one line per member, sorted by name in plain character order
(upper-case letters before lower-case letters): `<member> <total fee>`, the
sum of the fees of all their loans. Every member with at least one loan is
listed, with `0.00` if nothing is due. Finally print `total <sum of all
fees>`. Amounts have exactly two digits after the point.
